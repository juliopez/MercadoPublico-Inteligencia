#!/usr/bin/env python3
"""Carga manual idempotente de órdenes de compra publicadas en una fecha.
No infiere adjudicaciones ni vínculos con procesos ausentes en la fuente.
"""
import json, os, time
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from urllib.request import Request
from urllib.error import HTTPError, URLError
import gspread
from google.oauth2.service_account import Credentials
from api_retry import fetch_json, RateLimited

HEAD = ["codigo_oc","codigo_proceso","fecha_creacion","fecha_aceptacion","estado","proveedor","monto_total_oc_clp","tipo_oc","cantidad_lineas","total_lineas_neto"]
URL = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"

def val(obj, *keys):
    for key in keys:
        value = obj.get(key)
        if value is not None and value != "":
            return value
    return ""

def text(value):
    if value is None: return ""
    if isinstance(value, (dict,list)): return json.dumps(value, ensure_ascii=False)
    return str(value)

def main():
    date = os.environ["SYNC_FECHA_2026"]
    day = datetime.strptime(date, "%Y-%m-%d").date()
    if day > datetime.now(ZoneInfo("America/Santiago")).date():
        raise ValueError("No puede cargarse una fecha futura")
    ticket = os.environ["CHILECOMPRA_TICKET"]
    req = Request(URL+"?"+urlencode({"fecha":day.strftime("%d%m%Y"),"ticket":ticket}),
                  headers={"Accept":"application/json"})
    data = fetch_json(req,timeout=65,label="Órdenes de compra "+date)
    if not isinstance(data,dict) or not isinstance(data.get("Listado"),list):
        raise RuntimeError("Respuesta OC inválida; sin escrituras")
    records = data["Listado"]
    if data.get("Cantidad") is not None and int(data["Cantidad"]) != len(records):
        raise RuntimeError("Listado OC incompleto; sin escrituras")
    sa=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    cred=Credentials.from_service_account_info(sa,scopes=["https://www.googleapis.com/auth/spreadsheets"])
    book=gspread.authorize(cred).open_by_key(os.environ["GOOGLE_SHEET_ID"])
    audit=book.worksheet("Control")
    checkpoint_head=["tipo","fecha_consulta","codigo","estado"]
    checkpoint_header=audit.get("U1:X1")
    if checkpoint_header and not any(cell for row in checkpoint_header for cell in row):checkpoint_header=[]
    if checkpoint_header not in ([],[checkpoint_head]):raise RuntimeError("Control U:X incompatible")
    if not checkpoint_header:audit.update(range_name="U1:X1",values=[checkpoint_head])
    checkpoint_rows=audit.get("U2:X")
    done={row[2] for row in checkpoint_rows if len(row)>3 and row[0]=="ordenes_compra" and row[1]==date and row[3]=="completo"}
    checkpoint_next=2+len(checkpoint_rows)
    mapped={};rate_hit=False;temporary_error=None
    for item in records:
        if isinstance(item,dict) and str(item.get("Codigo") or "") in done:continue
        if not isinstance(item,dict): raise RuntimeError("OC sin objeto válido")
        # La lista diaria informa datos básicos; el código ofrece el detalle oficial.
        if not item.get("Proveedor") or item.get("Total") is None:
            detail_code=text(val(item,"Codigo","codigo")).strip()
            if not detail_code: raise RuntimeError("OC sin código en listado")
            detail_req=Request(URL+"?"+urlencode({"codigo":detail_code,"ticket":ticket}),headers={"Accept":"application/json"})
            try:
                detail=fetch_json(detail_req,timeout=65,label="Detalle OC "+detail_code)
            except RateLimited:
                rate_hit=True
                break
            except (HTTPError,URLError,TimeoutError) as ex:
                temporary_error=ex
                print("DETENIDO_ERROR_TRANSITORIO_OC",detail_code,type(ex).__name__,flush=True)
                break
            candidates=detail.get("Listado") if isinstance(detail,dict) else None
            if not isinstance(candidates,list):raise RuntimeError("Detalle OC sin listado: "+detail_code)
            selected=next((d for d in candidates if str(d.get("Codigo") or "")==detail_code),None)
            if not selected:raise RuntimeError("Código de OC no coincide: "+detail_code)
            item=selected
            time.sleep(float(os.getenv("OC_DETAIL_DELAY_SECONDS","0.2")))
        code = text(val(item,"Codigo","codigo")).strip()
        if not code or code in mapped: raise RuntimeError("Código OC ausente o repetido")
        fechas=item.get("Fechas") or {}
        items=item.get("Items") or {}
        prov = val(item,"Proveedor","proveedor")
        if isinstance(prov,dict): prov=val(prov,"Nombre","RazonSocial","nombre")
        row = [
            code,
            val(item,"CodigoLicitacion","codigo_licitacion","CodigoProceso"),
            val(fechas,"FechaCreacion") or val(item,"FechaCreacion","fecha_creacion"),
            val(fechas,"FechaAceptacion") or val(item,"FechaAceptacion","fecha_aceptacion"),
            val(item,"Estado","estado","CodigoEstado"),
            prov,
            val(item,"Total","MontoTotal","monto_total") if val(item,"TipoMoneda") in ("","CLP") else "",
            val(item,"Tipo","tipo","CodigoTipo"),
            val(items,"Cantidad") or val(item,"CantidadLineas","cantidad_lineas"),
            val(item,"TotalNeto","TotalLineasNeto","total_lineas_neto")
        ]
        mapped[code]=[text(v) for v in row]
    ws=book.worksheet("OrdenesCompra")
    existing=ws.get_all_values()
    if not existing or existing[0] != HEAD:
        raise RuntimeError("Cabeceras OrdenesCompra incompatibles; sin escrituras")
    ix={}
    for n,row in enumerate(existing[1:],start=2):
        if row and row[0]:
            if row[0] in ix: raise RuntimeError("OC duplicadas en la hoja; sin escrituras")
            ix[row[0]]=n
    updates=[]; inserts=[]
    for code,row in mapped.items():
        if code in ix:
            prev=existing[ix[code]-1]
            merged=[value or (prev[i] if i<len(prev) else "") for i,value in enumerate(row)]
            if merged != (prev+[""]*len(HEAD))[:len(HEAD)]:
                updates.append({"range":f"OrdenesCompra!A{ix[code]}:J{ix[code]}","values":[merged]})
        else:
            inserts.append(row)
    for i in range(0,len(updates),100):
        ws.spreadsheet.values_batch_update({"valueInputOption":"RAW","data":updates[i:i+100]})
    for i in range(0,len(inserts),500):
        ws.append_rows(inserts[i:i+500],value_input_option="RAW")
    codes=list(mapped)
    for start in range(0,len(codes),200):
        batch=codes[start:start+200]
        audit.update(range_name=f"U{checkpoint_next}:X{checkpoint_next+len(batch)-1}",values=[["ordenes_compra",date,code,"completo"] for code in batch])
        checkpoint_next+=len(batch)
    if rate_hit:
        print("DETENIDO_429_OC: lote parcial guardado; reanudar manualmente",flush=True)
        raise SystemExit(75)
    if temporary_error is not None:
        print("DETENIDO_ERROR_TRANSITORIO_OC: lote parcial guardado; reanudar manualmente",flush=True)
        raise SystemExit(74)
    print("ETL_OC_OK",json.dumps({"fecha":date,"recibidas":len(mapped),"nuevas":len(inserts),"actualizadas":len(updates)},ensure_ascii=False))

if __name__=="__main__": main()
