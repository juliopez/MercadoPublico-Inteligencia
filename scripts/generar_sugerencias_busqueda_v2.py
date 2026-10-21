#!/usr/bin/env python3
"""Sugerencias estáticas para búsqueda global V2 desde JSON públicos por mes/entidad."""
import argparse, collections, json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
TEXT={"procesos":("codigo","nombre","organismo_comprador"),"ofertas":("codigo","proveedor"),"resultados":("codigo","adjudicatario"),"ordenescompra":("codigo_oc","codigo_proceso","proveedor")}
FACETS={"procesos":("estado","modalidad"),"ofertas":("seleccionado",None),"resultados":("validado",None),"ordenescompra":("estado","tipo_oc")}
def norm(s):
 s=unicodedata.normalize("NFD",str(s or "").casefold())
 return "".join(c for c in s if unicodedata.category(c)!="Mn").strip()
def build(period,entity,root=ROOT):
 if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])",period) or entity not in TEXT:raise ValueError("Parámetros inválidos")
 catalog=json.loads((root/"data/catalogo-publico.json").read_text(encoding="utf8"))
 info=next(x for x in catalog["periodos"] if x["periodo"]==period)
 count=0; words=collections.Counter();facet=[collections.Counter(),collections.Counter()]
 for rel in info["partes"][entity]:
  if not re.fullmatch(rf"data/partes/{entity}/{period}/[a-z0-9_-]+\.json",rel):raise ValueError("Ruta inválida")
  rows=json.loads((root/rel).read_text(encoding="utf8"))
  count+=len(rows)
  for row in rows:
   tokens=set()
   for name in TEXT[entity]:
    tokens.update(w for w in re.findall(r"[a-z0-9]+",norm(row.get(name))) if len(w)>=3)
   words.update(tokens)
   for i,name in enumerate(FACETS[entity]):
    if name:
     v=str(row.get(name) or "").strip()
     if v:facet[i][v]+=1
 if count!=info["conteos"][entity]:raise ValueError("Conteo del catálogo no coincide")
 directory=root/"data/sugerencias"/period/entity;directory.mkdir(parents=True,exist_ok=True)
 shards=collections.defaultdict(list)
 for word,frequency in words.items():
  if frequency>=2:shards[word[:2]].append([word,frequency])
 for prefix,items in shards.items():
  best=sorted(items,key=lambda item:(-item[1],item[0]))[:120]
  (directory/(prefix+".json")).write_text(json.dumps([w for w,_ in best],ensure_ascii=False,separators=(",",":")),encoding="utf8")
 (directory/"facetas.json").write_text(json.dumps({"estado":[v for v,_ in facet[0].most_common(120)],"modalidad":[v for v,_ in facet[1].most_common(120)]},ensure_ascii=False,separators=(",",":")),encoding="utf8")
 (directory/"meta.json").write_text(json.dumps({"version":1,"periodo":period,"entidad":entity,"registros":count,"grupos":len(shards),"campos_texto":TEXT[entity],"campos_facetas":FACETS[entity]},ensure_ascii=False),encoding="utf8")
 print("SUGERENCIAS_VALIDAS",period,entity,count,len(shards))
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--periodo",required=True);ap.add_argument("--entidad",required=True,choices=TEXT)
 arg=ap.parse_args();build(arg.periodo,arg.entidad)
