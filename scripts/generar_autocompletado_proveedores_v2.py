#!/usr/bin/env python3
"""Construye autocompletado público desde perfiles ya agregados, sin releer históricos."""
import argparse,hashlib,json,re
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
def build(period,root=ROOT):
 if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])",period):raise ValueError("Período inválido")
 catalog=json.loads((root/"data/catalogo-publico.json").read_text(encoding="utf8"))
 entry=next(p for p in catalog["periodos"] if p["periodo"]==period)
 names={}
 for entity in ("ofertas","resultados","ordenescompra"):
  if not entry["conteos"].get(entity):continue
  folder=root/"data/perfiles"/period/entity
  if not (folder/"meta.json").exists():raise ValueError(f"Falta perfil: {period} {entity}")
  for path in folder.glob("[0-9a-f][0-9a-f].json"):
   for key,item in json.loads(path.read_text(encoding="utf8")).items():
    if len(key)>=2 and key not in names:names[key]=item["nombre"]
 buckets=defaultdict(list)
 for key,name in sorted(names.items()):
  buckets[hashlib.sha256(key[:2].encode('utf8')).hexdigest()[:2]].append([key,name])
 output=root/"data/autocompletar"/period;output.mkdir(parents=True,exist_ok=True)
 for prefix,items in buckets.items():
  (output/(prefix+".json")).write_text(json.dumps(items,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 (output/"meta.json").write_text(json.dumps({"version":1,"periodo":period,"proveedores":len(names),"grupos":len(buckets)},ensure_ascii=False),encoding="utf8")
 print("AUTOCOMPLETAR_OK",period,len(names),len(buckets))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--periodo",required=True)
 a=p.parse_args();build(a.periodo)
