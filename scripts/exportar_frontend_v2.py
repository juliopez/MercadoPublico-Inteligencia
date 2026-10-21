#!/usr/bin/env python3
"""Exportación aislada v2, por un período MER y una entidad; sin alterar la v1.

Ejemplo: python scripts/exportar_frontend_v2.py --periodo 2026-10 --entidad procesos
Usa GOOGLE_SERVICE_ACCOUNT_JSON o GOOGLE_APPLICATION_CREDENTIALS (JSON local).
No publica hasta verificar recuentos y sustituir atómicamente archivos v2.
"""
import argparse, datetime as dt, hashlib, json, os, shutil, tempfile, time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
ENTITIES={"procesos":"Procesos","ofertas":"Ofertas","resultados":"Resultados","ordenescompra":"OrdenesCompra"}
PUBLIC={
"procesos":["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre","monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas","motivo_seleccion","url_detalle","categoria","subcategoria","modalidad"],
"ofertas":["id_cotizacion","codigo","proveedor","monto_ofertado_clp","fecha_oferta","fuente","seleccionado"],
"resultados":["codigo","id_cotizacion_ganadora","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado","monto_oferta_seleccionada_clp","estado_verificacion_oc"],
"ordenescompra":["codigo_oc","codigo_proceso","fecha_creacion","fecha_aceptacion","estado","proveedor","monto_total_oc_clp","tipo_oc","cantidad_lineas","total_lineas_neto"]
}
def select(catalog,period):
 now=dt.datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m")
 entry=catalog["periodos"][period]
 if entry["tipo"]=="historico" and "auditad" in entry.get("estado","").lower():return entry
 if entry["tipo"]=="operativo" and period==now:return entry
 raise ValueError("Período no habilitado para publicar: "+period)
def export(period,entity,output):
 import gspread
 from google.oauth2.service_account import Credentials
 raw=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
 if raw:creds=Credentials.from_service_account_info(json.loads(raw),scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
 else:
  path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS",str(Path.home()/".config/mercadopublico/servicio-google.json"))
  creds=Credentials.from_service_account_file(path,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
 catalog=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf8"))
 entry=select(catalog,period)
 book=gspread.authorize(creds).open_by_key(entry["id"])
 sheet=book.worksheet(ENTITIES[entity])
 header=sheet.row_values(1)
 missing=[k for k in PUBLIC[entity] if k not in header]
 if missing:raise ValueError("Faltan campos públicos: "+repr(missing))
 indexes=[header.index(k) for k in PUBLIC[entity]]
 limit=max(indexes)+1
 # Lectura en tramos: evita cargar toda una entidad en memoria.
 target=output/"data"/"partes"/entity/period
 target.mkdir(parents=True,exist_ok=True)
 names=[];total=0;rowsbuf=[];sha=hashlib.sha256()
 def flush():
  nonlocal rowsbuf
  if not rowsbuf:return
  name=f"{len(names)+1:04d}.json"
  content=json.dumps(rowsbuf,ensure_ascii=False,separators=(",",":"))+"\n"
  if len(content.encode())>=25_000_000:raise ValueError("Fragmento superior a 25 MB")
  (target/name).write_text(content,encoding="utf8")
  names.append(f"data/partes/{entity}/{period}/{name}")
  rowsbuf=[]
 max_rows=max(1,sheet.row_count)
 for start in range(2,max_rows+1,5000):
  end=min(max_rows,start+4999)
  for attempt in range(5):
   try:
    block=sheet.get(f"A{start}:{chr(64+limit)}{end}")
    break
   except gspread.exceptions.APIError as exc:
    if getattr(getattr(exc,"response",None),"status_code",None)!=429 or attempt==4:raise
    time.sleep(35*(attempt+1))
  for rawrow in block:
   if not rawrow or not str(rawrow[0]).strip():continue
   row={key:str(rawrow[ix]) if ix<len(rawrow) else "" for key,ix in zip(PUBLIC[entity],indexes)}
   rowsbuf.append(row);total+=1
   sha.update((json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n").encode())
   if len(rowsbuf)>=1000:flush()
 flush()
 return {"periodo":period,"entidad":entity,"tipo":entry["tipo"],"total":total,"sha256":sha.hexdigest(),"partes":names}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--periodo",required=True)
 p.add_argument("--entidad",required=True,choices=sorted(ENTITIES))
 p.add_argument("--salida",type=Path,default=ROOT/"frontend-v2")
 a=p.parse_args()
 if len(a.periodo)!=7 or a.periodo[4]!="-" or not a.periodo[:4].isdigit() or a.periodo[5:] not in [f"{m:02d}" for m in range(1,13)]:
  p.error("Período inválido; usar AAAA-MM")
 # Solo se reemplaza la rama de datos requerida, dejando las demás intactas.
 with tempfile.TemporaryDirectory(prefix="mer-v2-") as work:
  staging=Path(work)
  summary=export(a.periodo,a.entidad,staging)
  base=a.salida/"data"
  manifest_path=base/"catalogo-publico.json"
  manifest=json.loads(manifest_path.read_text(encoding="utf8"))
  existing=next((x for x in manifest["periodos"] if x["periodo"]==a.periodo),None)
  if existing is None:
   existing={"periodo":a.periodo,"tipo":summary["tipo"],"conteos":{},"partes":{},"huellas":{}}
   manifest["periodos"].append(existing)
  existing["conteos"][a.entidad]=summary["total"]
  existing["partes"][a.entidad]=summary["partes"]
  existing["huellas"][a.entidad]=summary["sha256"]
  manifest["periodos"].sort(key=lambda x:x["periodo"])
  manifest["fecha_publicacion"]=dt.datetime.now(dt.timezone.utc).isoformat()
  newdir=staging/"data"/"partes"/a.entidad/a.periodo
  destination=base/"partes"/a.entidad/a.periodo
  destination.parent.mkdir(parents=True,exist_ok=True)
  if destination.exists():shutil.rmtree(destination)
  shutil.move(str(newdir),str(destination))
  manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  print("EXPORTACION_V2_OK",a.periodo,a.entidad,summary["total"],"fragmentos",len(summary["partes"]))
if __name__=="__main__":main()
