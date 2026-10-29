#!/usr/bin/env python3
"""Exportación controlada de MER operativo a los fragmentos V2. No escribe Sheets.
La publicación Git es responsabilidad del script Ubuntu posterior.
"""
import argparse, datetime as dt, json, os, pathlib, shutil, tempfile
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"frontend-v2/data"
MAP={
 "Procesos":("procesos",["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre","monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas","motivo_seleccion","url_detalle","categoria","subcategoria","modalidad"]),
 "OrdenesCompra":("ordenescompra",["codigo_oc","codigo_proceso","fecha_creacion","fecha_aceptacion","estado","proveedor","monto_total_oc_clp","tipo_oc","cantidad_lineas","total_lineas_neto"]),
 "Ofertas":("ofertas",["id_cotizacion","codigo","proveedor","monto_ofertado_clp","fecha_oferta","seleccionado"]),
 "Resultados":("resultados",["codigo","id_cotizacion_ganadora","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","validado","monto_oferta_seleccionada_clp","estado_verificacion_oc"])
}
def exportar(periodo, aplicar):
 import gspread
 from google.oauth2.service_account import Credentials
 from importlib.util import spec_from_file_location,module_from_spec
 cred=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
 secret=os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON","")
 if not secret and (not cred or not pathlib.Path(cred).is_file()):raise RuntimeError("Falta credencial autorizada")
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
 dest=cat["periodos"][periodo]
 if dest["tipo"]!="operativo":raise RuntimeError("El mes no es operativo")
 creds=Credentials.from_service_account_file(cred,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]) if cred and pathlib.Path(cred).is_file() else Credentials.from_service_account_info(json.loads(secret),scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
 book=gspread.authorize(creds).open_by_key(dest["id"])
 spec=spec_from_file_location("mer_schema",ROOT/"scripts/importador_historicos_v2.py")
 mod=module_from_spec(spec);spec.loader.exec_module(mod)
 public=json.loads((DATA/"catalogo-publico.json").read_text())
 matches=[p for p in public["periodos"] if p["periodo"]==periodo]
 if len(matches)!=1:raise RuntimeError("Periodo publico inexistente o duplicado")
 current=matches[0]
 work=pathlib.Path(tempfile.mkdtemp(prefix="export_mer_v2_"))
 changes={}
 try:
  for sheet,(entity,fields) in MAP.items():
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
    rows.append({key:raw[pos] for key,pos in ix.items()})
   rows.sort(key=lambda r:r[fields[0]])
   folder=work/entity/periodo;folder.mkdir(parents=True)
   paths=[]
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
 args=ap.parse_args()
 if args.periodo!=dt.datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m"):
  ap.error("Solo se permite exportar el mes operativo actual")
 exportar(args.periodo,args.aplicar)
