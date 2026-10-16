import json
import os
from urllib.request import Request, urlopen

ticket = os.environ.get("CHILECOMPRA_TICKET")
if not ticket:
    raise SystemExit("CHILECOMPRA_TICKET no configurado")
url = "https://api2.mercadopublico.cl/v2/compra-agil?ttl_cambio_ms=300000"
with urlopen(Request(url, headers={"ticket":ticket,"Accept":"application/json"}),timeout=30) as response:
    result=json.load(response)
print("HTTP 200",flush=True)
payload=result.get("payload") or {}
items=payload.get("items") or []
paging=payload.get("paginacion")
print("cantidad_items",len(items),flush=True)
print("tipo_paginacion",type(paging).__name__,flush=True)
if isinstance(paging,dict):
    print("campos_paginacion",json.dumps(list(paging.keys()),ensure_ascii=False),flush=True)
if items and isinstance(items[0],dict):
    first=items[0]
    print("campos_item",json.dumps(list(first.keys()),ensure_ascii=False),flush=True)
    for key,value in first.items():
        if isinstance(value,dict):
            print("subobjeto",key,json.dumps(list(value.keys()),ensure_ascii=False),flush=True)
        elif isinstance(value,list):
            print("sublista",key,"longitud",len(value),flush=True)
            if value and isinstance(value[0],dict):
                print("sublista_campos",key,json.dumps(list(value[0].keys()),ensure_ascii=False),flush=True)
