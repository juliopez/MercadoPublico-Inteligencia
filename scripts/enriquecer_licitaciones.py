#!/usr/bin/env python3
"""Enriquecer licitaciones registradas con consulta detallada por código.
No infiere ofertas individuales ni adjudicatarios contractuales.
Se ejecuta manualmente y actualiza solamente campos verificables vacíos en Procesos.
"""
import json,os,time
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request
from google.oauth2.service_account import Credentials
import gspread
from api_retry import fetch_json

limit=max(1,min(100,int(os.getenv("DETAIL_MAX_CODES","10"))))
offset=max(0,int(os.getenv("DETAIL_OFFSET","0")))
day=os.getenv("DETAIL_FECHA","").strip()
if day:datetime.strptime(day,"%Y-%m-%d")
book=gspread.authorize(Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),scopes=["https://www.googleapis.com/auth/spreadsheets"])).open_by_key(os.environ["GOOGLE_SHEET_ID"])
ws=book.worksheet("Procesos")
data=ws.get_all_values()
head=data[0]
required=("codigo","modalidad","fecha_publicacion","fecha_cierre","organismo_comprador","region")
if any(x not in head for x in required):raise SystemExit("ERROR_ESQUEMA: faltan columnas; sin escrituras")
idx={key:head.index(key) for key in head}
def value(row,key):return row[idx[key]] if idx[key]<len(row) else ""
selected=[(n,row) for n,row in enumerate(data[1:],start=2) if value(row,"modalidad").strip().startswith("Licitación") and (not day or value(row,"fecha_publicacion")[:10]==day)]
manifest=os.getenv("DETAIL_MANIFEST_FILE","")
if manifest:
    with open(manifest,encoding="utf-8") as handle:allowed={line.strip() for line in handle if line.strip()}
    selected=[(n,row) for n,row in selected if value(row,"codigo") in allowed]
selected=selected[offset:offset+limit]
print("DETALLE_LICITACIONES",len(selected),"fecha",day or "todas","offset",offset,flush=True)
updates=[];failed=[];awards_seen=0;awards_multiple=0;actas_seen=0
for n,(sheetrow,row) in enumerate(selected):
    if n:time.sleep(1)
    code=value(row,"codigo")
    try:
        url="https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?"+urlencode({"codigo":code,"ticket":os.environ["CHILECOMPRA_TICKET"]})
        resp=fetch_json(Request(url,headers={"Accept":"application/json"}),timeout=40,label="Licitación "+code)
        listing=resp.get("Listado")
        if not isinstance(listing,list) or len(listing)!=1 or str(listing[0].get("CodigoExterno"))!=code:
            raise ValueError("Respuesta de detalle no coincide con el código consultado")
        detail=listing[0]
        comprador=detail.get("Comprador") or {}
        fechas=detail.get("Fechas") or {}
        if not isinstance(comprador,dict) or not isinstance(fechas,dict):raise ValueError("Objetos del detalle inválidos")
        pairs={"fecha_cierre":fechas.get("FechaCierre"),"organismo_comprador":comprador.get("NombreOrganismo"),"region":comprador.get("RegionUnidad")}
        adjud=detail.get("Adjudicacion") or {}
        acta=adjud.get("UrlActa") if isinstance(adjud,dict) else None
        if isinstance(acta,str) and acta.startswith("https://"):
            actas_seen+=1
            if "url_detalle" in idx and not value(row,"url_detalle").strip():
                col=idx["url_detalle"];letter=""
                while col>=0:
                    letter=chr(65+col%26)+letter
                    col=col//26-1
                updates.append({"range":f"Procesos!{letter}{sheetrow}","values":[[acta]]})
        items=detail.get("Items") or {}
        lines=items.get("Listado") if isinstance(items,dict) else None
        winners=set()
        for item in (lines if isinstance(lines,list) else []):
            award=item.get("Adjudicacion") if isinstance(item,dict) else None
            if isinstance(award,dict) and award.get("RutProveedor"):
                winners.add(str(award["RutProveedor"]).strip())
        if winners:
            awards_seen+=1
            if len(winners)>1:awards_multiple+=1
        # No escribir Resultados: el esquema actual no representa
        # adjudicaciones por línea o múltiples proveedores.
        for key,new in pairs.items():
            if new is not None and str(new).strip() and not value(row,key).strip():
                col=idx[key];letter=""
                while col>=0:letter=chr(65+col%26)+letter;col=col//26-1
                updates.append({"range":f"Procesos!{letter}{sheetrow}","values":[[str(new)]]})
        print("DETALLE_OK",code,flush=True)
    except (ValueError,KeyError,TypeError,TimeoutError) as e:
        failed.append(code);print("::warning title=Detalle pendiente::"+code+" "+type(e).__name__,flush=True)
    except Exception as e:
        # Sin escrituras sobre datos de un proceso cuyo detalle falla.
        failed.append(code);print("::warning title=Consulta pendiente::"+code+" "+type(e).__name__,flush=True)
for k in range(0,len(updates),100):
    book.values_batch_update({"valueInputOption":"RAW","data":updates[k:k+100]})
print("DETALLE_RESUMEN",json.dumps({"seleccionados":len(selected),"campos_completados":len(updates),"actas_identificadas":actas_seen,"procesos_con_adjudicacion_por_linea":awards_seen,"con_multiples_proveedores":awards_multiple,"pendientes":len(failed)},ensure_ascii=False),flush=True)
if failed:raise SystemExit("DETALLE_PARCIAL: revisar procesos pendientes; no se han sustituido valores existentes")
