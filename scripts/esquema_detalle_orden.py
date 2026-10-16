"""Diagnóstico estructural de una orden de compra sin publicar sus valores."""
import os, json
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ticket=os.environ.get("CHILECOMPRA_TICKET")
if not ticket: raise SystemExit("Falta secreto CHILECOMPRA_TICKET")
base="https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
def get(params):
    url=base+"?"+urlencode(dict(params,ticket=ticket))
    with urlopen(Request(url,headers={"Accept":"application/json"}),timeout=40) as res:
        return json.load(res)
try:
    listado=get({"fecha":"07102026"})
    ordenes=listado.get("Listado") or []
    print("listado",len(ordenes),"registros")
    if not ordenes: raise SystemExit("Listado sin órdenes")
    codigo=ordenes[0].get("Codigo")
    if not codigo: raise SystemExit("Primer registro sin Codigo")
    detalle=get({"codigo":codigo})
    print("detalle_campos_raiz",list(detalle.keys()))
    datos=detalle.get("Listado") or []
    print("detalle_registros",len(datos))
    if datos and isinstance(datos[0],dict):
        print("detalle_campos",list(datos[0].keys()))
        for key, value in datos[0].items():
            if isinstance(value,dict):
                print("subobjeto",key,list(value.keys()))
            elif isinstance(value,list):
                print("sublista",key,"cantidad",len(value))
                if value and isinstance(value[0],dict):
                    print("sublista_campos",key,list(value[0].keys()))
except HTTPError as e:
    print("error_http",e.code)
except (URLError,TimeoutError,ValueError) as e:
    print("error",type(e).__name__)
