import json,os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
token=os.environ.get("CHILECOMPRA_TICKET")
if not token: raise SystemExit("Falta CHILECOMPRA_TICKET")
code="2284-520-COT26"
out=Path("output/validacion_oc")
out.mkdir(parents=True,exist_ok=True)
url="https://api2.mercadopublico.cl/v2/compra-agil?"+urlencode({"id":code})
with urlopen(Request(url,headers={"ticket":token}),timeout=35) as r: data=json.load(r)
items=(data.get("payload") or {}).get("items") or []
item=next((x for x in items if x.get("codigo")==code),None)
if not item: raise SystemExit("No encontrado")
print("motivo_seleccion",json.dumps((item.get("motivos") or {}).get("motivo_seleccion"),ensure_ascii=False),flush=True)
print("estado",json.dumps(item.get("estado"),ensure_ascii=False),flush=True)
base="https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
for param in [{"codigo":"55348066"},{"codigo":"2284-520-COT26"}]:
    target=base+"?"+urlencode(dict(param,ticket=token))
    try:
        with urlopen(Request(target,headers={"Accept":"application/json"}),timeout=30) as r:
            response=json.load(r)
        orders=response.get("Listado") or []
        print("consulta",list(param.keys())[0],"resultado",len(orders),"campos",list(orders[0].keys()) if orders else [],flush=True)
        if orders:
            (out/"orden_respuesta.json").write_text(json.dumps(orders,ensure_ascii=False,indent=2),encoding="utf-8")
    except HTTPError as ex:
        print("consulta",param,"http",ex.code,flush=True)
    except (URLError,TimeoutError,ValueError) as ex:
        print("consulta","error",type(ex).__name__,flush=True)
