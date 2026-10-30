#!/usr/bin/env python3
"""Rotación operativa MER: después del ETL en último día hábil de Chile.
No concilia fuentes oficiales: ese procedimiento permanece diferido al día 10.
"""
import argparse,datetime as dt,json,os,pathlib,subprocess,sys,urllib.parse,urllib.request
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from importador_historicos_v2 import SCHEMA
TZ=ZoneInfo("America/Santiago")
FOLDER=pathlib.Path.home()/".local/share/mercadopublico/rotaciones"
def atomic(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix(".tmp")
 tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n")
 os.replace(tmp,path)
def api(url,token,method="GET",body=None):
 raw=None if body is None else json.dumps(body).encode()
 req=urllib.request.Request(url,data=raw,method=method,headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"})
 with urllib.request.urlopen(req,timeout=50) as r:return json.load(r)
def next_month(day):
 return (day.replace(day=28)+dt.timedelta(days=4)).replace(day=1)
def last_business(day,holidays):
 last=next_month(day)-dt.timedelta(days=1)
 while last.weekday()>=5 or last.isoformat() in holidays:last-=dt.timedelta(days=1)
 return last
def run(dry):
 import gspread
 from google.oauth2.service_account import Credentials
 from google.auth.transport.requests import Request
 now=dt.datetime.now(TZ);day=now.date();period=day.strftime("%Y-%m")
 hol=json.loads((ROOT/"config/feriados_chile_conciliacion.json").read_text())
 if str(day.year) not in hol["anios_verificados"]:raise SystemExit("BLOQUEO: validar feriados del año antes de rotar")
 last=last_business(day,set(hol["fechas"]))
 if day!=last:
  print("NO_CORRESPONDE_ROTACION",period,"ultimo_habil",last);return
 if not dry and now.hour<18:raise SystemExit("BLOQUEO: cierre solo después de las 18:00 Chile")
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
 current=cat["periodos"].get(period);nperiod=next_month(day).strftime("%Y-%m")
 following=cat["periodos"].get(nperiod)
 if not current or current.get("tipo")!="operativo" or not current.get("id"):raise SystemExit("BLOQUEO: mes actual no operativo")
 secret=os.getenv("GOOGLE_APPLICATION_CREDENTIALS",str(pathlib.Path.home()/".config/mercadopublico/servicio-google.json"))
 credentials=Credentials.from_service_account_file(secret,scopes=["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/spreadsheets"])
 drive=credentials.with_scopes(["https://www.googleapis.com/auth/drive"])
 drive.refresh(Request())
 token=drive.token
 def meta(id):return api("https://www.googleapis.com/drive/v3/files/"+id+"?fields=id,name,parents,mimeType,capabilities(canMoveItemWithinDrive,canEdit)&supportsAllDrives=true",token)
 g=gspread.authorize(credentials)
 def check(id,empty):
  b=g.open_by_key(id)
  for tab,cols in SCHEMA.items():
   s=b.worksheet(tab);values=s.get_all_values()
   if not values or values[0]!=cols:raise ValueError("SCHEMA incorrecto: "+tab)
   if empty and len(values)>1:raise ValueError("Destino nuevo contiene datos: "+tab)
  return b
 book=check(current["id"],False)
 old=meta(current["id"]);opf=cat["carpetas"]["operativo"];histf=cat["carpetas"]["historicos"]
 if old["id"]!=current["id"] or opf not in old.get("parents",[]):raise ValueError("Origen no está en carpeta operativa")
 if following:
  if following.get("tipo")!="operativo" or following["id"]==current["id"]:raise ValueError("Destino preexistente inválido")
  target=meta(following["id"])
  if opf not in target.get("parents",[]):raise ValueError("Destino fuera de carpeta operativa")
  if target.get("name")!="MER_"+nperiod.replace("-","_")+"_OPERATIVO":raise ValueError("Nombre destino inesperado")
  check(following["id"],True)
 elif dry:
  print("DESTINO_NO_CREADO: se creará una copia vacía de plantilla solo al aplicar")
 else:
  # Por seguridad se exige que el archivo del mes siguiente ya exista y esté verificado.
  # La creación automática de un Drive de tercero podría fallar por cuota/permisos.
  raise SystemExit("BLOQUEO: registrar/crear destino del mes siguiente antes del cierre")
 if dry:
  print("ROTACION_PREPARADA",period,"->",nperiod,"destino",following["id"] if following else "PENDIENTE");return
 # Exigir evidencia reciente del ETL de las 16:00 antes de archivar.
 status=json.loads((ROOT/"salida_operativa/estado_sincronizacion.json").read_text())["ultima_ejecucion"]
 stamp=dt.datetime.fromisoformat(status["ejecucion_chile"])
 if status["estado"]!="EXITOSA" or status["periodo"]!=period or stamp.date()!=day or stamp.hour<16:
  raise SystemExit("BLOQUEO: falta ETL validado del último día hábil")
 statefile=FOLDER/(period+".json")
 state=json.loads(statefile.read_text()) if statefile.exists() else {"periodo":period,"siguiente":nperiod,"id":current["id"]}
 if state.get("id")!=current["id"]:raise RuntimeError("Estado de rotación incompatible")
 state.update({"destino_id":following["id"],"verificado":now.isoformat()})
 atomic(statefile,state)
 newname="MER_"+period.replace("-","_")
 if opf in old.get("parents",[]):
  q=urllib.parse.urlencode({"addParents":histf,"removeParents":opf,"fields":"id,name,parents","supportsAllDrives":"true"})
  try:api("https://www.googleapis.com/drive/v3/files/"+current["id"]+"?"+q,token,"PATCH",{"name":newname})
  except Exception as e:raise SystemExit("BLOQUEO: no se pudo mover en Drive; revisar permisos de propietario: "+str(e))
 moved=meta(current["id"])
 if moved["name"]!=newname or histf not in moved.get("parents",[]):raise RuntimeError("Traslado no confirmado")
 state["traslado_drive"]="VERIFICADO";atomic(statefile,state)
 # Escribimos el catálogo por GitHub API con SHA, no alteramos el repositorio local ni sus locks.
 result=subprocess.run(["gh","api","repos/juliopez/MercadoPublico-Inteligencia/contents/config/catalogo_sheets.json"],capture_output=True,text=True,check=True)
 remote=json.loads(result.stdout);import base64
 obj=json.loads(base64.b64decode(remote["content"]))
 entry=obj["periodos"][period]
 if entry["id"]!=current["id"]:raise RuntimeError("Catálogo remoto ID distinto")
 if entry["tipo"]=="operativo":
  entry["tipo"]="historico"
  entry["estado"]="cierre_operativo_pendiente_conciliacion_oficial"
  obj["actualizado"]=day.isoformat()
  content=base64.b64encode((json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode()).decode()
  subprocess.run(["gh","api","--method","PUT","repos/juliopez/MercadoPublico-Inteligencia/contents/config/catalogo_sheets.json","-f","message=chore(mer): rotacion operativa "+period,"-f","sha="+remote["sha"],"-f","branch=main","-f","content="+content],check=True)
 state["catalogo"]="ACTUALIZADO";atomic(statefile,state)
 print("ROTACION_OPERATIVA_CONFIRMADA",period,"siguiente",nperiod)
def main():
 p=argparse.ArgumentParser();p.add_argument("--aplicar",action="store_true");args=p.parse_args()
 run(not args.aplicar)
if __name__=="__main__":main()
