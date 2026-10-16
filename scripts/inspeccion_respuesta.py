"""Inspección segura de la respuesta JSON de Compra Ágil V2."""
import json
import os
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "https://api2.mercadopublico.cl/v2/compra-agil"
ticket = os.environ.get("CHILECOMPRA_TICKET")
if not ticket:
    raise SystemExit("Falta el secreto CHILECOMPRA_TICKET")

tests = [
    ("listado", BASE + "?ttl_cambio_ms=300000"),
    ("detalle_otro", BASE + "/1549-3882-COT26"),
]
for label, url in tests:
    start = time.monotonic()
    try:
        with urlopen(Request(url, headers={"ticket": ticket, "Accept": "application/json"}), timeout=30) as response:
            raw = response.read(1500000)
            data = json.loads(raw)
            print(label, "HTTP", response.status, "segundos", round(time.monotonic()-start, 2), flush=True)
            print(label, "tipo_raiz", type(data).__name__, flush=True)
            if isinstance(data, dict):
                print(label, "claves_raiz", json.dumps(list(data.keys()), ensure_ascii=False), flush=True)
                for k, v in list(data.items())[:12]:
                    if isinstance(v, list):
                        print(label, "lista", k, "cantidad", len(v), flush=True)
                        if v and isinstance(v[0], dict):
                            print(label, "claves_primera_fila", json.dumps(list(v[0].keys()), ensure_ascii=False), flush=True)
                    elif isinstance(v, dict):
                        print(label, "objeto", k, "claves", json.dumps(list(v.keys()), ensure_ascii=False), flush=True)
            elif isinstance(data, list):
                print(label, "filas", len(data), flush=True)
                if data and isinstance(data[0], dict):
                    print(label, "claves_primera_fila", json.dumps(list(data[0].keys()), ensure_ascii=False), flush=True)
    except HTTPError as e:
        print(label, "HTTP", e.code, "segundos", round(time.monotonic()-start, 2), flush=True)
    except (URLError, TimeoutError, ValueError) as e:
        print(label, "error", type(e).__name__, "segundos", round(time.monotonic()-start, 2), flush=True)
