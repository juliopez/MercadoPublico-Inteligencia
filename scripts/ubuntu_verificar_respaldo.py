#!/usr/bin/env python3
"""Ensayo de respaldo local de las seis pestañas MER sin escribir en Google Sheets."""
import importlib.util,json,os
from pathlib import Path
from google.oauth2.service_account import Credentials
import gspread
BASE=Path(__file__).resolve().parents[1]
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 cat=json.loads((BASE/"config/catalogo_sheets.json").read_text(encoding="utf8"))
 import datetime
 from zoneinfo import ZoneInfo
 period=datetime.datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m")
 target=cat["periodos"].get(period)
 if not target or target["tipo"]!="operativo":raise RuntimeError("No está catalogado el mes operativo actual")
 secret=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS","")
 if not secret or not Path(secret).is_file():raise RuntimeError("Falta GOOGLE_APPLICATION_CREDENTIALS")
 creds=Credentials.from_service_account_file(secret,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
 book=gspread.authorize(creds).open_by_key(target["id"])
 etl=load(BASE/"scripts/etl_zip_dos_fuentes.py","etl_seguro")
 importer=load(BASE/"scripts/importador_historicos_v2.py","mer_schema")
 result=etl.respaldo_local(book,importer.SCHEMA,period)
 print("RESPALDO LOCAL CREADO Y VERIFICADO")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
