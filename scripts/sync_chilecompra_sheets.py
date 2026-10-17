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


def upsert_rows(found):
    if not found:return (0,0)
    creds=Credentials.from_service_account_info(SA,scopes=SCOPES)
    sheet=gspread.authorize(creds).open_by_key(SHEET_ID).worksheet("Procesos")
    existing=sheet.get_all_values()
    if not existing:
        raise RuntimeError("Hoja Procesos sin cabeceras")
    columns=existing[0]
    required=("codigo","nombre","estado","fecha_publicacion","organismo_comprador","modalidad")
    if len(columns)!=len(set(columns)) or any(h not in columns for h in required):
        raise RuntimeError("Esquema Procesos inválido: columnas obligatorias ausentes o repetidas")
    # Proyectar por nombres, no posiciones: admite la reducción controlada de columnas.
    code_col=columns.index("codigo")
    index={}
    for n,r in enumerate(existing[1:],start=2):
        code=r[code_col] if len(r)>code_col else ""
        if code:
            if code in index:raise RuntimeError("Código duplicado en Sheets")
            index[code]=n
    def col_letter(n):
        out=""
        while n:
            n,rem=divmod(n-1,26)
            out=chr(65+rem)+out
        return out
    last=col_letter(len(columns))
    updates=[];appends=[]
    for code,api_values in found.items():
        by_name=dict(zip(HEADERS,api_values))
        new=[by_name.get(h,"") for h in columns]
        if code in index:
            old=existing[index[code]-1]
            for k,h in enumerate(columns):
                previous=old[k] if k<len(old) else ""
                if not new[k] and previous:new[k]=previous
                if h in ("categoria","subcategoria","codigo_categoria_oficial") and previous and previous!="Sin clasificar":
                    new[k]=previous
                if h not in HEADERS:new[k]=previous
            updates.append({"range":f"Procesos!A{index[code]}:{last}{index[code]}","values":[new]})
        else:appends.append(new)
    for i in range(0,len(updates),100):
        sheet.spreadsheet.values_batch_update({"valueInputOption":"RAW","data":updates[i:i+100]})
    if appends:sheet.append_rows(appends,value_input_option="RAW",table_range=f"A:{last}")
    print(f"Sincronizados: {len(updates)} actualizados, {len(appends)} nuevos.",flush=True)
    return len(updates),len(appends)


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
            found[str(code)]=list(map(safe,[code,x.get("Nombre"),estado,"",publicada,x.get("FechaCierre"),"",x.get("MontoEstimado"),b.get("NombreOrganismo"),b.get("RutUnidad"),b.get("NombreUnidad"),b.get("RegionUnidad"),"","","",now.isoformat(),"Sin clasificar","Sin clasificar","","Licitación"]))
        print("API_V1_LICITACIONES",fecha,"registros",len(found),flush=True)
    else:
        creds=Credentials.from_service_account_info(SA,scopes=SCOPES)
        book=gspread.authorize(creds).open_by_key(SHEET_ID)
        control=book.worksheet("Control")
        control_values=control.get("A1:B")
        if not control_values or control_values[0][:2]!=["variable","valor"]:
            raise RuntimeError("Control A:B requiere encabezados variable, valor")
        prefix="compra_agil_page:"+fecha+":"
        previous={}
        for r in control_values[1:]:
            if len(r)<2 or not r[0].startswith(prefix):continue
            page_string=r[0][len(prefix):]
            if not page_string.isdigit() or not r[1].isdigit():raise RuntimeError("Checkpoint de paginación inválido")
            page_number=int(page_string)
            if page_number in previous and previous[page_number]!=int(r[1]):raise RuntimeError("Checkpoint contradictorio")
            previous[page_number]=int(r[1])
        totals=set(previous.values())
        if len(totals)>1:raise RuntimeError("Número total de páginas contradictorio")
        totalpages=next(iter(totals),None)
        if totalpages is not None and totalpages>maxpages:
            raise RuntimeError(f"Hay {totalpages} páginas y el máximo configurado es {maxpages}")
        page=1
        while totalpages is None or page<=totalpages:
            if page>maxpages:raise RuntimeError(f"Extracción supera {maxpages} páginas, no se considera completa")
            if page in previous:
                print(f"Página {page}/{totalpages}: ya persistida; omitida",flush=True)
                page+=1
                continue
            payload=fetch(page,start,end)
            pages=int((payload.get("paginacion") or {}).get("total_paginas") or 0)
            if pages<1:raise RuntimeError("Paginación ausente")
            if totalpages is not None and pages!=totalpages:
                raise RuntimeError(f"Paginación cambió: antes {totalpages}, ahora {pages}; revisar ventana")
            totalpages=pages
            if totalpages>maxpages:raise RuntimeError(f"Extracción excede {maxpages} páginas")
            batch=payload.get("items")
            if not isinstance(batch,list):raise RuntimeError("Página sin lista de ítems")
            if page<totalpages and not batch:raise RuntimeError("Página intermedia vacía")
            page_rows={}
            for item in batch:
                if not isinstance(item,dict) or not item.get("codigo"):
                    raise RuntimeError("Registro Compra Ágil sin código; página no guardada")
                code=str(item["codigo"])
                if code in page_rows:raise RuntimeError("Código duplicado en página "+str(page))
                page_rows[code]=row(item,now.isoformat())
            # Persistencia antes del checkpoint: una interrupción intermedia
            # provocará reescritura idempotente, no pérdida de la página.
            updated,inserted=upsert_rows(page_rows)
            control.append_row([prefix+str(page),str(totalpages)],value_input_option="RAW",table_range="A:B")
            print(f"Página {page}/{totalpages} persistida: {len(page_rows)} registros, "
                  f"{inserted} nuevos, {updated} actualizados",flush=True)
            page+=1
        print("COMPRA_AGIL_LISTADO_COMPLETO",fecha,"páginas",totalpages,flush=True)
        return
    cap=int(os.getenv("SYNC_MAX_RECORDS","0"))
    if cap>0:
        found=dict(list(found.items())[:cap])
        print("LIMITE_VALIDACION",cap,"registros",len(found),flush=True)
    manifest=os.getenv("SYNC_MANIFEST_FILE","")
    if manifest:
        with open(manifest,"w",encoding="utf-8") as out:out.write("\n".join(found)+"\n")
    if not found:
        print("Sin registros para ventana; no se cambia la hoja.")
        return
    upsert_rows(found)

if __name__=="__main__":
    main()
