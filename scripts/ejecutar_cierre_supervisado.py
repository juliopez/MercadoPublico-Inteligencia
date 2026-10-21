#!/usr/bin/env python3
"""Cierre MER v2 manual y supervisado, sin instalar cron.

Fases independientes y reanudables:
 diagnosticar: usar scripts/ubuntu_diagnostico_cierre.sh (separado).
 cargar: reconciliar, respaldar y escribir; requiere --confirmar-carga.
 trasladar: mover Drive mismo ID + actualizar catálogo GitHub; requiere
            --confirmar-traslado y evidencia de carga + revisión.
No invocar sobre archivos de producción antes del día 10 del mes siguiente.
"""
import argparse,datetime as dt,hashlib,json,os,sqlite3,subprocess,sys,urllib.error,urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from cargador_cierre_mer_v2 import ejecutar_carga_conciliada
from importador_historicos_v2 import SCHEMA

def git_token():
 token=os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
 if token:return token
 x=subprocess.run(["gh","auth","token"],capture_output=True,text=True,check=True)
 return x.stdout.strip()

def api(url,token,method="GET",payload=None,headers=None):
 hs={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","User-Agent":"MER-v2-cierre-supervisado"}
 if headers:hs.update(headers)
 data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode("utf8")
 if data is not None:hs["Content-Type"]="application/json"
 req=urllib.request.Request(url,data=data,headers=hs,method=method)
 try:
  with urllib.request.urlopen(req,timeout=100) as f:return json.loads(f.read())
 except urllib.error.HTTPError as e:
  raise RuntimeError(f"{method} API respondió HTTP {e.code}: {e.read(300).decode(errors='replace')}") from e

def drive_token():
 value=os.getenv("DRIVE_ACCESS_TOKEN")
 if value:return value
 # El token OAuth de usuario propietario es necesario si la cuenta de servicio
 # no puede trasladar hojas fuera de la carpeta.
 raise RuntimeError("Falta DRIVE_ACCESS_TOKEN del propietario con Drive scope.")

def guardar(path,record):
 path.parent.mkdir(parents=True,exist_ok=True)
 t=path.with_suffix(".tmp")
 t.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 os.replace(t,path)

def read_drive(id,token):
 return api("https://www.googleapis.com/drive/v3/files/"+id+"?fields=id,name,parents,mimeType&supportsAllDrives=true",token)

def mover_drive(id,old,new,name,token):
 return api("https://www.googleapis.com/drive/v3/files/"+id+
  "?addParents="+new+"&removeParents="+old+"&fields=id,name,parents&supportsAllDrives=true",token,
  "PATCH",{"name":name})

def revisar_drive(meta,id,nombre,carpeta):
 if meta.get("id")!=id or meta.get("name")!=nombre or carpeta not in meta.get("parents",[]):
  raise ValueError("Metadatos Drive incompatibles: ID, nombre o carpeta")

def github_catalog(token):
 url="https://api.github.com/repos/juliopez/MercadoPublico-Inteligencia/contents/config/catalogo_sheets.json"
 j=api(url,token);import base64
 return url,json.loads(base64.b64decode(j["content"])),j["sha"]

def update_catalog(token,url,sha,cat):
 import base64
 raw=json.dumps(cat,ensure_ascii=False,indent=2)+"\n"
 return api(url,token,"PUT",{"message":"chore: cerrar MER mensual conservando spreadsheet ID",
   "content":base64.b64encode(raw.encode("utf8")).decode(),"sha":sha,"branch":"main"})

def preflight(period,folder):
 hoy=dt.datetime.now(ZoneInfo("America/Santiago"))
 expected=(hoy.date().replace(day=1)-dt.timedelta(days=1)).strftime("%Y-%m")
 if hoy.day<10 or period!=expected:raise ValueError("Solo se cierra mes anterior desde día 10 en Santiago: "+expected)
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf8"))
 this=cat["periodos"][period]
 vigente=cat["periodos"].get(hoy.strftime("%Y-%m"),{})
 if this["tipo"]!="operativo" or not vigente or vigente.get("id")==this["id"]:
  raise ValueError("Catálogo operativo y destino de mes vigente incompatibles")
 status=json.loads((folder/"resumen_diagnostico_cierre.json").read_text(encoding="utf8"))
 if status.get("periodo")!=period or status.get("estado")!="DIAGNOSTICO_SIN_CONFLICTOS_PENDIENTE_CARGA":
  raise ValueError("El diagnóstico debe terminar sin conflictos antes de escribir")
 report=json.loads((folder/"preparados/informe.json").read_text(encoding="utf8"))
 if report.get("periodo")!=period or report.get("validacion_filas")!="OK":raise ValueError("Paquete histórico no validado")
 policy=json.loads((folder/"politica_conciliacion.json").read_text(encoding="utf8"))
 if policy.get("conflictos_totales")!=0:raise ValueError("Conciliación con conflictos")
 return cat,this,policy,report

def cargar(period,folder):
 cat,item,policy,report=preflight(period,folder)
 from google.oauth2.service_account import Credentials
 import gspread
 credential=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",str(Path.home()/".config/mercadopublico/servicio-google.json"))
 creds=Credentials.from_service_account_file(credential,scopes=["https://www.googleapis.com/auth/spreadsheets"])
 book=gspread.authorize(creds).open_by_key(item["id"])
 statefile=folder/"estado_carga_real.json"
 def registrar(event,payload):
  current=json.loads(statefile.read_text(encoding="utf8")) if statefile.exists() else {"periodo":period,"eventos":[]}
  current["eventos"].append({"evento":event,"fecha":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),"detalle":payload})
  guardar(statefile,current)
 with sqlite3.connect(f"file:{(folder/'preparados/preparado.sqlite').resolve()}?mode=ro",uri=True) as db:
  result=ejecutar_carga_conciliada(book,db,SCHEMA,period,policy,registrar,confirmacion="CIERRE_SUPERVISADO_AUTORIZADO")
 if result["estado"]!="CARGA_CONCILIADA_VERIFICADA_PENDIENTE_AUDITORIA":
  raise RuntimeError("Carga no finalizada")
 guardar(folder/"constancia_carga_real.json",{"periodo":period,"id":item["id"],
  "estado":"CARGA_VERIFICADA","backup":result["respaldo"],"datos":result["tablas"],
  "fecha":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),
  "traslado_autorizado":False})
 print("CARGA VERIFICADA; NO SE HA TRASLADADO EN DRIVE")

