#!/usr/bin/env python3
"""Carga manual, idempotente, de diez procesos fijos de Compra Ágil."""
import json, os, sys, time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import gspread
from google.oauth2.service_account import Credentials

CODES = ["1057429-1660-COT26","5513-30-COT26","4177-147-COT26",
"557639-3133-COT26","3836-323-COT26","4079-338-COT26",
"2430-224-COT26","3836-322-COT26","615-42-COT26","2430-223-COT26"]
FIELDS=["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre",
"fecha_ultimo_cambio","monto_disponible_clp","organismo_comprador","rut_organismo",
"unidad_compra","region","total_ofertas_recibidas","motivo_seleccion","url_detalle"]
def get(d,k): return (d or {}).get(k)
def normalized(item):
    e=item.get("estado") or {};c=item.get("convocatoria") or {}; f=item.get("fechas") or {}
    m=item.get("montos") or {}; i=item.get("institucion") or {}
    r=item.get("resumen") or {}; mt=item.get("motivos") or {}; links=item.get("links") or {}
    seq=[item.get("codigo"),item.get("nombre"),get(e,"glosa"),get(c,"descripcion"),
    get(f,"fecha_publicacion"),get(f,"fecha_cierre"),get(f,"fecha_ultimo_cambio"),
    get(m,"monto_disponible_clp"),get(i,"organismo_comprador"),get(i,"rut"),
    get(i,"unidad_compra"),get(i,"nombre_region"),get(r,"total_ofertas_recibidas"),
    get(mt,"motivo_seleccion"),get(links,"detalle")]
    return ["" if v is None else str(v) for v in seq]
ticket=os.getenv("CHILECOMPRA_TICKET","")
raw=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","")
sheet_id=os.getenv("GOOGLE_SHEET_ID","")
if not all((ticket,raw,sheet_id)): sys.exit("Faltan credenciales")
credentials=Credentials.from_service_account_info(json.loads(raw),
    scopes=["https://www.googleapis.com/auth/spreadsheets"])
ws=gspread.authorize(credentials).open_by_key(sheet_id).worksheet("Procesos")
existing=ws.get_all_values()
if not existing or existing[0][:15]!=FIELDS: sys.exit("Cabeceras diferentes; abortado")
existing_map={}
for idx,row in enumerate(existing[1:],start=2):
    if row and row[0]:
        if row[0] in existing_map: sys.exit("Duplicado existente en hoja; abortado")
        existing_map[row[0]]=idx
remote=[]
for code in CODES:
    url="https://api2.mercadopublico.cl/v2/compra-agil?"+urlencode({"id":code})
    with urlopen(Request(url,headers={"ticket":ticket,"Accept":"application/json"}),timeout=45) as resp:
        data=json.load(resp)
    records=(data.get("payload") or {}).get("items") or []
    matching=[x for x in records if x.get("codigo")==code]
    if len(matching)!=1: sys.exit("Respuesta no unica para "+code)
    row=normalized(matching[0])
    if not row[0] or not row[1]:sys.exit("Datos mínimos faltantes "+code)
    remote.append(row)
    time.sleep(1)
# Conservar contenido existente: actualizar solo filas ya presentes, no borrar valores
# existentes cuando el campo de origen está vacío.
updates=[];new=[]
for values in remote:
    code=values[0]
    if code in existing_map:
        idx=existing_map[code]
        old=existing[idx-1]
        merged=[v if v!="" else (old[i] if i<len(old) else "") for i,v in enumerate(values)]
        if merged != [(old[i] if i<len(old) else "") for i in range(15)]:
            updates.append({"range":f"Procesos!A{idx}:O{idx}","values":[merged]})
    else:new.append(values)
print("PLAN inserciones",len(new),"actualizaciones",len(updates),flush=True)
if updates:
    ws.spreadsheet.values_batch_update({"valueInputOption":"RAW","data":updates})
if new:
    ws.append_rows(new,value_input_option="RAW",table_range="A:O")
after=ws.get_all_values()
codes=[r[0] for r in after[1:] if r and r[0]]
if len(codes)!=len(set(codes)) or not set(CODES).issubset(codes):
    sys.exit("ERROR_VERIFICACION: duplicados o códigos faltantes; revisar hoja")
print("WRITE_OK","nuevos",len(new),"actualizados",len(updates))
print("VERIFY_OK","total_codigos_unicos",len(codes),"lote_presente",len(CODES))
