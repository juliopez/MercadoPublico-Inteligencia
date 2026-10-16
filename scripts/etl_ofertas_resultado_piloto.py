#!/usr/bin/env python3
"""Sincronización manual del piloto: ofertas por ID y selección, NO adjudicación contractual."""
import json, os, sys, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import gspread
from google.oauth2.service_account import Credentials

CODE="2284-520-COT26"
OF_HEADERS=["codigo","convocatoria","rut_proveedor","proveedor","monto_ofertado_clp","moneda","fecha_oferta","estado_oferta","fuente","fecha_extraccion","id_cotizacion","valor_neto_clp","impuestos_clp","despacho_clp","seleccionado","id_oc_interno","estado_api"]
RE_HEADERS=["codigo","convocatoria","rut_adjudicatario","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado"]
MORE=["id_cotizacion_ganadora","monto_oferta_seleccionada_clp","id_oc_interno","estado_verificacion_oc","fecha_extraccion"]
token=os.getenv("CHILECOMPRA_TICKET","")
raw=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","")
sid=os.getenv("GOOGLE_SHEET_ID","")
if not all((token,raw,sid)):sys.exit("CONFIG_ERROR: faltan credenciales")
creds=Credentials.from_service_account_info(json.loads(raw),scopes=["https://www.googleapis.com/auth/spreadsheets"])
book=gspread.authorize(creds).open_by_key(sid)
of=book.worksheet("Ofertas"); re=book.worksheet("Resultados")
oldof=of.get_all_values();oldre=re.get_all_values()
if oldof[0][:17]!=OF_HEADERS or oldre[0][:9]!=RE_HEADERS:sys.exit("SCHEMA_ERROR: encabezados inesperados")
keys=[r[10] for r in oldof[1:] if len(r)>10 and r[10]]
if len(keys)!=len(set(keys)):sys.exit("DATA_ERROR: IDs de cotización duplicados preexistentes")
resultkeys=[r[0] for r in oldre[1:] if r and r[0]]
if len(resultkeys)!=len(set(resultkeys)):sys.exit("DATA_ERROR: procesos duplicados en Resultados")
url="https://api2.mercadopublico.cl/v2/compra-agil/"+CODE
with urlopen(Request(url,headers={"ticket":token,"Accept":"application/json"}),timeout=55) as rsp:
    data=json.load(rsp)
p=data.get("payload") or {}
if p.get("codigo")!=CODE:sys.exit("API_ERROR: código no coincide")
offers=p.get("proveedores_cotizando") or []
if len(offers)!=3:sys.exit("API_ERROR: el piloto no contiene tres ofertas; abortado")
ids=[str(x.get("id_cotizacion") or "") for x in offers]
if not all(ids) or len(set(ids))!=3:sys.exit("API_ERROR: IDs invalidos o duplicados")
winners=[x for x in offers if x.get("proveedor_seleccionado") in (True,1,"1")]
if len(winners)!=1:sys.exit("API_ERROR: selección ambigua; abortado")
winner=winners[0];now=datetime.now(timezone.utc).isoformat()
def v(x):return "" if x is None else str(x)
def row(x):
    return list(map(v,[CODE, "",x.get("rut_proveedor"),x.get("razon_social"),x.get("monto_total"),
     "CLP",x.get("fecha_creacion"),x.get("estado"),"API Compra Ágil V2 - detalle",now,
     x.get("id_cotizacion"),x.get("valor_neto"),x.get("total_impuesto"),x.get("monto_despacho"),
     1 if x.get("proveedor_seleccionado") in (True,1,"1") else 0,x.get("id_oc"),x.get("estado")]))
incoming={str(x["id_cotizacion"]):row(x) for x in offers}
mapping={r[10]:i for i,r in enumerate(oldof[1:],start=2) if len(r)>10 and r[10]}
updates=[];appends=[]
for key,values in incoming.items():
    if key in mapping:
        idx=mapping[key];old=oldof[idx-1]
        merged=[val if val!="" else (old[k] if k<len(old) else "") for k,val in enumerate(values)]
        if merged!=[(old[k] if k<len(old) else "") for k in range(17)]:
            updates.append({"range":f"Ofertas!A{idx}:Q{idx}","values":[merged]})
    else:appends.append(values)
# Campos contractuales permanecen vacíos explícitamente.
motive=(p.get("motivos") or {}).get("motivo_seleccion")
selection=list(map(v,[CODE,"","","","",motive,"API Compra Ágil V2 - detalle","No: OC pública no verificada",
winner.get("id_cotizacion"),winner.get("monto_total"),winner.get("id_oc"),
"Pendiente de verificar OC pública",now]))
if len(oldre[0])<14:re.update(range_name="J1:N1",values=[MORE],value_input_option="RAW")
if CODE in resultkeys:
    idx=resultkeys.index(CODE)+2;old=oldre[idx-1]
    # Conserva columnas contractuales verificadas; no reemplazarlas con vacíos.
    selection=[val if val!="" else (old[k] if k<len(old) else "") for k,val in enumerate(selection)]
    re.update(range_name=f"A{idx}:N{idx}",values=[selection],value_input_option="RAW")
else:re.append_row(selection,value_input_option="RAW",table_range="A:N")
if updates:of.spreadsheet.values_batch_update({"valueInputOption":"RAW","data":updates})
if appends:of.append_rows(appends,value_input_option="RAW",table_range="A:Q")
check=of.get_all_values()
matches=[r[10] for r in check[1:] if len(r)>10 and r[0]==CODE]
if len(matches)!=3 or len(set(matches))!=3:sys.exit("VERIFY_ERROR: ofertas duplicadas o incompletas")
rc=re.get_all_values();out=[r for r in rc[1:] if r and r[0]==CODE]
if len(out)!=1:sys.exit("VERIFY_ERROR: resultado de selección duplicado")
print("ETL_OFERTAS_OK","nuevas",len(appends),"actualizadas",len(updates),"ofertas_unicas",3)
print("RESULTADO_SELECCION_OK","ganadores",len(winners),"OC_publica_verificada",False)
print("CONTRATO_NO_CONFIRMADO: monto_adjudicado_clp permanece sin inferencia")
