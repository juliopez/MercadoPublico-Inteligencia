#!/usr/bin/env python3
"""Auditoría reproducible de vínculos Compra Ágil ↔ OC usando históricos públicos V2.

Solo lectura de fragmentos; exporta informe compacto sin cambiar datos, índices ni ETL.
"""
import argparse, collections, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
def audit(code,root=ROOT):
 if not re.fullmatch(r"[A-Za-z0-9-]{5,80}",code):raise ValueError("Código inválido")
 catalog=json.loads((root/"data/catalogo-publico.json").read_text(encoding="utf8"))
 processes=[];offers=[];results=[];ocs=[];empty_refs=collections.Counter();same_unit=[];selected_names=set();award_names=set()
 order_codes=collections.Counter();total_oc=0;oc_by_process=collections.Counter()
 for item in catalog["periodos"]:
  period=item["periodo"]
  for entity,field,dest in [("procesos","codigo",processes),("ofertas","codigo",offers),("resultados","codigo",results),("ordenescompra","codigo_proceso",ocs)]:
   count=0
   for rel in item["partes"].get(entity,[]):
    if not re.fullmatch(rf"data/partes/{entity}/{period}/[a-z0-9_-]+\.json",rel):raise ValueError("Ruta de fragmento inválida")
    rows=json.loads((root/rel).read_text(encoding="utf8"))
    if not isinstance(rows,list):raise ValueError("Fragmento inválido")
    count+=len(rows)
    for rec in rows:
     if entity=="ordenescompra":
      total_oc+=1
      ref=str(rec.get(field) or "").strip()
      if not ref:empty_refs[period]+=1
      if ref:oc_by_process[ref]+=1
      oc_code=str(rec.get("codigo_oc") or "")
      if oc_code:order_codes[oc_code.split("-")[-1]]+=1
      if oc_code.startswith(code.split('-')[0]+'-') and oc_code.endswith('-AG26'):
       same_unit.append({'periodo':period,'codigo_oc':oc_code,'proveedor':rec.get('proveedor'),'codigo_proceso':rec.get('codigo_proceso'),'monto_total_oc_clp':rec.get('monto_total_oc_clp')})
     if str(rec.get(field) or "").strip()==code:
      if entity=='resultados' and rec.get('adjudicatario'):award_names.add(str(rec['adjudicatario']).strip().casefold())
      if entity=='ofertas' and str(rec.get('seleccionado') or '').lower() in ('si','sí','true','1'):selected_names.add(str(rec.get('proveedor') or '').strip().casefold())
      sample={"periodo":period,"codigo":rec.get("codigo_oc") if entity=="ordenescompra" else rec.get("codigo"),"proveedor":rec.get("proveedor") if entity in ("ofertas","ordenescompra") else None,"estado":rec.get("estado") if entity in ("procesos","ordenescompra") else None}
      dest.append(sample)
   if count!=item["conteos"][entity]:raise ValueError(f"Conteo distinto: {period} {entity}: {count}")
 # La identidad seleccionada permite candidatos, no vinculación probada.
 selected={str(x.get("proveedor") or "").strip().casefold() for x in offers if x.get("proveedor")}
 result_providers={str(x.get("adjudicatario") or "").strip().casefold() for x in results if x.get("adjudicatario")}
 matched_exact=sorted(selected & result_providers)
 report={
  "version":1,"codigo_proceso":code,"periodos_consultados":[x["periodo"] for x in catalog["periodos"]],
  "registros_oc_escaneados":total_oc,"oc_codigo_proceso_vacio_por_mes":dict(empty_refs),
  "distribucion_sufijo_oc":order_codes.most_common(12),
  "caso":{"procesos":processes,"ofertas":len(offers),"resultados":len(results),"ordenes_compra_enlazadas_exactamente":ocs,"proveedores_ofertantes_distintos":len(selected),"coincidencia_nombre_oferente_resultado":matched_exact},
  "otros_codigos_referencia":len(oc_by_process),
  "ofertas_marcadas_seleccionadas":sorted(selected_names),"resultados_adjudicatarios_informados":sorted(award_names),
  "oc_ag26_misma_unidad_compradora":len(same_unit),
  "candidatas_por_misma_unidad_y_proveedor": [x for x in same_unit if str(x['proveedor'] or '').strip().casefold() in (selected_names|award_names)][:40],
  "nota_candidatas":"Las candidatas por unidad/proveedor NO prueban vínculo ni adjudicación; deben compararse fechas, montos y registro oficial.",
  "conclusion":("Vinculación exacta en históricos" if ocs else "NO se encontró coincidencia exacta en codigo_proceso; no demuestra ausencia de OC oficial"),
  "limitaciones":["Solo períodos publicados en V2","No se verificó estado externo ni API oficial de OC","La selección de proveedor no confirma emisión de OC","Identificación por nombres no identifica legalmente a una empresa","No se examinan documentos PDF ni notas descriptivas fuera de los campos públicos"],
  "acciones_recomendadas":["Consultar ficha Compra Ágil en portal oficial para identificar código OC público o id_oc","Buscar OC por código oficial y contrastar proveedor, organismo, importe y fechas","Si OC está en históricos con otra referencia, corregir mapeo en transformador y regenerar índice conservando respaldo; no crear enlaces por similitud sin evidencia","En UI preferir 'No encontrada en históricos consultados' a 'No existe OC'"]
 }
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--codigo",default="839-4-COT26");p.add_argument("--salida",default="docs/auditorias/AUDITORIA_VINCULO_839-4-COT26_2026-10-21.json")
 a=p.parse_args();result=audit(a.codigo);out=Path(a.salida);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("AUDITORIA_VINCULO_OC_OK",a.codigo,len(result["caso"]["ordenes_compra_enlazadas_exactamente"]),result["registros_oc_escaneados"])
