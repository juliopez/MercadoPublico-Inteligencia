import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ticket = os.environ.get("CHILECOMPRA_TICKET")
if not ticket:
    raise SystemExit("Falta CHILECOMPRA_TICKET")

base = "https://api2.mercadopublico.cl/v2/compra-agil"
params = {
    "publicado_desde": "2026-10-01T00:00:00",
    "publicado_hasta": "2026-10-07T23:59:59",
    "q": "capacitacion",
    "tamano_pagina": 10,
    "numero_pagina": 1,
}
url = base + "?" + urlencode(params)
start = time.monotonic()
try:
    with urlopen(Request(url, headers={"ticket": ticket, "Accept": "application/json"}), timeout=35) as response:
        data = json.load(response)
        print("http_status", response.status)
        print("duracion_segundos", round(time.monotonic()-start,2))
        print("success", str(data.get("success")))
        payload = data.get("payload") or {}
        items = payload.get("items") or []
        paging = payload.get("paginacion") or {}
        print("cantidad_items", len(items))
        print("paginacion", json.dumps(paging, ensure_ascii=False))
        if items and isinstance(items[0], dict):
            first = items[0]
            print("campos_item", json.dumps(list(first.keys()), ensure_ascii=False))
            for key, val in first.items():
                if isinstance(val,dict):
                    print("subobjeto", key, json.dumps(list(val.keys()), ensure_ascii=False))
                elif isinstance(val,list):
                    print("sublista", key, "longitud", len(val))
        else:
            print("sin_items; revisar filtros o respuesta errors")
            print("numero_errores",len(data.get("errors") or []))
except HTTPError as error:
    print("http_status", error.code, "duracion_segundos", round(time.monotonic()-start,2))
except (URLError, TimeoutError) as error:
    print("error_conexion",type(error).__name__,round(time.monotonic()-start,2))
