"""Diagnóstico responsable de órdenes: una consulta, registro de estado y sin reintentos automáticos."""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
INTERNAL_ID = "55348066"  # ID interno de Compra Ágil: NO es código público de OC verificado.
PUBLIC_CODE = os.getenv("CODIGO_OC_PUBLICO", "").strip()
TOKEN = os.getenv("CHILECOMPRA_TICKET", "").strip()
OUT = Path("output/trazabilidad")
if not TOKEN:
    raise SystemExit("CHILECOMPRA_TICKET no configurado")
OUT.mkdir(parents=True, exist_ok=True)
event = {
    "fecha_consulta_utc": datetime.now(timezone.utc).isoformat(),
    "endpoint": "ordenesdecompra.json",
    "id_oc_interno": INTERNAL_ID,
    "codigo_oc_publico": PUBLIC_CODE or None,
    "codigo_oc_verificado": False,
    "respuesta_http": None,
    "retry_after": None,
    "resultado": "sin_consulta"
}
if not PUBLIC_CODE:
    event["resultado"] = "pendiente_codigo_publico"
    print("No se realiza consulta: falta CODIGO_OC_PUBLICO verificado.", flush=True)
else:
    url = API + "?" + urlencode({"codigo": PUBLIC_CODE, "ticket": TOKEN})
    start = time.monotonic()
    try:
        with urlopen(Request(url, headers={"Accept": "application/json"}), timeout=30) as response:
            data = json.load(response)
            event["respuesta_http"] = response.status
            orders = data.get("Listado") or []
            event["ordenes_encontradas"] = len(orders)
            event["resultado"] = "respuesta_recibida_sin_validar_asociacion"
            if len(orders) == 1 and orders[0].get("Codigo") == PUBLIC_CODE:
                event["codigo_oc_verificado"] = True
                event["resultado"] = "codigo_oc_encontrado"
                event["codigo_licitacion_informado"] = bool(orders[0].get("CodigoLicitacion"))
    except HTTPError as err:
        event["respuesta_http"] = err.code
        if err.code == 429:
            event["retry_after"] = err.headers.get("Retry-After")
            event["resultado"] = "limite_api_no_reintentar"
        else:
            event["resultado"] = "error_http"
    except (URLError, TimeoutError, ValueError) as err:
        event["resultado"] = type(err).__name__
    event["duracion_segundos"] = round(time.monotonic()-start, 2)
(OUT / "trazabilidad.json").write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(event, ensure_ascii=False), flush=True)
