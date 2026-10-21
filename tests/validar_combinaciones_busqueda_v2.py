#!/usr/bin/env python3
"""Comprueba todos los índices públicos v3 contra sus fragmentos, sin modificarlos."""
import json
import re
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
FIELDS={
 "procesos":("codigo","nombre","organismo_comprador"),
 "ofertas":("codigo","proveedor"),
 "resultados":("codigo","adjudicatario"),
 "ordenescompra":("codigo_oc","codigo_proceso","proveedor"),
}
def norm(v):
 s=unicodedata.normalize("NFD",str(v or "").casefold())
 return "".join(c for c in s if unicodedata.category(c)!="Mn")
def check():
 catalog=json.loads((ROOT/"data/catalogo-publico.json").read_text(encoding="utf8"))
 total=0
 for month in catalog["periodos"]:
  period=month["periodo"]
  for entity,fields in FIELDS.items():
   n=month["conteos"].get(entity,0)
   if not n:
    print("SIN_REGISTROS",period,entity)
    continue
   directory=ROOT/"data/busqueda"/period/entity
   meta=json.loads((directory/"meta.json").read_text(encoding="utf8"))
   paths=month["partes"][entity]
   assert meta["version"]==3 and meta["periodo"]==period and meta["entidad"]==entity
   assert meta["conteo"]==n and meta["fragmentos"]==len(paths)
   assert meta["formato"]=="referencias_fragmento_fila"
   # Las primeras filas reales dan consultas positivas para cada combinación.
   rowset=json.loads((ROOT/paths[0]).read_text(encoding="utf8"))
   checked=0
   for i,row in enumerate(rowset[:min(5,len(rowset))]):
    terms={word[:3] for field in fields for word in re.findall(r"[a-z0-9]+",norm(row.get(field))) if len(word)>=3}
    for term in sorted(terms)[:5]:
     group=json.loads((directory/(term[:2]+".json")).read_text(encoding="utf8"))
     assert [0,i] in group[term],(period,entity,term,i)
     checked+=1
   assert checked>0,(period,entity)
   # El cliente requiere rutas del catálogo; no se descargan meses completos.
   assert all(re.fullmatch(rf"data/partes/{entity}/{period}/[a-z0-9_-]+\.json",p) for p in paths)
   total+=1
   print("VALIDADO",period,entity,n,"consultas_positivas",checked)
 assert total==18,total
 print("BUSQUEDA_18_COMBINACIONES_OK",total)
if __name__=="__main__":check()
