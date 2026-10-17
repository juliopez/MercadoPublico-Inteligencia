#!/usr/bin/env python3
"""Primera escritura V2 en GitHub: una página (10 registros), upsert por código."""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import gspread
import v2_global_control as global_v2
from google.oauth2.service_account import Credentials

BASE="https://api2.mercadopublico.cl/v2/compra-agil"
CONTROL_HEAD=["clave","tipo","fecha","pagina","estado","intentos","proximo_intento_utc","http","registros","actualizado_utc"]
def stamp(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def safe(x):
    if x is None:return ""
    if isinstance(x,(dict,list)):x=json.dumps(x,ensure_ascii=False)
    s=str(x)
    return "'"+s if s.startswith(("=","+","-","@")) and not s.lstrip("-").replace(".","",1).isdigit() else s
def value(x,k):return (x or {}).get(k) or ""
def transform(item):
    e=item.get("estado") or {};c=item.get("convocatoria") or {};f=item.get("fechas") or {}
    m=item.get("montos") or {};i=item.get("institucion") or {};r=item.get("resumen") or {}
    mot=item.get("motivos") or {};link=item.get("links") or {}
    d={"codigo":item["codigo"],"nombre":item.get("nombre"),"estado":value(e,"glosa"),
       "convocatoria":value(c,"descripcion"),"fecha_publicacion":value(f,"fecha_publicacion"),
       "fecha_cierre":value(f,"fecha_cierre"),"fecha_ultimo_cambio":value(f,"fecha_ultimo_cambio"),
       "monto_disponible_clp":value(m,"monto_disponible_clp"),"organismo_comprador":value(i,"organismo_comprador"),
       "rut_organismo":value(i,"rut"),"unidad_compra":value(i,"unidad_compra"),"region":value(i,"nombre_region"),
       "total_ofertas_recibidas":value(r,"total_ofertas_recibidas"),"motivo_seleccion":value(mot,"motivo_seleccion"),
       "url_detalle":value(link,"detalle"),"fecha_sincronizacion":stamp(),"modalidad":"Compra Ágil"}
    return {k:safe(v) for k,v in d.items()}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fecha",required=True)
    p.add_argument("--pagina",type=int,default=1)
    p.add_argument("--escribir",action="store_true",help="Sin esta opción no se escribe")
    a=p.parse_args()
    day=datetime.strptime(a.fecha,"%Y-%m-%d").date()
    if not 1<=a.pagina<=10000:p.error("Página fuera de rango")
    if day>datetime.now(ZoneInfo("America/Santiago")).date():p.error("Fecha futura")
    if not a.escribir:raise SystemExit("Solo la ejecución explícita --escribir permite cambios")
    creds=Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets"])
    book=gspread.authorize(creds).open_by_key(os.environ["GOOGLE_SHEET_ID"])
    proces=book.worksheet("Procesos")
    heads=proces.row_values(1)
    if len(heads)!=len(set(heads)) or not {"codigo","modalidad","nombre"}.issubset(heads):
        raise RuntimeError("Esquema Procesos incompatible")
    try:ctrl=book.worksheet("ControlV2")
    except gspread.WorksheetNotFound:
        ctrl=book.add_worksheet(title="ControlV2",rows=1000,cols=10)
    actual=ctrl.row_values(1)
    if not actual:ctrl.update(range_name="A1:J1",values=[CONTROL_HEAD],value_input_option="RAW")
    elif actual!=CONTROL_HEAD:raise RuntimeError("Esquema ControlV2 incompatible, sin escrituras")
    key=f"compra_agil:{a.fecha}:pagina:{a.pagina}:10"
    control_rows=ctrl.get_all_values()
    found=[(i,row) for i,row in enumerate(control_rows[1:],2) if row and row[0]==key]
    if len(found)>1:raise RuntimeError("Checkpoint duplicado")
    previous=found[0][1] if found else []
    if len(previous)>4 and previous[4]=="completo":
        print("CHECKPOINT_COMPLETO: página ya procesada; sin HTTP ni escrituras");return
    if len(previous)>6 and previous[6] and previous[6]>stamp():
        print("CHECKPOINT_EN_ESPERA: todavía no corresponde reintentar");return
    attempts=int(previous[5]) if len(previous)>5 and previous[5] else 0
    def checkpoint(state,http="",count=0,next_date=""):
        row=[key,"compra_agil_listado",a.fecha,a.pagina,state,attempts+1,next_date,http,count,stamp()]
        if found:ctrl.update(range_name=f"A{found[0][0]}:J{found[0][0]}",values=[row],value_input_option="RAW")
        else:ctrl.append_row(row,value_input_option="RAW",table_range="A:J")
    start=datetime.combine(day,datetime.min.time(),ZoneInfo("America/Santiago"))
    end=datetime.combine(day+timedelta(days=1),datetime.min.time(),ZoneInfo("America/Santiago"))-timedelta(seconds=1)
    url=BASE+"?"+urlencode({"publicado_desde":start.isoformat(timespec="seconds"),
        "publicado_hasta":end.isoformat(timespec="seconds"),"numero_pagina":a.pagina,"tamano_pagina":10})
    request=Request(url,headers={"ticket":os.environ["CHILECOMPRA_TICKET"],"Accept":"application/json"})
    if not global_v2.reserve(ctrl):
        print('V2_NO_CONSULTA_CONTROL_GLOBAL');return
    try:
        with urlopen(request,timeout=45) as resp:
            status=resp.status;data=json.loads(resp.read())
    except HTTPError as exc:
        status=exc.code;exc.close()
        global_v2.finish(ctrl,status)
        wait=3600 if status==429 else min(3600,300*2**min(attempts,3))
        next_date=(datetime.now(timezone.utc)+timedelta(seconds=wait)).isoformat(timespec="seconds")
        checkpoint("espera" if status in (429,500,502,503,504) else "revision",status,0,next_date if status in (429,500,502,503,504) else "")
        print(f"HTTP_{status}: registrado sin cambios en Procesos");return
    except (URLError,TimeoutError,OSError) as exc:
        global_v2.finish(ctrl,None)
        next_date=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat(timespec="seconds")
        checkpoint("espera","red",0,next_date)
        print("ERROR_RED: registrado",type(exc).__name__);return
    global_v2.finish(ctrl,200)
    payload=data.get("payload") if isinstance(data,dict) else None
    if data.get("success") not in ("OK",True) or not isinstance(payload,dict):
        raise RuntimeError("Respuesta inválida, no escribir")
    items=payload.get("items");pageinfo=payload.get("paginacion") or {}
    total=int(pageinfo.get("total_paginas") or 0)
    if not isinstance(items,list) or len(items)>10 or total<a.pagina or (a.pagina<total and not items):
        raise RuntimeError("Paginación inconsistente")
    codes=[str(x.get("codigo","")) for x in items if isinstance(x,dict)]
    if len(codes)!=len(items) or not all(codes) or len(set(codes))!=len(codes):
        raise RuntimeError("Códigos inválidos o duplicados")
    existing=proces.get_all_values();idx=heads.index("codigo")
    records={}
    for n,row in enumerate(existing[1:],2):
        code=row[idx] if len(row)>idx else ""
        if code:
            if code in records:raise RuntimeError("Duplicados en Procesos; no escribir")
            records[code]=(n,row)
    updates=[];appends=[]
    last_col=""
    num=len(heads)
    while num:
        num,rem=divmod(num-1,26);last_col=chr(65+rem)+last_col
    for item in items:
        d=transform(item);code=str(item["codigo"])
        if code in records:
            rownum,old=records[code]
            new=[]
            for i,h in enumerate(heads):
                prev=old[i] if i<len(old) else ""
                new.append(d.get(h) or prev)
            updates.append({"range":f"Procesos!A{rownum}:{last_col}{rownum}","values":[new]})
        else:appends.append([d.get(h,"") for h in heads])
    if updates:book.values_batch_update({"valueInputOption":"RAW","data":updates})
    if appends:proces.append_rows(appends,value_input_option="RAW")
    checkpoint("completo",200,len(items))
    print(f"V2_SHEETS_OK: página {a.pagina}/{total}, {len(items)} registros, {len(appends)} nuevos, {len(updates)} actualizados")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("V2_SHEETS_ERROR:",type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(1)
