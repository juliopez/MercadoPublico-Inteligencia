#!/usr/bin/env python3
"""Audita únicamente los JSON ya guardados; no consulta la API."""
import json
from collections import Counter
from pathlib import Path

base = Path("extraccion_v2_local")
dirs = sorted(base.glob("2026-10-15_*"))
if len(dirs) != 1:
    raise SystemExit(f"Se esperaba una carpeta 2026-10-15_*, encontradas: {len(dirs)}")
folder = dirs[0]
files = sorted(folder.glob("pagina_*.json"))
if not files:
    raise SystemExit("No hay páginas JSON locales")
keys = Counter()
nested = {}
codes = []
for file in files:
    doc = json.loads(file.read_text(encoding="utf-8"))
    payload = doc["payload"]
    for item in payload["items"]:
        if not isinstance(item,dict):
            raise SystemExit(f"Elemento no es objeto: {file}")
        codes.append(str(item.get("codigo","")))
        keys.update(item.keys())
        for field,value in item.items():
            if isinstance(value,dict):
                nested.setdefault(field,Counter()).update(value.keys())
            elif isinstance(value,list):
                nested.setdefault(field,Counter()).update(["[lista]"])
print("DIRECTORIO:",folder)
print("PAGINAS:",len(files),"REGISTROS:",len(codes),"UNICOS:",len(set(codes)))
print("CAMPOS DE PRIMER NIVEL (presencia por registro):")
for k,n in sorted(keys.items()):
    print(f"  {k}: {n}/{len(codes)}")
print("SUBCAMPOS (se muestran nombres, nunca valores):")
for field,counts in sorted(nested.items()):
    print(f"  {field}: {', '.join(sorted(counts))}")
terms=("oferta","cotiza","proveedor","adjud","seleccion","monto","precio","ganador","result")
matches=[k for k in sorted(keys) if any(term in k.casefold() for term in terms)]
print("CAMPOS POTENCIALMENTE RELEVANTES PARA COTIZACIONES:",matches)
print("NOTA: ausencia de campos explícitos no demuestra ausencia de alternativas en la API.")
