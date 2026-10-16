#!/usr/bin/env python3
"""ChileCompra Compra Ágil -> Google Sheets, idempotente por código."""
import json, os, sys, time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import gspread
from api_retry import fetch_json
from google.oauth2.service_account import Credentials

SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
TICKET = os.environ["CHILECOMPRA_TICKET"]
RAW_SA = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
if not RAW_SA:
    raise SystemExit("Falta GOOGLE_SERVICE_ACCOUNT_JSON en GitHub Secrets; sin cambios.")
try:
    SA = json.loads(RAW_SA)
except json.JSONDecodeError:
    raise SystemExit("GOOGLE_SERVICE_ACCOUNT_JSON no es JSON valido; sin cambios.")
if not isinstance(SA, dict) or not SA.get("client_email") or not SA.get("private_key"):
    raise SystemExit("Credencial Google incompleta; sin cambios.")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = ["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre",
           "fecha_ultimo_cambio","monto_disponible_clp","organismo_comprador",
           "rut_organismo","unidad_compra","region","total_ofertas_recibidas",
           "motivo_seleccion","url_detalle","fecha_sincronizacion","categoria","subcategoria","codigo_categoria_oficial","modalidad"]
BASE="https://api2.mercadopublico.cl/v2/compra-agil"
LICITACION_ESTADOS={"5":"Publicada","6":"Cerrada","7":"Desierta","8":"Adjudicada","18":"Revocada","19":"Suspendida"}

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
        value(motive,"motivo_seleccion"),value(links,"detalle"),now,"Sin clasificar","Sin clasificar","","Compra Ágil"]))

def fetch(page, start, end):
    args={"publicado_desde":start,"publicado_hasta":end,
          "tamano_pagina":50,"numero_pagina":page}
    req=Request(BASE+"?"+urlencode(args),headers={"ticket":TICKET,"Accept":"application/json"})
    data=fetch_json(req,timeout=50,label=f"Compra Ágil página {page}")
    if not data.get("payload") or data.get("success") not in (True,"OK"):
        raise RuntimeError("Respuesta API sin payload válido; no se escriben datos")
    return data["payload"]

def main():
    now=datetime.now(timezone.utc)
    fecha=os.getenv("SYNC_FECHA_2026","2026-10-15")
    try:
        day=datetime.strptime(fecha,"%Y-%m-%d").date()
    except ValueError:
        raise SystemExit("Fecha inválida; usar AAAA-MM-DD")
    if day>datetime.now(__import__("zoneinfo").ZoneInfo("America/Santiago")).date():
        raise SystemExit("La fecha no puede ser futura en Chile")
    start=fecha+"T00:00:00"
    end=fecha+"T23:59:59"
    maxpages=int(os.getenv("SYNC_MAX_PAGES","20"))
    modalidad=os.getenv("SYNC_MODALIDAD","compra_agil")
    if modalidad not in ("compra_agil","licitaciones"):raise SystemExit("Modalidad no admitida")
    found={}
    totalpages=None
    if modalidad=="licitaciones":
        args=urlencode({"fecha":datetime.strptime(fecha,"%Y-%m-%d").strftime("%d%m%Y"),"ticket":TICKET})
        req=Request("https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?"+args,headers={"Accept":"application/json"})
        data=fetch_json(req,timeout=65,label="Licitaciones "+fecha)
        if not isinstance(data,dict) or not isinstance(data.get("Listado"),list):raise RuntimeError("Formato V1 no reconocido")
        if data.get("Cantidad") is not None and int(data["Cantidad"])!=len(data["Listado"]):raise RuntimeError("Listado V1 incompleto")
        for x in data["Listado"]:
            b=x.get("Comprador") or {}
            if not isinstance(b,dict):b={}
            code=x.get("CodigoExterno")
            if not code:raise RuntimeError("Licitación sin código; sin escrituras")
            estado_code=str(x.get("CodigoEstado") or "")
            estado=x.get("Estado") or LICITACION_ESTADOS.get(estado_code) or ("Código "+estado_code if estado_code else "")
            # La API V1 documenta que fecha=DDMMAAAA lista licitaciones publicadas ese día.
            # El listado básico puede carecer de FechaPublicacion; usar fecha de consulta,
            # NO confundir con FechaCreacion del objeto de respuesta (fecha de consulta).
            publicada=x.get("FechaPublicacion") or fecha
            found[str(code)]=list(map(safe,[code,x.get("Nombre"),estado,"",publicada,x.get("FechaCierre"),x.get("FechaAdjudicacion"),x.get("MontoEstimado"),b.get("NombreOrganismo"),b.get("RutUnidad"),b.get("NombreUnidad"),b.get("RegionUnidad"),"","","",now.isoformat(),"Sin clasificar","Sin clasificar","","Licitación"]))
        print("API_V1_LICITACIONES",fecha,"registros",len(found),flush=True)
    else:
      for page in range(1,maxpages+1):
        payload=fetch(page,start,end)
        pages=int((payload.get("paginacion") or {}).get("total_paginas") or 0)
        if pages<1:raise RuntimeError("Paginación ausente: sin escritura")
        totalpages=pages
        batch=payload.get("items") or []
        for item in batch:
            if item.get("codigo"):found[item["codigo"]]=row(item,now.isoformat())
        print(f"Página {page}/{pages}, registros {len(batch)}, únicos {len(found)}",flush=True)
        if page>=pages: break
        if not batch:raise RuntimeError("Página vacía antes de completar la paginación: sin escritura")
        time.sleep(1)
    if modalidad=="compra_agil" and totalpages and totalpages>maxpages:
        raise RuntimeError(f"Extracción incompleta: {totalpages} páginas, máximo {maxpages}. No se escribe Google Sheets.")
    if not found:
        print("Sin registros para ventana; no se cambia la hoja.")
        return
    creds=Credentials.from_service_account_info(SA,scopes=SCOPES)
    sheet=gspread.authorize(creds).open_by_key(SHEET_ID).worksheet("Procesos")
    existing=sheet.get_all_values()
    if not existing or existing[0][:20]!=HEADERS:
        raise RuntimeError("Cabeceras de Procesos no coinciden con el esquema.")
    # Conserva atributos documentales existentes si la API actual no los informa.
    # No modificar cabeceras ni columnas opcionales U:W tras la migración.
    index={}
    for n,r in enumerate(existing[1:],start=2):
        if r and r[0]:
            if r[0] in index:raise RuntimeError("Código duplicado en Sheets")
            index[r[0]]=n
    updates=[]; appends=[]
    for code,values in found.items():
        if code in index:
            old=existing[index[code]-1]
            for k in range(20):
                if len(old)>k and not values[k] and old[k]:values[k]=old[k]
            for k in (16,17,18):
                if len(old)>k and old[k] and old[k]!="Sin clasificar":values[k]=old[k]
            # Solo actualizar el contrato base A:T: las columnas añadidas permanecen intactas.
            updates.append({"range":f"Procesos!A{index[code]}:T{index[code]}","values":[values]})
        else:appends.append(values)
    # API batch update of values, in manageable batches.
    for i in range(0,len(updates),100):
        sheet.spreadsheet.values_batch_update({"valueInputOption":"RAW","data":updates[i:i+100]})
    if appends:sheet.append_rows(appends,value_input_option="RAW",table_range="A:T")
    print(f"Sincronizados: {len(updates)} actualizados, {len(appends)} nuevos.")

if __name__=="__main__":
    main()
