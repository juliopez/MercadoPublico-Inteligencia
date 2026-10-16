#!/usr/bin/env python3
"""Complemento diario de adjudicaciones oficiales para licitaciones.
La API V1 de detalle no garantiza ofertas individuales: nunca las fabrica.
Preserva montos/adjudicatarios existentes y solo incorpora datos oficiales presentes.
"""
import json, os, time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request
from zoneinfo import ZoneInfo
import gspread
from google.oauth2.service_account import Credentials
from api_retry import fetch_json

RH=["codigo","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado","id_cotizacion_ganadora","monto_oferta_seleccionada_clp","estado_verificacion_oc"]
API="https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
def as_text(x):
    return "" if x is None else str(x)
def main():
    date=os.environ["SYNC_FECHA_2026"]
    datetime.strptime(date,"%Y-%m-%d")
    creds=Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),scopes=["https://www.googleapis.com/auth/spreadsheets"])
    wb=gspread.authorize(creds).open_by_key(os.environ["GOOGLE_SHEET_ID"])
    ps=wb.worksheet("Procesos").get_all_records()
    ws=wb.worksheet("Resultados")
    before=ws.get_all_values()
    if not before or before[0]!=RH:raise RuntimeError("Cabecera Resultados incompatible")
    existing={}
    for i,row in enumerate(before[1:],2):
        if not row or not row[0]:continue
        if row[0] in existing:raise RuntimeError("Resultados duplicados: "+row[0])
        existing[row[0]]=(i,(row+[""]*len(RH))[:len(RH)])
    candidates=[p for p in ps if str(p.get("modalidad") or "").lower().startswith("licitaci") and
                (str(p.get("fecha_publicacion") or "")[:10]==date or
                 str(p.get("estado") or "").lower() in ("adjudicada","cerrada"))]
    # Estado cerrado puede transformarse después de la fecha de publicación:
    # los pendientes anteriores se revisan nuevamente en cada ejecución.
    seen=set(); updates=[]; inserts=[]; failures=[]
    for p in candidates:
        code=str(p.get("codigo") or "").strip()
        if not code or code in seen:continue
        seen.add(code)
        req=Request(API+"?"+urlencode({"codigo":code,"ticket":os.environ["CHILECOMPRA_TICKET"]}),headers={"Accept":"application/json"})
        try:
            data=fetch_json(req,timeout=50,label="Detalle licitación "+code)
            records=data.get("Listado") if isinstance(data,dict) else None
            if not isinstance(records,list):raise ValueError("Detalle sin listado")
            match=next((x for x in records if str(x.get("CodigoExterno") or "")==code),None)
            if not match:raise ValueError("Código no coincide")
            a=match.get("Adjudicacion") or {}
            if not isinstance(a,dict):a={}
            # Contrato/adjudicación deben estar expresamente informados.
            org=as_text(a.get("Nombre") or a.get("NombreProveedor") or "")
            amount=as_text(a.get("Monto") or "")
            awarded=bool(a.get("Tipo") or a.get("Numero") or a.get("Fecha") or org or amount)
            if not awarded:continue
            new=[code,org,amount,as_text(a.get("Fecha") or ""),"","API ChileCompra V1 - adjudicación","Adjudicación informada por API","","","OC no verificada"]
            if code in existing:
                i,old=existing[code]
                # No degradar datos históricos validados; solo completar vacíos.
                merged=[old[j] or new[j] for j in range(len(RH))]
                if merged!=old:updates.append({"range":f"Resultados!A{i}:J{i}","values":[merged]})
            else:
                inserts.append(new)
        except (ValueError,TypeError,KeyError,RuntimeError) as ex:
            failures.append(code+":"+type(ex).__name__)
        except Exception as ex:
            failures.append(code+":"+type(ex).__name__)
        time.sleep(float(os.getenv("LICITACION_DETAIL_DELAY","0.2")))
    for i in range(0,len(updates),100):
        wb.values_batch_update({"valueInputOption":"RAW","data":updates[i:i+100]})
    for i in range(0,len(inserts),500):
        ws.append_rows(inserts[i:i+500],value_input_option="RAW")
    print("DETALLE_LICITACIONES",json.dumps({"fecha":date,"consultadas":len(seen),"insertadas":len(inserts),"actualizadas":len(updates),"errores":len(failures)},ensure_ascii=False))
    if failures:
        print("PENDIENTES",json.dumps(failures[:50],ensure_ascii=False))
        raise SystemExit(2)
if __name__=="__main__":main()
