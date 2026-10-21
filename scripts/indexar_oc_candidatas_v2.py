#!/usr/bin/env python3
"""Índice de OC candidatas por unidad compradora y proveedor; no asigna procesos.

Solo incluye OC AG con codigo_proceso vacío. Cada relación requiere validación
documental externa y jamás reemplaza los índices de vínculos confirmados.
"""
import argparse,hashlib,json,re,unicodedata
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
def norm(v):
 s=unicodedata.normalize("NFD",str(v or "").casefold())
 return re.sub(r"\s+"," ","".join(x for x in s if unicodedata.category(x)!="Mn")).strip()
def index(period,root=ROOT):
 if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])",period):raise ValueError("Período no válido")
 catalog=json.loads((root/"data/catalogo-publico.json").read_text())
 info=next(p for p in catalog["periodos"] if p["periodo"]==period)
 groups=defaultdict(lambda:defaultdict(list))
 count=0; candidates=0
 for rel in info["partes"]["ordenescompra"]:
  if not re.fullmatch(rf"data/partes/ordenescompra/{period}/[a-z0-9_-]+\.json",rel):raise ValueError("Fragmento inválido")
  for row in json.loads((root/rel).read_text(encoding="utf8")):
   count+=1
   code=str(row.get("codigo_oc") or "").strip()
   supplier=str(row.get("proveedor") or "").strip()
   ref=str(row.get("codigo_proceso") or "").strip()
   if ref or not re.fullmatch(r"([0-9]+)-[0-9]+-AG[0-9]{2}",code,re.I) or not norm(supplier):continue
   unit=code.split("-")[0]
   key=unit+"|"+norm(supplier)
   shard=hashlib.sha256(key.encode("utf8")).hexdigest()[:2]
   groups[shard][key].append([code,supplier,row.get("monto_total_oc_clp"),row.get("estado"),row.get("fecha_creacion")])
   candidates+=1
 if count!=info["conteos"]["ordenescompra"]:raise ValueError("Conteo diferente al catálogo")
 out=root/"data"/"oc-candidatas"/period;out.mkdir(parents=True,exist_ok=True)
 for shard,contents in groups.items():
  (out/(shard+".json")).write_text(json.dumps(contents,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 meta={"version":1,"periodo":period,"oc_examinadas":count,"oc_candidatas_ag_sin_referencia":candidates,"shards":len(groups),"clave":"unidad|proveedor_normalizado","estado":"candidata_no_verificada"}
 (out/"meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("OC_CANDIDATAS_OK",period,count,candidates,len(groups))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--periodo",required=True);a=p.parse_args();index(a.periodo)
