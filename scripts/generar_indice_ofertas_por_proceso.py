#!/usr/bin/env python3
"""Índice compacto por código de proceso y mes; derivado de fragmentos públicos.
No modifica los fragmentos originales ni los procesos protegidos.
"""
import argparse, json, re, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"

def money(value):
    if value is None or not str(value).strip():return None
    try:
        n=float(str(value).strip().replace(".","").replace(",","."))
        return round(n) if 0<=n<=1e15 else None
    except (ValueError, OverflowError):return None

def generate(month,root=ROOT):
    if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])",month):raise ValueError("mes no válido")
    catalog=json.loads((root/"data/catalogo-publico.json").read_text(encoding="utf-8"))
    entry=next(x for x in catalog["periodos"] if x["periodo"]==month)
    grouped={};missing=0;total=0;seen=set()
    paths=entry["partes"]["ofertas"]
    for rel in paths:
        if not re.fullmatch(rf"data/partes/ofertas/{month}/[a-z0-9_-]+\.json",rel):raise ValueError("ruta no válida")
        for row in json.loads((root/rel).read_text(encoding="utf-8")):
            total+=1
            code=str(row.get("codigo") or "").strip().upper()
            if not code:continue
            id_=str(row.get("id_cotizacion") or "").strip()
            if not id_:
                missing+=1
                grouped.setdefault(code,{"n":0,"c":0,"m":0,"s":0})["s"]+=1
                continue
            key=(code,id_)
            if key in seen:continue
            seen.add(key)
            rec=grouped.setdefault(code,{"n":0,"c":0,"m":0,"s":0})
            rec["n"]+=1
            amount=money(row.get("monto_ofertado_clp"))
            if amount is not None:
                rec["c"]+=1
                rec["m"]+=amount
    if total!=entry["conteos"]["ofertas"]:raise ValueError(f"Conteo de ofertas: {total} != {entry['conteos']['ofertas']}")
    out=root/"data/analitica-ofertas"/month
    out.mkdir(parents=True,exist_ok=True)
    shards={}
    for code,stats in grouped.items():
        key=hashlib.sha256(code.encode("utf-8")).hexdigest()[:2]
        shards.setdefault(key,{})[code]=stats
    for key,data in shards.items():
        (out/(key+".json")).write_text(json.dumps(data,ensure_ascii=False,separators=(",",":"),sort_keys=True),encoding="utf-8")
    meta={"version":1,"periodo":month,"fuente_conteos":total,"codigos":len(grouped),"shards":sorted(shards),"sin_id":missing}
    (out/"meta.json").write_text(json.dumps(meta,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print("INDICE_OFERTAS_OK",month,total,len(grouped),len(shards),missing)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--periodo",required=True)
    args=parser.parse_args()
    generate(args.periodo)
