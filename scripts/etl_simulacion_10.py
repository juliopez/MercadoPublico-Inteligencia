#!/usr/bin/env python3
"""Simulación ETL ChileCompra -> Sheets: no escribe; máximo 10 procesos."""
import json, os, sys
from datetime import datetime,timezone,timedelta
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import gspread
from google.oauth2.service_account import Credentials

ticket=os.getenv("CHILECOMPRA_TICKET","").strip()
raw=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","").strip()
sid=os.getenv("GOOGLE_SHEET_ID","").strip()
if not all((ticket,raw,sid)): sys.exit("Faltan credenciales o ID de Sheets")
info=json.loads(raw)
creds=Credentials.from_service_account_info(info,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
sheet=gspread.authorize(creds).open_by_key(sid).worksheet("Procesos")
rows=sheet.get_all_values()
if not rows or rows[0][0]!="codigo":sys.exit("Esquema invalido")
existing={row[0]:row for row in rows[1:] if row}
now=datetime.now(timezone.utc)
params={"publicado_desde":(now-timedelta(days=7)).strftime("%Y-%m-%dT00:00:00"),
"publicado_hasta":now.strftime("%Y-%m-%dT23:59:59"),"q":"capacitacion","tamano_pagina":10,"numero_pagina":1}
url="https://api2.mercadopublico.cl/v2/compra-agil?"+urlencode(params)
with urlopen(Request(url,headers={"ticket":ticket,"Accept":"application/json"}),timeout=45) as response:
    body=json.load(response)
payload=body.get("payload") or {}
items=(payload.get("items") or [])[:10]
if not items: print("Sin procesos; no se realizan cambios");sys.exit(0)
ids=[item.get("codigo") for item in items]
if len(ids)!=len(set(ids)) or not all(ids):sys.exit("IDs duplicados o ausentes")
new=[code for code in ids if code not in existing]
updated=[code for code in ids if code in existing]
print("ETL_SIMULACION_OK")
print("procesos_consultados",len(items))
print("nuevos",len(new))
print("existentes_para_actualizar",len(updated))
print("escrituras_google_sheets",0)
print("codigos_consultados",json.dumps(ids))
