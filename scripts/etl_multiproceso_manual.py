#!/usr/bin/env python3
"""ETL manual multiproceso: errores aislados y selección separada del contrato."""
import json, os, time, re
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import gspread
from api_retry import fetch_json
from google.oauth2.service_account import Credentials

# Solo se consultan procesos Compra Ágil existentes en Sheets; lote limitado.
# La selección publicada el mismo día normalmente no existe todavía.
MAX_CODES=max(1,min(100,int(os.getenv("DETAIL_MAX_CODES","10"))))
OFFSET=max(0,int(os.getenv("DETAIL_OFFSET","0")))
TARGET_DATE=os.getenv("DETAIL_FECHA","").strip()
if TARGET_DATE:
    datetime.strptime(TARGET_DATE,"%Y-%m-%d")
CODES=()
OHEAD=["codigo","convocatoria","rut_proveedor","proveedor","monto_ofertado_clp","moneda","fecha_oferta","estado_oferta","fuente","fecha_extraccion","id_cotizacion","valor_neto_clp","impuestos_clp","despacho_clp","seleccionado","id_oc_interno","estado_api"]
RHEAD=["codigo","convocatoria","rut_adjudicatario","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado","id_cotizacion_ganadora","monto_oferta_seleccionada_clp","id_oc_interno","estado_verificacion_oc","fecha_extraccion"]
ticket=os.environ["CHILECOMPRA_TICKET"]
creds=Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),scopes=["https://www.googleapis.com/auth/spreadsheets"])
book=gspread.authorize(creds).open_by_key(os.environ["GOOGLE_SHEET_ID"])
ws_p=book.worksheet("Procesos")
process_rows=ws_p.get_all_records()
candidates=[]
for p in process_rows:
    code=str(p.get("codigo") or "").strip()
    day=str(p.get("fecha_publicacion") or "")[:10]
    if re.search(r"-COT\d{2}$",code) and (not TARGET_DATE or day==TARGET_DATE):
        candidates.append(code)
CODES=tuple(dict.fromkeys(candidates))[OFFSET:OFFSET+MAX_CODES]
print("DETALLE_PLAN",len(CODES),"procesos seleccionados","fecha",TARGET_DATE or "sin filtro","limite",MAX_CODES,"desde_indice",OFFSET,flush=True)
ws_o=book.worksheet("Ofertas");ws_r=book.worksheet("Resultados")
orig_o=ws_o.get_all_values();orig_r=ws_r.get_all_values()
if orig_o[0][:17]!=OHEAD or orig_r[0][:14]!=RHEAD:
    raise SystemExit("ERROR_ESQUEMA: encabezados no coinciden; sin escrituras")
o_index={};r_index={}
for i,r in enumerate(orig_o[1:],start=2):
    if len(r)>10 and r[10]:
        if r[10] in o_index:raise SystemExit("DUPLICADOS_OFERTAS: sin escrituras")
        o_index[r[10]]=i
for i,r in enumerate(orig_r[1:],start=2):
    if r and r[0]:
        if r[0] in r_index:raise SystemExit("DUPLICADOS_RESULTADOS: sin escrituras")
        r_index[r[0]]=i
def v(x):return "" if x is None else str(x)
def offer_row(code,x,stamp):
    return list(map(v,[code,"",x.get("rut_proveedor"),x.get("razon_social"),x.get("monto_total"),"CLP",x.get("fecha_creacion"),x.get("estado"),"API Compra Ágil V2 - detalle",stamp,x.get("id_cotizacion"),x.get("valor_neto"),x.get("total_impuesto"),x.get("monto_despacho"),1 if x.get("proveedor_seleccionado") in (True,1,"1") else 0,x.get("id_oc"),x.get("estado")]))
def select_row(code,selected,motive,stamp):
    # La contratación pública no se infiere de la selección.
    return list(map(v,[code,"","","","","",motive,"API Compra Ágil V2 - detalle","No: OC pública no verificada",selected.get("id_cotizacion"),selected.get("monto_total"),selected.get("id_oc"),"Pendiente de verificar OC pública",stamp]))
success=[];failures={}
for n,code in enumerate(CODES):
    if n:time.sleep(3)
    try:
        request=Request("https://api2.mercadopublico.cl/v2/compra-agil/"+code,headers={"ticket":ticket,"Accept":"application/json"})
        data=fetch_json(request,timeout=40,label="Detalle "+code)
        payload=data.get("payload") or {}
        offers=payload.get("proveedores_cotizando")
        if payload.get("codigo")!=code or not isinstance(offers,list):
            raise ValueError("Respuesta incompleta")
        if not offers:
            print("SIN_OFERTAS_PUBLICAS",code,"sin escritura y sin adjudicación inferida",flush=True)
            continue
        ids=[str(o.get("id_cotizacion") or "") for o in offers]
        winners=[o for o in offers if o.get("proveedor_seleccionado") in (True,1,"1")]
        if not all(ids) or len(ids)!=len(set(ids)) or len(winners)>1:
            raise ValueError("IDs duplicados o seleccion ambigua")
        stamp=datetime.now(timezone.utc).isoformat()
        success.append((code,[offer_row(code,o,stamp) for o in offers],
                        select_row(code,winners[0],(payload.get("motivos") or {}).get("motivo_seleccion"),stamp) if winners else None))
        print("API_OK",code,"ofertas",len(offers),flush=True)
    except HTTPError as err:
        failures[code]="HTTP_"+str(err.code)
        print("::warning title=Proceso pendiente::"+code+": "+failures[code]+". Esperar unos minutos y volver a ejecutar manualmente.",flush=True)
    except (URLError,TimeoutError,ValueError,KeyError,TypeError) as err:
        failures[code]=type(err).__name__
        print("API_PENDIENTE",code,failures[code],flush=True)
