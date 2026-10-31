#!/usr/bin/env python3
"""Exportación exclusiva del histórico oficial ya conciliado; no modifica el exportador diario."""
import argparse, datetime as dt, json, os, pathlib, shutil, tempfile
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"frontend-v2/data"
MAP={
 "Procesos":("procesos",["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre","monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas","motivo_seleccion","url_detalle","categoria","subcategoria","modalidad"]),
 "OrdenesCompra":("ordenescompra",["codigo_oc","codigo_proceso","fecha_creacion","fecha_aceptacion","estado","proveedor","monto_total_oc_clp","tipo_oc","cantidad_lineas","total_lineas_neto"]),
}
API_MAP={
 "Ofertas":("ofertas",["id_cotizacion","codigo","proveedor","monto_ofertado_clp","fecha_oferta","seleccionado"]),
 "Resultados":("resultados",["codigo","id_cotizacion_ganadora","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","validado","monto_oferta_seleccionada_clp","estado_verificacion_oc"])
}
def exportar(periodo, aplicar, incluir_api=False):
 import gspread
 from google.oauth2.service_account import Credentials
 from importlib.util import spec_from_file_location,module_from_spec
 cred=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
 secret=os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON","")
 if not secret and (not cred or not pathlib.Path(cred).is_file()):raise RuntimeError("Falta credencial autorizada")
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
 dest=cat["periodos"][periodo]
 if dest["tipo"]!="historico" or dest.get("estado") not in ("cierre_operativo_pendiente_conciliacion_oficial","cerrado_tras_carga_oficial_verificada"):raise RuntimeError("Solo histórico mensual con rotación confirmada")
 creds=Credentials.from_service_account_file(cred,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]) if cred and pathlib.Path(cred).is_file() else Credentials.from_service_account_info(json.loads(secret),scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
 book=gspread.authorize(creds).open_by_key(dest["id"])
 spec=spec_from_file_location("mer_schema",ROOT/"scripts/importador_historicos_v2.py")
 mod=module_from_spec(spec);spec.loader.exec_module(mod)
 public=json.loads((DATA/"catalogo-publico.json").read_text())
 matches=[p for p in public["periodos"] if p["periodo"]==periodo]
 if len(matches)>1:raise RuntimeError("Periodo publico duplicado")
 if not matches:
  # Alta automática únicamente para un mes operativo autorizado en catálogo privado.
  # No convertir el mes anterior en histórico: eso requiere cierre oficial posterior.
  previous=max((x["periodo"] for x in public["periodos"]),default="")
  if periodo<=previous:raise RuntimeError("Alta de período no consecutivo o ya publicado")
  entry={"periodo":periodo,"tipo":"operativo","conteos":{e:0 for e in ("procesos","ofertas","resultados","ordenescompra")},
         "partes":{e:[] for e in ("procesos","ofertas","resultados","ordenescompra")}}
  public["periodos"].append(entry)
  matches=[entry]
 current=matches[0]
 work=pathlib.Path(tempfile.mkdtemp(prefix="export_mer_v2_"))
 changes={}
 try:
  entidades={**MAP,**API_MAP} if incluir_api else MAP
  if not incluir_api and not current["partes"].get("ofertas") and not current["partes"].get("resultados"):
   # Primer día del mes: producir las cuatro entidades antes de indexar.
   entidades={**MAP,**API_MAP}
  seleccionados={}
  if "Resultados" in entidades:
   cotizaciones=book.worksheet("Ofertas").get_all_values()
   columnas=mod.SCHEMA["Ofertas"]
   if not cotizaciones or cotizaciones[0]!=columnas:raise ValueError("Contrato de Ofertas incompatible")
   for raw in cotizaciones[1:]:
    r=dict(zip(columnas,(raw+[""]*len(columnas))[:len(columnas)]))
    if str(r["seleccionado"]).strip() in ("1","True","true") and r["codigo"] and r["id_cotizacion"] and r["proveedor"]:
     k=(r["codigo"],r["id_cotizacion"])
     if k in seleccionados and seleccionados[k]!=r["proveedor"]:raise ValueError("Identidades de oferta en conflicto")
     seleccionados[k]=r["proveedor"]
  for sheet,(entity,fields) in entidades.items():
   vals=book.worksheet(sheet).get_all_values()
   expected=mod.SCHEMA[sheet]
   if not vals or vals[0]!=expected:raise ValueError("Contrato MER inválido: "+sheet)
   ix={k:expected.index(k) for k in fields}
   keys=set(); rows=[]
   for raw in vals[1:]:
    if not raw or not raw[0]:raise ValueError("PK vacía: "+sheet)
    raw=(raw+[""]*len(expected))[:len(expected)]
    pk=(raw[expected.index("codigo")],raw[expected.index("id_cotizacion_ganadora")]) if sheet=="Resultados" else (raw[expected.index("codigo")],raw[expected.index("id_cotizacion")]) if sheet=="Ofertas" else (raw[0],)
    if not all(pk) or pk in keys:raise ValueError("PK duplicada/incompleta: "+sheet)
    keys.add(pk)
    record={key:raw[pos] for key,pos in ix.items()}
    if sheet=="Resultados":
     record["proveedor_seleccionado"]=seleccionados.get((record["codigo"],record["id_cotizacion_ganadora"]),"")
    rows.append(record)
   rows.sort(key=lambda r:r[fields[0]])
   folder=work/entity/periodo;folder.mkdir(parents=True)
   paths=[]
   if not rows:
    (folder/"0001.json").write_text("[]",encoding="utf-8")
    paths.append(f"data/partes/{entity}/{periodo}/0001.json")
   for i in range(0,len(rows),1000):
    name=f"{i//1000+1:04d}.json"
    (folder/name).write_text(json.dumps(rows[i:i+1000],ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    paths.append(f"data/partes/{entity}/{periodo}/{name}")
   if sum(len(json.loads((work/p.split("/")[2]/periodo/p.split("/")[-1]).read_text())) for p in paths)!=len(rows):
    raise ValueError("Fragmentos inconsistentes")
   changes[entity]={"count":len(rows),"paths":paths}
  print(json.dumps({"periodo":periodo,"modo":"APLICAR" if aplicar else "SIMULACION","conteos":{k:v["count"] for k,v in changes.items()}},ensure_ascii=False))
  if not aplicar:return
  # Preparar catálogo; nunca cambiar Ofertas o Resultados sin una fuente actualizada.
  for entity,d in changes.items():
   current["conteos"][entity]=d["count"]
   current["partes"][entity]=d["paths"]
  current["tipo"]="historico"
  public["fecha_publicacion"]=dt.datetime.now(dt.timezone.utc).isoformat()
  # Los fragmentos deben existir ANTES del commit del catálogo.
  for entity in changes:
   destination=DATA/"partes"/entity/periodo
   destination.mkdir(parents=True,exist_ok=True)
   # Conservar fragmentos previos hasta completar la generación.
   for p in (work/entity/periodo).glob("*.json"):
    # /tmp y el repositorio pueden estar en sistemas de archivos diferentes.
    # Copiar primero a un temporal dentro del destino y reemplazar allí.
    staged=None
    try:
     with tempfile.NamedTemporaryFile(prefix=".export_mer_",suffix=".tmp",dir=destination,delete=False) as temp:
      staged=pathlib.Path(temp.name)
      with p.open("rb") as source:shutil.copyfileobj(source,temp)
     os.replace(staged,destination/p.name)  # mismo filesystem: reemplazo atómico
    finally:
     if staged is not None:staged.unlink(missing_ok=True)
   desired={pathlib.Path(p).name for p in changes[entity]["paths"]}
   for old in destination.glob("*.json"):
    if old.name not in desired:old.unlink()
  tmp=DATA/"catalogo-publico.json.tmp"
  tmp.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  os.replace(tmp,DATA/"catalogo-publico.json")
  print("EXPORTACION_V2_VERIFICADA")
 finally:shutil.rmtree(work,ignore_errors=True)
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--periodo",default=dt.datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m"))
 ap.add_argument("--aplicar",action="store_true")
 ap.add_argument("--incluir-api",action="store_true",help="Exportar también Ofertas y Resultados; solo orquestación nocturna")
 args=ap.parse_args()
 today=dt.datetime.now(ZoneInfo("America/Santiago")).date()
 expected=(today.replace(day=1)-dt.timedelta(days=1)).strftime("%Y-%m")
 if args.periodo!=expected or today.day<10:
  ap.error("Solo se permite republicar el mes anterior desde el día 10")
 exportar(args.periodo,args.aplicar,args.incluir_api)
