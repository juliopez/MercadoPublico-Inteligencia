"""Extrae ofertas de un proceso real; conserva resultados solo como artefacto temporal."""
import csv
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

CODE = "2284-520-COT26"
ticket = os.environ.get("CHILECOMPRA_TICKET")
if not ticket:
    raise SystemExit("Falta CHILECOMPRA_TICKET")
url = "https://api2.mercadopublico.cl/v2/compra-agil/" + CODE
with urlopen(Request(url, headers={"ticket": ticket, "Accept": "application/json"}), timeout=50) as resp:
    body = json.load(resp)
payload = body.get("payload") or {}
if payload.get("codigo") != CODE:
    raise SystemExit("Código inesperado: se omite exportación")
offers = payload.get("proveedores_cotizando") or []
if not offers:
    raise SystemExit("Respuesta sin ofertas: revisar endpoint")
columns = ["codigo", "id_cotizacion", "razon_social", "rut_proveedor",
           "valor_neto", "total_impuesto", "monto_despacho", "monto_total",
           "proveedor_seleccionado", "id_oc", "estado"]
directory = Path("output/ofertas")
directory.mkdir(parents=True, exist_ok=True)
with (directory / "ofertas_piloto.csv").open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
    writer.writeheader()
    for offer in offers:
        writer.writerow({key:CODE if key == "codigo" else offer.get(key) for key in columns})
metadata = {
    "codigo": CODE,
    "cantidad_ofertas": len(offers),
    "id_orden_compra_presente": bool(payload.get("id_orden_compra")),
    "campo_seleccion_informado": sum(o.get("proveedor_seleccionado") is not None for o in offers),
    "marcados_seleccionados": sum(o.get("proveedor_seleccionado") in (True, 1, "1") for o in offers),
    "ofertas_con_monto_total": sum(o.get("monto_total") is not None for o in offers),
}
(directory / "control.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(metadata,ensure_ascii=False),flush=True)
