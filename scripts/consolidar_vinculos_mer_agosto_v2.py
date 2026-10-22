#!/usr/bin/env python3
"""Consolida vínculos OC de agosto acreditables, sin modificar históricos/Sheets.

Lee conciliación V2 (código de proceso exacto) y evidencia documental aprobada.
Escribe un CSV MER v2 para carga controlada y un JSON de auditoría.
"""
import csv,hashlib,json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"frontend-v2/data"
OUT=DATA/"conciliacion/2026-08"
HEADER=["id_vinculo","codigo_cot","codigo_oc","origen_vinculo","estado_oc_historico","fecha_aceptacion_oc","relacion_confiable"]
def main():
 summary=json.loads((OUT/"resumen.json").read_text(encoding="utf8"))
 catalog=json.loads((DATA/"catalogo-publico.json").read_text(encoding="utf8"))
 aug=next(i for i in catalog["periodos"] if i["periodo"]=="2026-08")
 registry=json.loads((DATA/"vinculos-oc-verificados.json").read_text(encoding="utf8"))
 reference={}
 for path in aug["partes"]["ordenescompra"]:
  for oc in json.loads((ROOT/"frontend-v2"/path).read_text(encoding="utf8")):
   key=str(oc.get("codigo_oc") or "").strip()
   if key and key in reference:raise ValueError("Duplicated OC key "+key)
   if key:reference[key]=oc
 assert len(reference)==aug["conteos"]["ordenescompra"]
 entries={}; conflicts=[];counter=collections.Counter()
 def add(code,oc,origin,evidence):
  pair=(code,oc)
  row=reference.get(oc)
  if row is None:raise ValueError("OC absent in August "+oc)
  if pair in entries:
   if entries[pair]["origen_vinculo"]!=origin:counter["multiple_evidencias"]+=1
   return
  ident=hashlib.sha256((code+"|"+oc).encode("utf8")).hexdigest()
  entries[pair]={"id_vinculo":ident,"codigo_cot":code,"codigo_oc":oc,"origen_vinculo":origin,
   "estado_oc_historico":str(row.get("estado") or ""),"fecha_aceptacion_oc":str(row.get("fecha_aceptacion") or ""),
   "relacion_confiable":evidence}
 for file in sorted((OUT/"directos").glob("*.json")):
  chunk=json.loads(file.read_text(encoding="utf8"))
  for code,links in chunk.items():
   if not code.endswith('-COT26'):continue
   for x in links:
    oc=x["codigo_oc"]
    if str(reference[oc].get("codigo_proceso") or "").strip()!=code:raise ValueError("Reference mismatch "+oc)
    add(code,oc,"REFERENCIA_EXACTA_EN_CAMPO_CODIGO_PROCESO","CODIGO_PROCESO_OFICIAL")
    counter["directos"]+=1
 for item in registry["vinculos"]:
  if item.get("periodo_oc")!="2026-08" or item.get("estado_verificacion")!="confirmado_documentalmente":continue
  code=item["codigo_proceso"];oc=item["codigo_oc"]
  if reference.get(oc) is None:raise ValueError("Documented OC absent "+oc)
  if reference[oc].get("codigo_proceso") and reference[oc]["codigo_proceso"]!=code:
   conflicts.append({"codigo_oc":oc,"codigo_documental":code,"codigo_original":reference[oc]["codigo_proceso"]})
   continue
  add(code,oc,"DESCRIPCION_OFICIAL_OC_EVIDENCIA_DOCUMENTAL","DOCUMENTO_OFICIAL_VALIDADO")
  counter["documentales"]+=1
 if conflicts:raise ValueError("Conflicting documented links: "+str(conflicts))
 if counter["directos"]>summary["oc_vinculadas_exactas_con_proceso_agosto"]:
  raise ValueError("Unexpected direct link count")
 csvpath=OUT/"VinculosCOT_OC_conciliados_2026-08.csv"
 with csvpath.open("w",encoding="utf-8-sig",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=HEADER);writer.writeheader()
  writer.writerows(entries[k] for k in sorted(entries))
 result={"periodo":"2026-08","oc_revisadas":len(reference),"vinculos_exactos":counter["directos"],
  "vinculos_documentales":counter["documentales"],"vinculos_exactos_cot":counter["directos"],"vinculos_exactos_no_cot_excluidos":summary["oc_vinculadas_exactas_con_proceso_agosto"]-counter["directos"],"vinculos_consolidados_sin_duplicados":len(entries),
  "conflictos":conflicts,"candidatas_excluidas":summary["oc_candidatas_distintas"],
  "destino":"CSV MER v2 preparado, sin escritura a la Sheet histórica ni al cron",
  "sin_descripcion_oficial_en_json":True,"archivo_csv":csvpath.name,
  "estado":"PREPARADO_SOLO_LECTURA_REQUIERE_IMPORTACION_CONTROLADA"}
 (OUT/"resultado_vinculos_mer.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("VINCULOS_MER_AGOSTO_OK",json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
