#!/usr/bin/env python3
"""Conciliación multientidad para junio, julio y septiembre 2026, sobre históricos V2.
Relaciones exactas y candidatas separadas; nunca presume confirmación por similitud.
"""
import argparse,collections,hashlib,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
PERIOD="2026-08"
def norm(v):
 s=unicodedata.normalize("NFD",str(v or "").casefold())
 return re.sub(r"\s+"," ","".join(c for c in s if unicodedata.category(c)!="Mn")).strip()
def rows(meta,entity):
 for path in meta["partes"][entity]:
  if not re.fullmatch(rf"data/partes/{entity}/{meta['periodo']}/[a-z0-9_-]+\.json",path):raise ValueError("Ruta inesperada")
  for record in json.loads((ROOT/path).read_text(encoding="utf8")):yield record
def main():
 global PERIOD
 parser=argparse.ArgumentParser(description="Conciliación multientidad de OC, sin cambios en MER")
 parser.add_argument("--periodo",required=True,choices=["2026-06","2026-07","2026-09"])
 PERIOD=parser.parse_args().periodo
 cat=json.loads((ROOT/"data/catalogo-publico.json").read_text())
 meta=next(x for x in cat["periodos"] if x["periodo"]==PERIOD)
 processes={};selected=collections.defaultdict(set);award=collections.defaultdict(set)
 count=collections.Counter()
 # Consolidar actores y procesos de todos los meses publicados; OC objetivo solo agosto.
 process_months=collections.defaultdict(set)
 for entry in cat["periodos"]:
  month=entry["periodo"]
  for row in rows(entry,"procesos"):
   if month==PERIOD:count["procesos"]+=1
   code=str(row.get("codigo") or "").strip()
   if code:
    processes[code]=row
    process_months[code].add(month)
  for row in rows(entry,"ofertas"):
   if month==PERIOD:count["ofertas"]+=1
   code=str(row.get("codigo") or "").strip()
   if code and norm(row.get("seleccionado")) in ("si","true","1"):
    selected[code].add(norm(row.get("proveedor")))
  for row in rows(entry,"resultados"):
   if month==PERIOD:count["resultados"]+=1
   code=str(row.get("codigo") or "").strip()
   if code and row.get("adjudicatario"):award[code].add(norm(row["adjudicatario"]))
 # Clasificamos toda OC exactamente una vez, conservando evidencias separadas.
 direct=[];possible=[];unlinked=collections.Counter();repeated=collections.Counter()
 # Índice reducido por unidad y proveedor, solo para procesos CA con selección informada.
 lookup=collections.defaultdict(set)
 for code,row in processes.items():
  if not re.fullmatch(r"[0-9]+-[0-9]+-COT[0-9]{2}",code,re.I):continue
  unit=code.split("-")[0]
  for provider in selected.get(code,set())|award.get(code,set()):
   if provider:lookup[(unit,provider)].add(code)
 for oc in rows(meta,"ordenescompra"):
  count["ordenescompra"]+=1
  oc_code=str(oc.get("codigo_oc") or "").strip()
  process=str(oc.get("codigo_proceso") or "").strip()
  provider=norm(oc.get("proveedor"))
  if process:
   if process in processes:direct.append([process,oc_code,"coincidencia_exacta_codigo_proceso",PERIOD])
   else:unlinked["con_referencia_fuera_procesos_publicados"]+=1
   continue
  unlinked["sin_codigo_proceso"]+=1
  if not re.fullmatch(r"[0-9]+-[0-9]+-AG[0-9]{2}",oc_code,re.I):continue
  matches=sorted(lookup.get((oc_code.split("-")[0],provider),set()))
  if matches:
   reason="unico_candidato_por_unidad_y_proveedor" if len(matches)==1 else "ambiguo_varios_procesos"
   for code in matches:possible.append([code,oc_code,reason,PERIOD])
   if len(matches)>1:repeated["oc_ambiguas"]+=1
  else:unlinked["ag_sin_candidato_proveedor"]+=1
 for entity in ("procesos","ofertas","resultados","ordenescompra"):
  if count[entity]!=meta["conteos"][entity]:raise ValueError(f"Conteo no concilia {entity}")
 out=ROOT/"data/conciliacion"/PERIOD;out.mkdir(parents=True,exist_ok=True)
 # Proteger la estructura original y crear archivos pequeños por prefijo de proceso.
 for label,items in (("directos",direct),("candidatos",possible)):
  buckets=collections.defaultdict(lambda:collections.defaultdict(list))
  for code,oc,reason,month in items:
   shard=hashlib.sha256(code.encode()).hexdigest()[:2]
   buckets[shard][code].append({"codigo_oc":oc,"periodo_oc":month,"tipo":reason})
  target=out/label;target.mkdir(exist_ok=True)
  for shard,d in buckets.items():
   (target/(shard+".json")).write_text(json.dumps(d,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 report={"version":1,"periodo":PERIOD,"totales_fuente":dict(count),"oc_vinculadas_exactas_con_proceso":len(direct),
 "oc_candidatas_relaciones":len(possible),"oc_candidatas_distintas":len({x[1] for x in possible}),
 "oc_candidatas_ambiguas":repeated["oc_ambiguas"],"procesos_de_todos_los_meses":len(processes),"diagnostico":dict(unlinked),
 "tipo_evidencia":{"directos":"codigo_proceso exacto, buscando procesos publicados junio-octubre","candidatos":"misma unidad compradora y proveedor seleccionado o en resultados, SIN verificación"},
 "limitaciones":["Se consideran procesos y selecciones publicados en todos los meses actuales; para el futuro se debe regenerar al ampliar la cobertura","No hay descripción oficial de OC en el esquema público actual","No se completan referencias vacías ni se certifican candidatos como vínculos"],
 "ejemplo_839_4_COT26":{"candidatos":[x for x in possible if x[0]=="839-4-COT26"],"directos":[x for x in direct if x[0]=="839-4-COT26"]}}
 (out/"resumen.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
 print("CONCILIACION_MULTIMES_COMPLETA",json.dumps({k:report[k] for k in ("totales_fuente","oc_vinculadas_exactas_con_proceso","oc_candidatas_distintas","oc_candidatas_ambiguas")}))
if __name__=="__main__":main()
