#!/usr/bin/env python3
"""Exportación MER v2 de Sheets a SQLite local, lectura exclusivamente.

Se usa catálogo para identificar un único mes operativo; ninguna escritura en
Google. Exporta de forma atómica: si falla una tabla, no reemplaza instantánea.
"""
import argparse,datetime as dt,hashlib,importlib.util,json,os,sqlite3,tempfile
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
def schema():
 spec=importlib.util.spec_from_file_location("importador",ROOT/"scripts/importador_historicos_v2.py")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod.SCHEMA
def exportar(book,schemas,destino):
 destino=Path(destino);destino.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix=".mer_operativo_",suffix=".sqlite",dir=destino.parent)
 os.close(fd);temporal=Path(tmp)
 counts={};hashes={}
 try:
  con=sqlite3.connect(temporal)
  try:
   for tabla,cols in schemas.items():
    con.execute('CREATE TABLE "'+tabla+'" (pk TEXT PRIMARY KEY,fila TEXT NOT NULL)')
    ws=book.worksheet(tabla)
    datos=ws.get_all_values()
    if not datos or datos[0]!=cols:raise ValueError("Encabezados incompatibles: "+tabla)
    h=hashlib.sha256();num=0
    for i,row in enumerate(datos[1:],2):
     if not row or not row[0]:raise ValueError(f"PK vacía {tabla}:{i}")
     if len(row)>len(cols):raise ValueError(f"Columnas excedentes {tabla}:{i}")
     normalized=[str(v or "") for v in (row+[""]*len(cols))[:len(cols)]]
     pk=normalized[0]
     canonical=json.dumps(normalized,ensure_ascii=False,separators=(",",":"))
     try:con.execute('INSERT INTO "'+tabla+'" VALUES (?,?)',(pk,canonical))
     except sqlite3.IntegrityError as e:raise ValueError(f"PK duplicada {tabla}:{pk}") from e
     h.update((canonical+"\n").encode("utf8"));num+=1
    counts[tabla]=num;hashes[tabla]=h.hexdigest()
    con.commit()
   check=con.execute("PRAGMA integrity_check").fetchone()[0]
   if check!="ok":raise ValueError("SQLite integrity_check falló: "+check)
  finally:con.close()
  os.chmod(temporal,0o600)
  os.replace(temporal,destino)
  return {"tablas":counts,"huellas_orden_hoja":hashes,"sqlite":str(destino)}
 finally:
  if temporal.exists():temporal.unlink()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--periodo",required=True)
 p.add_argument("--salida",type=Path,required=True)
 a=p.parse_args()
 hoy=dt.datetime.now(ZoneInfo("America/Santiago"))
 anterior=(hoy.date().replace(day=1)-dt.timedelta(days=1)).strftime("%Y-%m")
 if hoy.day<10 or a.periodo!=anterior:p.error("Solo mes anterior desde día 10")
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf8"))
 entry=cat["periodos"].get(a.periodo)
 if not entry or entry.get("tipo")!="operativo" or not entry.get("id"):p.error("No hay hoja operativa autorizada")
 import gspread
 from google.oauth2.service_account import Credentials
 path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
 if not path or not Path(path).is_file():p.error("Falta credencial local")
 creds=Credentials.from_service_account_file(path,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
 book=gspread.authorize(creds).open_by_key(entry["id"])
 resultado=exportar(book,schema(),a.salida)
 report={"periodo":a.periodo,"spreadsheet_id":entry["id"],"fecha_chile":hoy.isoformat(),
  "estado":"SNAPSHOT_SOLO_LECTURA","resultado":resultado,"cierre_autorizado":False}
 reportpath=a.salida.with_suffix(".json")
 reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("INSTANTÁNEA OPERATIVA CREADA:",a.salida)
 print(json.dumps(resultado["tablas"],ensure_ascii=False))
if __name__=="__main__":main()
