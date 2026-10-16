#!/usr/bin/env python3
"""ChileCompra Compra Ágil -> Google Sheets, idempotente por código."""
import json, os, sys, time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
TICKET = os.environ["CHILECOMPRA_TICKET"]
SA = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = ["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre",
           "fecha_ultimo_cambio","monto_disponible_clp","organismo_comprador",
           "rut_organismo","unidad_compra","region","total_ofertas_recibidas",
           "motivo_seleccion","url_detalle","fecha_sincronizacion"]
BASE="https://api2.mercadopublico.cl/v2/compra-agil"

def value(obj, key):
    return (obj or {}).get(key) or ""

def safe(x):
    if x is None: return ""
    if isinstance(x, (dict,list)): x=json.dumps(x,ensure_ascii=False)
    s=str(x)
    return "'"+s if s.startswith(("=","+","-","@")) and not s.lstrip("-").replace(".","",1).isdigit() else s

def row(item, now):
    e=item.get("estado") or {}; c=item.get("convocatoria") or {}
    f=item.get("fechas") or {}; m=item.get("montos") or {}
    i=item.get("institucion") or {}; r=item.get("resumen") or {}
    motive=item.get("motivos") or {}; links=item.get("links") or {}
    return list(map(safe,[item.get("codigo"),item.get("nombre"),value(e,"glosa"),
        value(c,"descripcion"),value(f,"fecha_publicacion"),value(f,"fecha_cierre"),
        value(f,"fecha_ultimo_cambio"),value(m,"monto_disponible_clp"),
        value(i,"organismo_comprador"),value(i,"rut"),value(i,"unidad_compra"),
        value(i,"nombre_region"),value(r,"total_ofertas_recibidas"),
        value(motive,"motivo_seleccion"),value(links,"detalle"),now]))

def fetch(page, start, end):
    args={"publicado_desde":start,"publicado_hasta":end,
          "q":"capacitacion","tamano_pagina":50,"numero_pagina":page}
    req=Request(BASE+"?"+urlencode(args),headers={"ticket":TICKET,"Accept":"application/json"})
    for attempt in range(3):
        try:
            with urlopen(req,timeout=50) as response:
                data=json.load(response)
            if not data.get("payload") or data.get("success") not in (True,"OK"):
                raise RuntimeError("Respuesta API sin payload válido")
            return data["payload"]
        except HTTPError as e:
            if e.code not in (429,502,503,504) or attempt==2: raise
            retry=e.headers.get("Retry-After")
            delay=min(60,int(retry)) if retry and retry.isdigit() else (attempt+1)*10
            time.sleep(delay)
        except (URLError,TimeoutError):
            if attempt==2: raise
            time.sleep((attempt+1)*10)

def main():
    now=datetime.now(timezone.utc)
    since=now-timedelta(days=int(os.getenv("SYNC_LOOKBACK_DAYS","7")))
    start=since.strftime("%Y-%m-%dT00:00:00")
    end=now.strftime("%Y-%m-%dT23:59:59")
    maxpages=int(os.getenv("SYNC_MAX_PAGES","20"))
    found={}
    totalpages=None
    for page in range(1,maxpages+1):
        payload=fetch(page,start,end)
        pages=(payload.get("paginacion") or {}).get("total_paginas",0)
        totalpages=pages
        batch=payload.get("items") or []
        for item in batch:
            if item.get("codigo"):found[item["codigo"]]=row(item,now.isoformat())
        print(f"Página {page}/{pages}, registros {len(batch)}, únicos {len(found)}",flush=True)
        if page>=pages or not batch: break
        time.sleep(1)
    if totalpages and totalpages>maxpages:
        raise RuntimeError(f"Extracción incompleta: {totalpages} páginas, máximo {maxpages}. No se escribe Google Sheets.")
    if not found:
        print("Sin registros para ventana; no se cambia la hoja.")
        return
    creds=Credentials.from_service_account_info(SA,scopes=SCOPES)
    sheet=gspread.authorize(creds).open_by_key(SHEET_ID).worksheet("Procesos")
    existing=sheet.get_all_values()
    if not existing or existing[0][:15]!=HEADERS[:15]:
        raise RuntimeError("Cabeceras de Procesos no coinciden con el esquema.")
    # Escribe filas completas conservando el formato original y la columna P.
    if len(existing[0])<16:sheet.update(range_name="P1",values=[["fecha_sincronizacion"]],value_input_option="RAW")
    index={r[0]:n for n,r in enumerate(existing[1:],start=2) if r and r[0]}
    updates=[]; appends=[]
    for code,values in found.items():
        if code in index:
            updates.append({"range":f"Procesos!A{index[code]}:P{index[code]}","values":[values]})
        else:appends.append(values)
    # API batch update of values, in manageable batches.
    for i in range(0,len(updates),100):
        sheet.spreadsheet.values_batch_update({"valueInputOption":"RAW","data":updates[i:i+100]})
    if appends:sheet.append_rows(appends,value_input_option="RAW",table_range="A:P")
    print(f"Sincronizados: {len(updates)} actualizados, {len(appends)} nuevos.")

if __name__=="__main__":
    main()
