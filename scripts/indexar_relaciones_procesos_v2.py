#!/usr/bin/env python3
"""Índice público exacto de códigos de Procesos, por mes, fragmento y fila."""
import argparse,hashlib,json,re
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
def generate(period,root=ROOT):
 if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])",period):raise ValueError("Período incorrecto")
 catalog=json.loads((root/"data/catalogo-publico.json").read_text(encoding="utf8"))
 entry=next(e for e in catalog["periodos"] if e["periodo"]==period)
 shards=defaultdict(lambda:defaultdict(list));count=0;linked=0
 for part,path in enumerate(entry["partes"]["procesos"]):
  if not re.fullmatch(rf"data/partes/procesos/{period}/[a-z0-9_-]+\.json",path):raise ValueError("Ruta inválida")
  records=json.loads((root/path).read_text(encoding="utf8"))
  for row,record in enumerate(records):
   count+=1;code=str(record.get("codigo") or "").strip()
   if not code:continue
   shard=hashlib.sha256(code.encode("utf8")).hexdigest()[:2]
   shards[shard][code].append([part,row]);linked+=1
 if count!=entry["conteos"]["procesos"]:raise ValueError("Diferencia de registros")
 output=root/"data/relaciones-procesos"/period;output.mkdir(parents=True,exist_ok=True)
 for shard,records in shards.items():
  (output/(shard+".json")).write_text(json.dumps(records,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 meta={"version":1,"periodo":period,"registros":count,"registros_con_codigo":linked,"fragmentos":len(entry["partes"]["procesos"]),"grupos":len(shards)}
 (output/"meta.json").write_text(json.dumps(meta,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 print("INDICE_PROCESO_OK",period,count,linked,len(shards))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--periodo",required=True);generate(p.parse_args().periodo)
