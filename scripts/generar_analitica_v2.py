#!/usr/bin/env python3
"""Agregados analíticos por período y entidad desde fragmentos públicos; nunca altera fuentes."""
import argparse,collections,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
ACTORS={"procesos":"organismo_comprador","ofertas":"proveedor","resultados":"adjudicatario","ordenescompra":"proveedor"}
AMOUNTS={"procesos":"monto_disponible_clp","ofertas":"monto_ofertado_clp","resultados":"monto_adjudicado_clp","ordenescompra":"monto_total_oc_clp"}
def money(value):
 if value is None or str(value).strip()=="":return None
 try:
  x=float(str(value).strip().replace(".","").replace(",","."))
  if x<0 or x>1e15:return None
  return round(x)
 except (ValueError,OverflowError):return None
def build(period,entity,root=ROOT):
 assert re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])",period) and entity in ACTORS
 catalog=json.loads((root/"data/catalogo-publico.json").read_text(encoding="utf8"))
 item=next(x for x in catalog["periodos"] if x["periodo"]==period)
 counts=collections.Counter();amounts_by_actor=collections.Counter();modality_counts=collections.Counter();total=0;with_money=0;sum_money=0
 for rel in item["partes"][entity]:
  assert re.fullmatch(rf"data/partes/{entity}/{period}/[a-z0-9_-]+\.json",rel)
  rows=json.loads((root/rel).read_text(encoding="utf8"))
  for row in rows:
   total+=1;name=str(row.get(ACTORS[entity]) or "").strip()
   if name:counts[name]+=1
   modality=str(row.get("modalidad") or row.get("tipo_oc") or "").strip()
   if modality:modality_counts[modality]+=1
   amount=money(row.get(AMOUNTS[entity]))
   if amount is not None:
    with_money+=1;sum_money+=amount
    if name:amounts_by_actor[name]+=amount
 assert total==item["conteos"][entity]
 data={"version":1,"periodo":period,"entidad":entity,"registros":total,"registros_con_monto":with_money,
       "monto_total_clp":sum_money,"actores_distintos_por_nombre":len(counts),
       "top_actores":counts.most_common(10),
       "top_actores_monto":[[name,amount] for name,amount in amounts_by_actor.most_common(10)],
       "modalidades":modality_counts.most_common(),
       "campo_monto":AMOUNTS[entity],
       "advertencia":"Son registros y sumas de importes informados; no operaciones únicas ni pagos comprobados."}
 out=root/"data/analitica"/period;out.mkdir(parents=True,exist_ok=True)
 (out/(entity+".json")).write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 print("ANALITICA_OK",period,entity,total,len(counts))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--periodo",required=True);p.add_argument("--entidad",required=True,choices=ACTORS)
 a=p.parse_args();build(a.periodo,a.entidad)
