#!/usr/bin/env python3
"""Conciliación MER v2 SOLO LECTURA: SQLite histórico preparado vs Google Sheets operativo.
No modifica hojas; genera reporte JSON, con claves completas solo como ejemplos acotados.
"""
import argparse,datetime as dt,importlib.util,json,os,sqlite3,collections,hashlib
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
TABLES=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")
def esquema():
 spec=importlib.util.spec_from_file_location("mer_hist",ROOT/"scripts/importador_historicos_v2.py")
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m.SCHEMA
def leer_destino(ws,cols):
 # Lectura completa necesaria para comparar claves y valores. Ninguna escritura.
 values=ws.get_all_values()
 if not values or values[0]!=cols:
  raise ValueError("Cabeceras incompatibles en "+ws.title)
 found={}
 for i,row in enumerate(values[1:],2):
  if not row or not row[0]:raise ValueError(f"Fila sin clave primaria en {ws.title}:{i}")
  if len(row)>len(cols):raise ValueError(f"Exceso de columnas en {ws.title}:{i}")
  key=row[0]
  if key in found:raise ValueError("Clave duplicada en "+ws.title+": "+key)
  found[key]=[str(x or "") for x in (row+[""]*len(cols))[:len(cols)]]
 return found
def huella_tabla(actual):
 h=hashlib.sha256()
 for pk in sorted(actual):
  h.update(json.dumps([pk,actual[pk]],ensure_ascii=False,separators=(',',':')).encode('utf-8'))
  h.update(b'\n')
 return h.hexdigest()
def comparar(db,table,actual,muestra=5):
 conteos=collections.Counter();ejemplos={k:[] for k in ("nuevos","modificados","sin_cambios","solo_operativo")}
 presentes=set()
 for key,raw in db.execute('SELECT pk,fila FROM "'+table+'"'):
  hist=[str(v or "") for v in json.loads(raw)]
  if hist[0]!=key:raise ValueError("PK distinta de fila: "+table)
  presentes.add(key)
  if key not in actual:kind="nuevos"
  elif actual[key]==hist:kind="sin_cambios"
  else:kind="modificados"
  conteos[kind]+=1
  if len(ejemplos[kind])<muestra:ejemplos[kind].append(key)
 for key in actual:
  if key not in presentes:
   conteos["solo_operativo"]+=1
   if len(ejemplos["solo_operativo"])<muestra:ejemplos["solo_operativo"].append(key)
 return {**{k:conteos[k] for k in ejemplos},"ejemplos_pk":ejemplos,
         "filas_historico":len(presentes),"filas_operativo":len(actual),
         "sha256_operativo":huella_tabla(actual)}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--periodo",required=True,help="AAAA-MM")
 p.add_argument("--paquete",required=True,type=Path,help="Carpeta con preparado.sqlite e informe.json")
 p.add_argument("--salida",type=Path,help="Ruta del reporte JSON")
 args=p.parse_args()
 now=dt.datetime.now(ZoneInfo("America/Santiago"))
 first=now.date().replace(day=1)
 anterior=(first-dt.timedelta(days=1)).strftime("%Y-%m")
 if args.periodo!=anterior:p.error("Solo conciliación del mes anterior: "+anterior)
 if now.day<10:p.error("Conciliación de cierre habilitada desde el día 10")
 catalogo=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf-8"))
 item=catalogo["periodos"].get(args.periodo)
 if not item or item.get("tipo")!="operativo":p.error("Período no catalogado como operativo")
 dbpath=args.paquete/"preparado.sqlite";reportpath=args.paquete/"informe.json"
 if not dbpath.is_file() or not reportpath.is_file():p.error("Faltan paquete preparado o informe")
 report=json.loads(reportpath.read_text(encoding="utf-8"))
 if report.get("periodo")!=args.periodo or report.get("validacion_filas")!="OK":
  p.error("Paquete no validado para el período")
 try:
  import gspread
  from google.oauth2.service_account import Credentials
 except ImportError as e:raise SystemExit("Instalar gspread y google-auth: "+str(e))
 credential=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
 if not credential:p.error("Definir GOOGLE_APPLICATION_CREDENTIALS en Ubuntu")
 creds=Credentials.from_service_account_file(credential,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
 book=gspread.authorize(creds).open_by_key(item["id"])
 schemas=esquema();db=sqlite3.connect(f"file:{dbpath.resolve()}?mode=ro",uri=True)
 try:
  tablas={}
  for table in TABLES:
   ws=book.worksheet(table)
   actual=leer_destino(ws,schemas[table])
   tablas[table]=comparar(db,table,actual)
   if tablas[table]["filas_historico"]!=report[table]:
    raise ValueError("Conteo histórico no coincide en "+table)
  resultado={"periodo":args.periodo,"fecha_chile":now.isoformat(),"spreadsheet_id":item["id"],
             "estado":"CONCILIACION_INFORMATIVA_REQUIERE_REVISION",
             "tablas":tablas,"observaciones_paquete":{k:v for k,v in report.items() if k.endswith("_sin_proceso") or k=="selecciones_ambiguas"},
             "escrituras_google_sheets":False,"traslado_drive":False,
             "advertencia":"Solo clasifica diferencias; no decide sobre pérdida de registros operativos ni adjudicaciones."}
  salida=args.salida or args.paquete.parent/"conciliacion.json"
  salida.parent.mkdir(parents=True,exist_ok=True)
  salida.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  print(json.dumps(resultado,ensure_ascii=False,indent=2))
  print("INFORME",salida)
 finally:db.close()
if __name__=="__main__":main()
