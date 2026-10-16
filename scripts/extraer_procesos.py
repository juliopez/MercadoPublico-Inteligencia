"""Extraer una muestra paginada y normalizar procesos de Compra Ágil."""
import csv
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api2.mercadopublico.cl/v2/compra-agil"
TOKEN = os.environ.get("CHILECOMPRA_TICKET", "")
if not TOKEN:
    raise SystemExit("Falta configurar CHILECOMPRA_TICKET")
OUT = Path("output/historico")
OUT.mkdir(parents=True, exist_ok=True)
FIELDS = [
    "codigo", "nombre", "estado", "convocatoria", "fecha_publicacion",
    "fecha_cierre", "fecha_ultimo_cambio", "monto_disponible_clp",
    "organismo_comprador", "rut_organismo", "unidad_compra",
    "region", "total_ofertas_recibidas", "motivo_seleccion", "url_detalle"
]
items_by_code = {}
for page in range(1, 4):
    params = {
        "publicado_desde": "2026-10-01T00:00:00",
        "publicado_hasta": "2026-10-07T23:59:59",
        "q": "capacitacion",
        "tamano_pagina": 10,
        "numero_pagina": page
    }
    url = BASE + "?" + urlencode(params)
    with urlopen(Request(url, headers={"ticket": TOKEN, "Accept": "application/json"}), timeout=40) as r:
        result = json.load(r)
    if not result.get("payload"):
        raise RuntimeError("Respuesta sin payload en página " + str(page))
    payload = result["payload"]
    batch = payload.get("items") or []
    for it in batch:
        code = it.get("codigo")
        if code:
            items_by_code[code] = it
    print("pagina", page, "registros", len(batch), "unicos", len(items_by_code), flush=True)
    if not batch or page >= (payload.get("paginacion") or {}).get("total_paginas", page):
        break
    time.sleep(2)

with (OUT / "procesos.csv").open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter=";")
    writer.writeheader()
    for it in items_by_code.values():
        estado, convocatoria = it.get("estado") or {}, it.get("convocatoria") or {}
        fechas, montos = it.get("fechas") or {}, it.get("montos") or {}
        institucion, resumen = it.get("institucion") or {}, it.get("resumen") or {}
        motivos, links = it.get("motivos") or {}, it.get("links") or {}
        writer.writerow({
            "codigo": it.get("codigo"), "nombre": it.get("nombre"),
            "estado": estado.get("glosa"), "convocatoria": convocatoria.get("descripcion"),
            "fecha_publicacion": fechas.get("fecha_publicacion"),
            "fecha_cierre": fechas.get("fecha_cierre"),
            "fecha_ultimo_cambio": fechas.get("fecha_ultimo_cambio"),
            "monto_disponible_clp": montos.get("monto_disponible_clp"),
            "organismo_comprador": institucion.get("organismo_comprador"),
            "rut_organismo": institucion.get("rut"),
            "unidad_compra": institucion.get("unidad_compra"),
            "region": institucion.get("nombre_region"),
            "total_ofertas_recibidas": resumen.get("total_ofertas_recibidas"),
            "motivo_seleccion": motivos.get("motivo_seleccion"),
            "url_detalle": links.get("detalle")
        })
print("finalizado", "procesos_unicos", len(items_by_code), flush=True)
