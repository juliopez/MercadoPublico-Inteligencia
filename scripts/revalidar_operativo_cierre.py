#!/usr/bin/env python3
"""Revalidación del operativo MER antes de un cierre. SOLO LECTURA.

Compara hash de todas las PK y todos los campos de cada tabla con la conciliación
original. Los recuentos por sí solos NO prueban que la hoja siga idéntica.
"""
import argparse,datetime as dt,hashlib,importlib.util,json,os,sys
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
def cargar():
 spec=importlib.util.spec_from_file_location("conciliador",ROOT/"scripts/conciliar_cierre_mensual.py")
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def cotejar(conciliacion, actual, huella):
 if not isinstance(huella,str) or len(huella)!=64:
  raise ValueError("Conciliación previa sin huella SHA256 de contenido: repetir conciliación")
 if actual!=huella:raise ValueError("La hoja cambió desde la conciliación; repetir conciliación y aprobación")
 return True
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--conciliacion",type=Path,required=True)
 p.add_argument("--salida",type=Path)
 a=p.parse_args()
 c=json.loads(a.conciliacion.read_text(encoding="utf8"))
 mes=c.get("periodo")
 now=dt.datetime.now(ZoneInfo("America/Santiago"))
 first=now.date().replace(day=1)
 previo=(first-dt.timedelta(days=1)).strftime("%Y-%m")
 if mes!=previo or now.day<10:p.error("Solo mes inmediatamente anterior y a partir del día 10")
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf8"))
 dest=cat["periodos"].get(mes)
 if not dest or dest.get("tipo")!="operativo" or dest["id"]!=c.get("spreadsheet_id"):
  p.error("Destino no coincide con el catálogo o dejó de ser operativo")
 mod=cargar()
 for tab in mod.TABLES:
  if tab not in c.get("tablas",{}) or not c["tablas"][tab].get("sha256_operativo"):
   p.error("Informe antiguo sin hash para "+tab+": generar nueva conciliación")
 try:
  import gspread
  from google.oauth2.service_account import Credentials
 except ImportError as e:raise RuntimeError("Falta gspread/google-auth") from e
 cred=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
 if not cred:p.error("Definir GOOGLE_APPLICATION_CREDENTIALS")
 token=Credentials.from_service_account_file(cred,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
 book=gspread.authorize(token).open_by_key(dest["id"])
 schema=mod.esquema()
 checked={}
 for tab in mod.TABLES:
  current=mod.leer_destino(book.worksheet(tab),schema[tab])
  nuevo=mod.huella_tabla(current)
  antiguo=c["tablas"][tab]["sha256_operativo"]
  cotejar(c,nuevo,antiguo)
  if len(current)!=c["tablas"][tab]["filas_operativo"]:
   raise ValueError("Conteo del destino cambió en "+tab)
  checked[tab]={"filas":len(current),"sha256":nuevo}
 resultado={"periodo":mes,"spreadsheet_id":dest["id"],"fecha_chile":now.isoformat(),
   "estado":"OPERATIVO_SIN_CAMBIOS_DESDE_CONCILIACION",
   "tablas":checked,"escrituras_google":False,"traslado_drive":False,
   "advertencia":"Una comprobación solo lectura no garantiza exclusión mutua futura. Requiere bloqueo de escritor y revalidación antes de aplicar."}
 salida=a.salida or a.conciliacion.parent/"revalidacion_operativo.json"
 salida.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("REVALIDADO SOLO LECTURA:",salida)
if __name__=="__main__":main()
