#!/usr/bin/env python3
"""Detalle Compra Ágil V2: un código, checkpoint ControlV2, upsert Ofertas/Resultados."""
import argparse
import json
import os
import re
import sys
from datetime import datetime,timezone,timedelta
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import gspread
import v2_global_control as global_v2
from google.oauth2.service_account import Credentials
from v2_primera_escritura_sheets import CONTROL_HEAD,stamp,safe

O=["codigo","proveedor","monto_ofertado_clp","fecha_oferta","fuente","id_cotizacion","seleccionado"]
R=["codigo","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado","id_cotizacion_ganadora","monto_oferta_seleccionada_clp","estado_verificacion_oc"]
SOURCE="API Compra Ágil V2 - detalle"

def upsert_offers(ws,code,offers):
    existing=ws.get_all_values()
    if not existing or existing[0]!=O:raise RuntimeError("Esquema Ofertas diferente al validado")
    ix={}
    for n,row in enumerate(existing[1:],2):
        if len(row)>5 and row[0] and row[5]:
            key=(row[0],row[5])
            if key in ix:raise RuntimeError("Ofertas duplicadas: detener")
            ix[key]=(n,row)
    update=[];new=[]
    for offer in offers:
        key=(code,str(offer["id_cotizacion"]))
        data=[safe(code),safe(offer.get("razon_social")),safe(offer.get("monto_total")),
              safe(offer.get("fecha_creacion")),SOURCE,safe(key[1]),
              "1" if offer.get("proveedor_seleccionado") in (True,1,"1") else "0"]
        if key in ix:
            n,old=ix[key]
            merged=[v if v!="" else (old[j] if j<len(old) else "") for j,v in enumerate(data)]
            if merged!=old[:7]:update.append({"range":f"Ofertas!A{n}:G{n}","values":[merged]})
        else:new.append(data)
    return update,new

