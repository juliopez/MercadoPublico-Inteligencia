"""Diagnóstico de API clásica de órdenes de compra, sin publicar datos de proveedores."""
import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ticket = os.environ.get("CHILECOMPRA_TICKET")
if not ticket:
    raise SystemExit("Falta CHILECOMPRA_TICKET")
base = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
params = {"fecha": "07102026", "ticket": ticket}
url = base + "?" + urlencode(params)
started = time.monotonic()
try:
    with urlopen(Request(url, headers={"Accept": "application/json"}), timeout=40) as response:
        body = json.load(response)
    print("http_status",response.status,"segundos",round(time.monotonic()-started,2),flush=True)
    print("tipo_raiz",type(body).__name__,flush=True)
    if isinstance(body, dict):
        print("campos_raiz",json.dumps(list(body.keys()),ensure_ascii=False),flush=True)
        print("cantidad_declarada",body.get("Cantidad"),flush=True)
        items=body.get("Listado") or []
        print("registros_listado",len(items),flush=True)
        if items and isinstance(items[0], dict):
            print("campos_orden",json.dumps(list(items[0].keys()),ensure_ascii=False),flush=True)
            for k,v in items[0].items():
                if isinstance(v,dict):
                    print("subobjeto",k,json.dumps(list(v.keys()),ensure_ascii=False),flush=True)
except HTTPError as e:
    print("http_status",e.code,"segundos",round(time.monotonic()-started,2),flush=True)
except (URLError,TimeoutError,ValueError) as e:
    print("error",type(e).__name__,"segundos",round(time.monotonic()-started,2),flush=True)
