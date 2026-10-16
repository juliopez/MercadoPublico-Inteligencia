"""Prueba de rutas alternativas de Compra Ágil, sin exponer tickets ni datos de proveedores."""
import os
import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

TOKEN = os.environ.get("CHILECOMPRA_TICKET", "")
if not TOKEN:
    raise SystemExit("Configurar CHILECOMPRA_TICKET en GitHub Actions Secrets")
BASE = "https://api2.mercadopublico.cl/v2/compra-agil"
CASES = [
    ("listado_por_id", BASE + "?" + urlencode({"id":"425-325-COT26","tamano_pagina":10,"numero_pagina":1})),
    ("listado_seleccionados", BASE + "?" + urlencode({
        "publicado_desde":"2026-10-01T00:00:00",
        "publicado_hasta":"2026-10-07T23:59:59",
        "estado":"proveedor_seleccionado","q":"capacitacion",
        "tamano_pagina":10,"numero_pagina":1
    }))
]
for label, url in CASES:
    started = time.monotonic()
    try:
        with urlopen(Request(url,headers={"ticket":TOKEN,"Accept":"application/json"}),timeout=35) as response:
            data = json.load(response)
            payload = data.get("payload") or {}
            items = payload.get("items") or []
            print(label, "HTTP",response.status,"success",data.get("success"),
                  "registros",len(items),"paginacion",json.dumps(payload.get("paginacion") or {}),
                  "segundos",round(time.monotonic()-started,2),flush=True)
            if items:
                first = items[0]
                print(label,"campos_item",json.dumps(list(first.keys()),ensure_ascii=False),flush=True)
                print(label,"campos_motivos",json.dumps(list((first.get("motivos") or {}).keys()),ensure_ascii=False),flush=True)
    except HTTPError as error:
        print(label,"HTTP",error.code,"segundos",round(time.monotonic()-started,2),flush=True)
    except (URLError,TimeoutError,ValueError) as error:
        print(label,"error",type(error).__name__,"segundos",round(time.monotonic()-started,2),flush=True)
    time.sleep(2)
