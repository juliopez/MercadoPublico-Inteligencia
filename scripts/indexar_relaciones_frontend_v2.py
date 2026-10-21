#!/usr/bin/env python3
"""Índice público de fragmentos por código de proceso, sin duplicar filas ni publicar datos privados."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "frontend-v2"
TABLE_KEYS = {"ofertas": "codigo", "resultados": "codigo", "ordenescompra": "codigo_proceso"}

def build(periodo, base=ROOT):
    manifest=json.loads((base/"data/catalogo-publico.json").read_text(encoding="utf8"))
    entry=next((p for p in manifest["periodos"] if p["periodo"]==periodo),None)
    if not entry: raise ValueError("Período no publicado: "+periodo)
    indexed={}
    files_by_entity={}
    for entidad,key in TABLE_KEYS.items():
        paths=entry.get("partes",{}).get(entidad)
        if paths is None:continue
        mapping=defaultdict(list)
        files_by_entity[entidad]=paths
        for file_index,rel in enumerate(paths):
            path=base/rel
            if not path.is_file():raise ValueError("Fragmento ausente: "+rel)
            records=json.loads(path.read_text(encoding="utf8"))
            if not isinstance(records,list):raise ValueError("Fragmento inválido: "+rel)
            for code in {str(row.get(key) or "").strip() for row in records} - {""}:
                mapping[code].append(file_index)
        indexed[entidad]={code:refs for code,refs in sorted(mapping.items())}
    result={"periodo":periodo,"version":2,"archivos":files_by_entity,"entidades":indexed}
    dest=base/"data"/"indices"/(periodo+".json")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
    print("INDICE_OK",periodo,{k:len(v) for k,v in indexed.items()},dest.stat().st_size)
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--periodo",required=True)
    args=ap.parse_args()
    build(args.periodo)
