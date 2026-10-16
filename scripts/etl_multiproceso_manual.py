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
# Las extensiones del esquema son opcionales y deben estar después del contrato base.
OEXTRA=("url_documento_oferta","nivel_visibilidad","fecha_actualizacion_fuente")
REXTRA=("tipo_resultado","fuente_adjudicacion","codigo_oc_publica","url_documento_publico","id_linea_adjudicacion","clave_resultado")
def validate_extensions(headers,base,extras):
    tail=headers[len(base):]
    if any(name in headers[:len(base)] for name in extras):
        raise SystemExit("ERROR_ESQUEMA: columnas extendidas dentro del bloque base")
    if any(name in tail for name in extras):
        expected=[name for name in extras if name in tail]
        actual=[name for name in tail if name in extras]
        if expected!=actual:raise SystemExit("ERROR_ESQUEMA: orden de columnas extendidas")
    return headers
o_headers=validate_extensions(orig_o[0],OHEAD,OEXTRA)
r_headers=validate_extensions(orig_r[0],RHEAD,REXTRA)
def extend(base,headers,extras,values):
    # Nunca emitir datos más allá de las columnas conocidas ni inventar documentos públicos.
    result=base+[""]*max(0,len(headers)-len(base))
    for key,val in values.items():
        if key in extras and key in headers:result[headers.index(key)]=val
    return result
o_index={};r_index={}
# Clave compuesta: el identificador de oferta puede repetirse en procesos distintos.
for i,r in enumerate(orig_o[1:],start=2):
    if len(r)>10 and r[0] and r[10]:
        key=(r[0],r[10])
        if key in o_index:raise SystemExit("DUPLICADOS_OFERTAS: sin escrituras")
        o_index[key]=i
for i,r in enumerate(orig_r[1:],start=2):
    if r and r[0]:
        key_pos=r_headers.index("clave_resultado") if "clave_resultado" in r_headers else -1
        key=(r[0],r[key_pos]) if key_pos>=0 and len(r)>key_pos and r[key_pos] else (r[0],"seleccion:"+r[9] if len(r)>9 and r[9] else "legacy")
        if key in r_index:raise SystemExit("DUPLICADOS_RESULTADOS: sin escrituras")
        r_index[key]=i
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
        key=(row[0],row[10])
        if key in o_index:
            idx=o_index[key];old=orig_o[idx-1];merged=merge(row,old)
            # Las columnas opcionales no se sobrescriben al actualizar datos base.
            if merged!=old[:17]:
                o_updates.append({"range":f"Ofertas!A{idx}:Q{idx}","values":[merged]})
        else:o_new.append(extend(row,o_headers,OEXTRA,{"nivel_visibilidad":"no disponible"}))
    if result is None:continue
    result_key=(code,"seleccion:"+str(result[9]))
    fallback=(code,"legacy")
    existing_key=result_key if result_key in r_index else fallback if fallback in r_index else None
    if existing_key is not None:
        idx=r_index[existing_key];old=orig_r[idx-1]
        # No modificar nunca las columnas C:F (identidad/monto/fecha contractuales).
        for col in range(2,6):result[col]=old[col] if col<len(old) else ""
        # Nunca degradar una adjudicación previamente validada a selección no verificada.
        prior_type=old[r_headers.index("tipo_resultado")] if "tipo_resultado" in r_headers and len(old)>r_headers.index("tipo_resultado") else ""
        verified=bool((len(old)>8 and old[8].strip().lower().startswith(("si","sí"))) or
                      prior_type in ("adjudicacion_informada","contrato_verificado"))
        if verified:
            for col in (8,12):
                result[col]=old[col] if len(old)>col else ""
            # No reemplazar los datos de selección con información que pueda contradecir el registro verificado.
            for col in (9,10,11):
                result[col]=old[col] if len(old)>col else ""
        merged=merge(result,old)
        if merged!=old[:14]:
            r_updates.append({"range":f"Resultados!A{idx}:N{idx}","values":[merged]})
        # Clasificar registros antiguos solo cuando no exista otra clasificación.
        if "clave_resultado" in r_headers:
            key_col=r_headers.index("clave_resultado")
            if len(old)<=key_col or not old[key_col]:
                colname=chr(65+key_col) if key_col<26 else None
                if not colname:raise SystemExit("ERROR_ESQUEMA: índice de clave fuera de rango")
                r_updates.append({"range":f"Resultados!{colname}{idx}","values":[[result_key[1]]]})
        if "tipo_resultado" in r_headers and not prior_type and not verified:
            col=r_headers.index("tipo_resultado")
            # Posición O corresponde a la primera columna ampliada.
            r_updates.append({"range":f"Resultados!{chr(65+col)}{idx}","values":[["oferta_seleccionada"]]})
    else:r_new.append(extend(result,r_headers,REXTRA,{"tipo_resultado":"oferta_seleccionada","clave_resultado":result_key[1]}))
print("PLAN","procesos_ok",len(success),"fallidos",len(failures),"ofertas_nuevas",len(o_new),"ofertas_actualizar",len(o_updates),"resultados_nuevos",len(r_new),flush=True)
# Procesos fallidos nunca entran en los lotes de escritura.
if o_updates:book.values_batch_update({"valueInputOption":"RAW","data":o_updates})
if o_new:ws_o.append_rows(o_new,value_input_option="RAW")
if r_updates:book.values_batch_update({"valueInputOption":"RAW","data":r_updates})
if r_new:ws_r.append_rows(r_new,value_input_option="RAW")
after_o=ws_o.get_all_values();after_r=ws_r.get_all_values()
all_ids=[(r[0],r[10]) for r in after_o[1:] if len(r)>10 and r[0] and r[10]]
all_codes=[(r[0],r[r_headers.index("clave_resultado")] if "clave_resultado" in r_headers and len(r)>r_headers.index("clave_resultado") and r[r_headers.index("clave_resultado")] else ("seleccion:"+r[9] if len(r)>9 and r[9] else "legacy")) for r in after_r[1:] if r and r[0]]
if len(all_ids)!=len(set(all_ids)) or len(all_codes)!=len(set(all_codes)):
    raise SystemExit("ERROR_VERIFICACION: duplicados detectados")
for code,offers,result in success:
    if not all((row[0],row[10]) in all_ids for row in offers) or (result is not None and (code,"seleccion:"+str(result[9])) not in all_codes):
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
    ids={(row[0],row[10]) for row in offers}
    inserted=sum((row[0],row[10]) in ids for row in o_new)
    updated=sum((op["values"][0][0],op["values"][0][10]) in ids for op in o_updates)
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
