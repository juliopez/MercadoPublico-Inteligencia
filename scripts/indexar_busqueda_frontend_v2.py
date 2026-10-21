#!/usr/bin/env python3
"""Prepara un índice de búsqueda público por período/entidad desde fragmentos V2.

El índice no contiene filas completas ni identificadores internos. Se divide
en 64 particiones según el identificador de registro y se genera fuera de Sheets.
No modificar la carga del frontend hasta publicar y validar índices completos.
"""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "frontend-v2"
FIELDS = {
    "procesos": ("codigo", "nombre", "organismo_comprador"),
    "ofertas": ("codigo", "proveedor"),
    "resultados": ("codigo", "adjudicatario"),
    "ordenescompra": ("codigo_oc", "codigo_proceso", "proveedor"),
}
SHARDS = 64

def normalize(value):
    text = unicodedata.normalize("NFD", str(value or "").casefold())
    return re.sub(r"\s+", " ", "".join(c for c in text if unicodedata.category(c) != "Mn")).strip()

def build(period, entity, root=ROOT):
    if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])", period):
        raise ValueError("Período inválido")
    if entity not in FIELDS:
        raise ValueError("Entidad inválida")
    manifest = json.loads((root / "data/catalogo-publico.json").read_text(encoding="utf-8"))
    entry = next((x for x in manifest["periodos"] if x["periodo"] == period), None)
    if entry is None:
        raise ValueError("Período no publicado")
    parts = entry.get("partes", {}).get(entity)
    expected = entry.get("conteos", {}).get(entity)
    if not isinstance(parts, list) or not isinstance(expected, int):
        raise ValueError("Entidad incompleta en el manifiesto")
    output = root / "data" / "busqueda" / period / entity
    output.mkdir(parents=True, exist_ok=True)
    buckets = {}
    count = 0
    for part_id, relative in enumerate(parts):
        if not re.fullmatch(rf"data/partes/{entity}/{period}/[a-z0-9_-]+\\.json", relative):
            raise ValueError("Ruta inválida: " + relative)
        records = json.loads((root / relative).read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError("Fragmento inválido")
        for row_id, record in enumerate(records):
            search = normalize(" ".join(str(record.get(field) or "") for field in FIELDS[entity]))
            keys = {word[:3] for word in re.findall(r"[a-z0-9]+", search) if len(word) >= 3}
            for key in keys:
                buckets.setdefault(key, []).append([part_id, row_id, search])
            count += 1
    if count != expected:
        raise ValueError(f"Conteo discordante: {count} != {expected}")
    for key, rows in buckets.items():
        (output / f"{key}.json").write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + "\\n", encoding="utf-8")
    meta = {"version": 1, "periodo": period, "entidad": entity, "conteo": count,
            "fragmentos": len(parts), "tipo": "prefijo_palabra", "longitud_prefijo": 3,
            "particiones": len(buckets), "campos": list(FIELDS[entity])}
    (output / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print("BUSQUEDA_INDICE_OK", period, entity, count, len(buckets))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--periodo", required=True)
    parser.add_argument("--entidad", choices=sorted(FIELDS), required=True)
    arguments = parser.parse_args()
    build(arguments.periodo, arguments.entidad)
