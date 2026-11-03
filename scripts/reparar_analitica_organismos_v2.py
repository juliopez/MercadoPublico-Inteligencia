#!/usr/bin/env python3
"""Reparar agregados de organismos ausentes/desfasados de TODOS los períodos públicos.

Fuente: fragmentos publicados en frontend-v2/data/partes/procesos.
No descarga ZIP, ni escribe Sheets, ni altera el ETL protegido.
"""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"frontend-v2/data"

def get_generator():
    spec=importlib.util.spec_from_file_location("analitica_mer",ROOT/"scripts/generar_analitica_v2.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def valid(agg,period,expected):
    if not isinstance(agg,dict):return False
    if agg.get("periodo")!=period or agg.get("entidad")!="procesos":return False
    if agg.get("registros")!=expected:return False
    if not isinstance(agg.get("organismos_procesos_unicos"),list):return False
    if not isinstance(agg.get("procesos_unicos"),int):return False
    if not isinstance(agg.get("modalidades_unicas"),dict):return False
    if agg["procesos_unicos"]>expected or agg["procesos_unicos"]<0:return False
    if sum(int(x.get("procesos",0)) for x in agg["organismos_procesos_unicos"])!=agg["procesos_unicos"]:
        return False
    return True

def run(data=DATA,dry_run=False):
    catalog=json.loads((data/"catalogo-publico.json").read_text(encoding="utf-8"))
    periods=catalog.get("periodos",[])
    if not isinstance(periods,list) or not periods:raise ValueError("Catálogo sin períodos")
    seen=set()
    generator=get_generator()
    changed=[]
    for entry in sorted(periods,key=lambda x:x["periodo"]):
        period=entry["periodo"]
        if period in seen:raise ValueError("Período duplicado: "+period)
        seen.add(period)
        count=entry["conteos"]["procesos"]
        if not isinstance(count,int) or count<0:raise ValueError("Conteo de procesos incompatible")
        output=data/"analitica"/period/"procesos.json"
        current=None
        if output.is_file():
            try:current=json.loads(output.read_text(encoding="utf-8"))
            except (ValueError,UnicodeError):pass
        if valid(current,period,count):
            print("ANALITICA_ORGANISMOS_VIGENTE",period,count,flush=True)
            continue
        print("ANALITICA_ORGANISMOS_REGENERAR",period,count,flush=True)
        changed.append(period)
        if dry_run:continue
        generator.build(period,"procesos",root=data.parent)
        produced=json.loads(output.read_text(encoding="utf-8"))
        if not valid(produced,period,count):
            raise ValueError("Agregado de organismos inválido tras reconstrucción: "+period)
        print("ANALITICA_ORGANISMOS_VERIFICADA",period,produced["procesos_unicos"],flush=True)
    print("PERIODOS_REGENERADOS",",".join(changed) if changed else "NINGUNO")
    return changed

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--simular",action="store_true",help="Solo diagnosticar, sin escritura")
    args=ap.parse_args()
    run(dry_run=args.simular)
