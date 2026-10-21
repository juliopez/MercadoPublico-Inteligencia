#!/usr/bin/env python3
"""Agregados públicos de actores por entidad y período; sin datos privados."""
import argparse, hashlib, json, re, unicodedata
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
ACTORS={"procesos":"organismo_comprador","ofertas":"proveedor","resultados":"adjudicatario","ordenescompra":"proveedor"}
MONEY={"procesos":"monto_disponible_clp","ofertas":"monto_ofertado_clp","resultados":"monto_adjudicado_clp","ordenescompra":"monto_total_oc_clp"}
def norm(x):
 v=unicodedata.normalize("NFD",str(x or "").casefold())
 return re.sub(r"\s+"," ","".join(c for c in v if unicodedata.category(c)!="Mn")).strip()
def amount(x):
 if x is None or str(x).strip()=="":return None
 raw=str(x).strip().replace(".","").replace(",",".")
 try:
  v=float(raw)
  return round(v) if 0<=v<10**15 else None
 except (ValueError,OverflowError):return None
def build(period,entity,root=ROOT):
 if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])",period) or entity not in ACTORS:raise ValueError("Argumentos incorrectos")
 catalog=json.loads((root/"data/catalogo-publico.json").read_text(encoding="utf8"))
 info=next(x for x in catalog["periodos"] if x["periodo"]==period)
 grouped={}; count=0;identified=0
 for rel in info["partes"][entity]:
  if not re.fullmatch(rf"data/partes/{entity}/{period}/[a-z0-9_-]+\.json",rel):raise ValueError("Ruta inválida")
  rows=json.loads((root/rel).read_text(encoding="utf8"))
  for row in rows:
   count+=1
   name=str(row.get(ACTORS[entity]) or "").strip()
   key=norm(name)
   if not key:continue
   identified+=1
   if key not in grouped:grouped[key]={"nombre":name,"registros":0,"monto_total_clp":0,"registros_con_monto":0}
   item=grouped[key];item["registros"]+=1
   v=amount(row.get(MONEY[entity]))
   if v is not None:item["monto_total_clp"]+=v;item["registros_con_monto"]+=1
 if count!=info["conteos"][entity]:raise ValueError("Conteo incorrecto")
 out=root/"data/perfiles"/period/entity;out.mkdir(parents=True,exist_ok=True)
 shards=defaultdict(dict)
 for key,value in grouped.items():shards[hashlib.sha256(key.encode("utf8")).hexdigest()[:2]][key]=value
 for shard,items in shards.items():
  (out/f"{shard}.json").write_text(json.dumps(items,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 meta={"version":1,"periodo":period,"entidad":entity,"campo_actor":ACTORS[entity],"campo_monto":MONEY[entity],
       "registros":count,"registros_identificados":identified,"actores":len(grouped),"archivos":len(shards),
       "nota":"Cifras descriptivas por entidad/mes; registros y montos no equivalen a operaciones únicas ni adjudicaciones verificadas."}
 (out/"meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf8")
 print("PERFILES_OK",period,entity,count,len(grouped),len(shards))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--periodo",required=True);p.add_argument("--entidad",required=True,choices=ACTORS)
 a=p.parse_args();build(a.periodo,a.entidad)