def trasladar(period,folder):
 cat,item,policy,report=preflight(period,folder)
 evidence=json.loads((folder/"constancia_carga_real.json").read_text(encoding="utf8"))
 if evidence.get("periodo")!=period or evidence.get("id")!=item["id"] or evidence.get("estado")!="CARGA_VERIFICADA":
  raise ValueError("Sin constancia de carga verificada")
 # Una aprobación supervisada del contenido ya cargado es necesaria, aparte de datos del script.
 acceptance=folder/"APROBACION_CIERRE.json"
 approval=json.loads(acceptance.read_text(encoding="utf8"))
 if approval.get("periodo")!=period or approval.get("spreadsheet_id")!=item["id"] or approval.get("aprobar_traslado") is not True:
  raise ValueError("No existe aprobación explícita de traslado")
 tok=drive_token();id=item["id"];before="MER_"+period.replace("-","_")+"_OPERATIVO";after="MER_"+period.replace("-","_")
 orig=cat["carpetas"]["operativo"];dst=cat["carpetas"]["historicos"]
 live=read_drive(id,tok)
 if live.get("name")==before and orig in live.get("parents",[]):
  revisar_drive(live,id,before,orig)
  mover_drive(id,orig,dst,after,tok)
  live=read_drive(id,tok)
 revisar_drive(live,id,after,dst)
 print("DRIVE CONFIRMADO: ID conservado",id,flush=True)
 # Estado idempotente: no repetir movimiento si el catálogo falló.
 gt=git_token();url,remote,sha=github_catalog(gt)
 remote_entry=remote["periodos"].get(period,{})
 if remote_entry.get("id")!=id:raise ValueError("ID remoto del catálogo no coincide")
 if remote_entry.get("tipo")=="operativo":
  remote_entry["tipo"]="historico"
  remote_entry["estado"]="auditado_con_observaciones"
  # Derivar conteos reales tras carga de la evidencia.
  remote_entry.pop("filas",None)
  remote["actualizado"]=dt.datetime.now(ZoneInfo("America/Santiago")).date().isoformat()
  update_catalog(gt,url,sha,remote)
 elif remote_entry.get("tipo")!="historico":
  raise ValueError("Tipo de catálogo inesperado")
 _,confirmed,_=github_catalog(gt)
 if confirmed["periodos"][period]["tipo"]!="historico" or confirmed["periodos"][period]["id"]!=id:
  raise ValueError("GitHub no confirmó el cambio")
 guardar(folder/"constancia_traslado.json",{"periodo":period,"id":id,"estado":"CERRADO_VERIFICADO",
 "fecha":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat()})
 print("CIERRE VERIFICADO Drive y GitHub",id)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--periodo",required=True)
 p.add_argument("--directorio",type=Path,default=Path.home()/".local/share/mercadopublico/cierres")
 phases=p.add_mutually_exclusive_group(required=True)
 phases.add_argument("--cargar",action="store_true")
 phases.add_argument("--trasladar",action="store_true")
 p.add_argument("--confirmar-carga",action="store_true")
 p.add_argument("--confirmar-traslado",action="store_true")
 a=p.parse_args();folder=a.directorio.expanduser().resolve()/a.periodo
 if a.cargar:
  if not a.confirmar_carga:raise SystemExit("Requiere --confirmar-carga")
  cargar(a.periodo,folder)
 else:
  if not a.confirmar_traslado:raise SystemExit("Requiere --confirmar-traslado")
  trasladar(a.periodo,folder)
if __name__=="__main__":main()