# Conserva valores existentes donde la API entrega vacío.
def merge(new,old):
    return [n if n!="" else (old[i] if i<len(old) else "") for i,n in enumerate(new)]
o_updates=[];o_new=[];r_updates=[];r_new=[]
for code,offers,result in success:
    for row in offers:
        key=row[10]
        if key in o_index:
            idx=o_index[key];old=orig_o[idx-1];merged=merge(row,old)
            if merged!=merge([""]*17,old):
                o_updates.append({"range":f"Ofertas!A{idx}:Q{idx}","values":[merged]})
        else:o_new.append(row)
    if result is None:continue
    if code in r_index:
        idx=r_index[code];old=orig_r[idx-1]
        # No modificar nunca las columnas C:F (identidad/monto/fecha contractuales).
        for col in range(2,6):result[col]=old[col] if col<len(old) else ""
        merged=merge(result,old)
        if merged!=merge([""]*14,old):
            r_updates.append({"range":f"Resultados!A{idx}:N{idx}","values":[merged]})
    else:r_new.append(result)
print("PLAN","procesos_ok",len(success),"fallidos",len(failures),"ofertas_nuevas",len(o_new),"ofertas_actualizar",len(o_updates),"resultados_nuevos",len(r_new),flush=True)
# Procesos fallidos nunca entran en los lotes de escritura.
if o_updates:book.values_batch_update({"valueInputOption":"RAW","data":o_updates})
if o_new:ws_o.append_rows(o_new,value_input_option="RAW",table_range="A:Q")
if r_updates:book.values_batch_update({"valueInputOption":"RAW","data":r_updates})
if r_new:ws_r.append_rows(r_new,value_input_option="RAW",table_range="A:N")
after_o=ws_o.get_all_values();after_r=ws_r.get_all_values()
all_ids=[r[10] for r in after_o[1:] if len(r)>10 and r[10]]
all_codes=[r[0] for r in after_r[1:] if r and r[0]]
if len(all_ids)!=len(set(all_ids)) or len(all_codes)!=len(set(all_codes)):
    raise SystemExit("ERROR_VERIFICACION: duplicados detectados")
for code,offers,result in success:
    if not all(row[10] in all_ids for row in offers) or (result is not None and code not in all_codes):
        raise SystemExit("ERROR_VERIFICACION: lote incompleto")
# Registro histórico en Control!D:K, sin alterar metadatos existentes A:B.
audit=book.worksheet("Control")
audit_headers=["fecha_utc","codigo","http_resultado","estado_extraccion","ofertas_recuperadas","ofertas_insertadas","ofertas_actualizadas","observacion"]
current=audit.get("D1:K1")
if current and current[0] and current[0]!=audit_headers:
    raise SystemExit("ERROR_CONTROL: encabezados D:K no coinciden; revisar antes de escribir")
if not current or not current[0]:
    audit.update(range_name="D1:K1",values=[audit_headers],value_input_option="RAW")
stamp=datetime.now(timezone.utc).isoformat()
entries=[]
for code,offers,result in success:
    ids={row[10] for row in offers}
    inserted=sum(row[10] in ids for row in o_new)
    updated=sum(op["values"][0][10] in ids for op in o_updates)
    entries.append([stamp,code,"200","completo",len(offers),inserted,updated,"Selección informada; OC pública no verificada" if result is not None else "Ofertas recuperadas; sin proveedor seleccionado"])
for code,reason in failures.items():
    http=reason.split("_",1)[1] if reason.startswith("HTTP_") else ""
    entries.append([stamp,code,http,"pendiente",0,0,0,reason])
# Añadir filas D:K después del último registro de auditoría, preservando A:B.
prior=audit.get("D2:D")
start=2+len(prior)
audit.update(range_name=f"D{start}:K{start+len(entries)-1}",values=entries,value_input_option="RAW")
print("CONTROL_OK","registros_auditoria",len(entries),flush=True)
print("ETL_MULTIPROCESO_OK",json.dumps({"correctos":len(success),"pendientes":failures,"ofertas_totales":len(all_ids),"resultados_totales":len(all_codes)},ensure_ascii=False),flush=True)

if failures:
    print(f"::warning title=Extracción parcial::{len(failures)} procesos pendientes; vuelva a ejecutar manualmente más tarde. No se han sobrescrito datos de procesos fallidos.",flush=True)
    raise SystemExit(2)
