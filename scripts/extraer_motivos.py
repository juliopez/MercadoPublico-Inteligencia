"""Inspección acotada de motivos de selección en Compra Ágil V2."""
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ticket = os.environ.get("CHILECOMPRA_TICKET")
if not ticket:
    raise SystemExit("Falta CHILECOMPRA_TICKET")
codes = ["425-325-COT26", "2927-370-COT26"]
output = Path("output/motivos")
output.mkdir(parents=True, exist_ok=True)
rows = []
for code in codes:
    url = "https://api2.mercadopublico.cl/v2/compra-agil?" + urlencode({"id": code})
    request = Request(url, headers={"ticket": ticket, "Accept": "application/json"})
    with urlopen(request, timeout=35) as response:
        data = json.load(response)
    items = (data.get("payload") or {}).get("items") or []
    if len(items) != 1 or items[0].get("codigo") != code:
        raise ValueError("Resultado inesperado para " + code)
    item = items[0]
    motivos = item.get("motivos") or {}
    estado = item.get("estado") or {}
    row = {
        "codigo": code,
        "estado": estado.get("codigo"),
        "motivo_seleccion": motivos.get("motivo_seleccion"),
        "ofertas_recibidas": (item.get("resumen") or {}).get("total_ofertas_recibidas"),
        "fuente": "API Compra Agil V2 - listado por id"
    }
    rows.append(row)
    print(code, "estado", row["estado"], "motivo_informado", bool(row["motivo_seleccion"]), flush=True)
(output / "motivos.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print("Procesos examinados:", len(rows), flush=True)