def plan_result(ws,code,selected,motive):
    existing=ws.get_all_values()
    if not existing or existing[0]!=R:raise RuntimeError("Esquema Resultados diferente al validado")
    if selected is None:return [],[]
    matching=[(n,row) for n,row in enumerate(existing[1:],2) if row and row[0]==code]
    sid=str(selected["id_cotizacion"])
    row=[code,"","","",safe(motive),SOURCE,"No: OC pública no verificada",sid,
         safe(selected.get("monto_total")),"Pendiente de verificar OC pública"]
    # Las columnas B-D contractuales no se infieren de la selección.
    if matching:
        same=[(n,old) for n,old in matching if len(old)>7 and old[7]==sid]
        if len(same)>1:raise RuntimeError("Selecciones duplicadas")
        if same:
            n,old=same[0]
            # Cualquier información verificada por otra fuente queda íntegra.
            if len(old)>6 and old[6].strip().lower().startswith(("si","sí")):return [],[]
            merged=[v if v!="" else (old[j] if j<len(old) else "") for j,v in enumerate(row)]
            for j in (1,2,3):merged[j]=old[j] if j<len(old) else ""
            return ([{"range":f"Resultados!A{n}:J{n}","values":[merged]}] if merged!=old[:10] else []),[]
        # No sobrescribir registros existentes de resultado, incluso si se seleccionó otro proveedor.
        if any(len(old)>6 and old[6].strip().lower().startswith(("si","sí")) for _,old in matching):return [],[]
    return [],[row]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--codigo",required=True)
    a=p.parse_args()
    code=a.codigo.strip()
    if code!="auto" and not re.fullmatch(r"[A-Za-z0-9]+-[A-Za-z0-9]+-COT[0-9]{2}",code):p.error("Código Compra Ágil inválido")
    cred=Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets"])
    book=gspread.authorize(cred).open_by_key(os.environ["GOOGLE_SHEET_ID"])
    control=book.worksheet("ControlV2")
    if control.row_values(1)!=CONTROL_HEAD:raise RuntimeError("ControlV2 incompatible")
    process=book.worksheet("Procesos").get_all_records()
    valid_codes={str(x.get("codigo","")).strip() for x in process if str(x.get("modalidad","")).strip().casefold() in ("compra ágil","compra agil")}
    if code=="auto":
        control_rows=control.get_all_values()[1:]
        checkpoints={row[0][len("detalle:"):]:row for row in control_rows
                     if row and row[0].startswith("detalle:")}
        candidates=[]
        for item in process:
            candidate=str(item.get("codigo","")).strip()
            if candidate not in valid_codes or not re.fullmatch(r"[A-Za-z0-9]+-[A-Za-z0-9]+-COT[0-9]{2}",candidate):
                continue
            # El listado informa la cantidad de ofertas, no asegura que el detalle las exponga.
            try: total=int(str(item.get("total_ofertas_recibidas") or "0").strip())
            except ValueError:total=0
            if total<=0:continue
            state=checkpoints.get(candidate,[])
            if len(state)>4 and state[4] in ("completo","revision"):continue
            if len(state)>6 and state[6] and state[6]>stamp():continue
            candidates.append((-total,candidate))
        if not candidates:
            print("DETALLE_SIN_CANDIDATOS_CON_OFERTAS: sin procesos elegibles según resumen; no HTTP");return
        code=sorted(candidates)[0][1]
        print("DETALLE_CODIGO_SELECCIONADO:",code)
    if code not in valid_codes:
        raise RuntimeError("Código no existe en Procesos como Compra Ágil, no consultar")
    ws_o=book.worksheet("Ofertas");ws_r=book.worksheet("Resultados")
    if ws_o.row_values(1)!=O or ws_r.row_values(1)!=R:
        raise RuntimeError("Esquema Ofertas o Resultados incompatible")
    key="detalle:"+code
    rows=control.get_all_values()
    found=[(n,row) for n,row in enumerate(rows[1:],2) if row and row[0]==key]
    if len(found)>1:raise RuntimeError("Checkpoints duplicados")
    prior=found[0][1] if found else []
    if len(prior)>4 and prior[4]=="completo":
        print("DETALLE_COMPLETO: ya finalizado, sin HTTP");return
    if len(prior)>6 and prior[6] and prior[6]>stamp():
        print("DETALLE_EN_ESPERA: aún no vence plazo");return
    attempts=int(prior[5]) if len(prior)>5 and prior[5] else 0
    def checkpoint(state,http="",count=0,due=""):
        record=[key,"compra_agil_detalle","",code,state,attempts+1,due,http,count,stamp()]
        if found:control.update(range_name=f"A{found[0][0]}:J{found[0][0]}",values=[record],value_input_option="RAW")
        else:control.append_row(record,value_input_option="RAW",table_range="A:J")
    req=Request("https://api2.mercadopublico.cl/v2/compra-agil/"+code,
        headers={"ticket":os.environ["CHILECOMPRA_TICKET"],"Accept":"application/json"})
    if not global_v2.reserve(control):
        print('DETALLE_NO_CONSULTA_CONTROL_GLOBAL');return
    try:
        with urlopen(req,timeout=45) as resp:
            raw=resp.read();http=resp.status
    except HTTPError as e:
        http=e.code;e.close()
        global_v2.finish(control,http)
        temporary=http in (429,500,502,503,504)
        sec=3600 if http==429 else min(3600,300*2**min(attempts,3))
        due=(datetime.now(timezone.utc)+timedelta(seconds=sec)).isoformat(timespec="seconds") if temporary else ""
        checkpoint("espera" if temporary else "revision",http,0,due)
        print(f"DETALLE_HTTP_{http}: registrado sin escrituras");return
    except (URLError,TimeoutError,OSError) as exc:
        global_v2.finish(control,None)
        due=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat(timespec="seconds")
        checkpoint("espera","red",0,due)
        print("DETALLE_ERROR_RED",type(exc).__name__);return
    global_v2.finish(control,200)
    data=json.loads(raw)
    payload=data.get("payload") if isinstance(data,dict) else None
    if data.get("success") not in (True,"OK") or data.get("errors") or not isinstance(payload,dict) or str(payload.get("codigo"))!=code:
        raise RuntimeError("Respuesta detalle inválida, no escribir")
    offers=payload.get("proveedores_cotizando")
    if not isinstance(offers,list) or not isinstance(payload.get("institucion"),dict) or not isinstance(payload.get("productos_solicitados"),list):
        raise RuntimeError("Detalle incompleto")
    ids=[str(x.get("id_cotizacion") or "") for x in offers if isinstance(x,dict)]
    if len(ids)!=len(offers) or not all(ids) or len(set(ids))!=len(ids):raise RuntimeError("Identificadores de oferta inválidos")
    winners=[x for x in offers if x.get("proveedor_seleccionado") in (True,1,"1")]
    if len(winners)>1:raise RuntimeError("Selección ambigua")
    ou,on=upsert_offers(ws_o,code,offers)
    ru,rn=plan_result(ws_r,code,winners[0] if winners else None,(payload.get("motivos") or {}).get("motivo_seleccion"))
    if ou:book.values_batch_update({"valueInputOption":"RAW","data":ou})
    if on:ws_o.append_rows(on,value_input_option="RAW")
    if ru:book.values_batch_update({"valueInputOption":"RAW","data":ru})
    if rn:ws_r.append_rows(rn,value_input_option="RAW")
    checkpoint("completo",200,len(offers))
    print(f"DETALLE_V2_SHEETS_OK: {code}, ofertas={len(offers)}, nuevas={len(on)}, actualizadas={len(ou)}, resultados_nuevos={len(rn)}")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("DETALLE_V2_ERROR:",type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(1)
