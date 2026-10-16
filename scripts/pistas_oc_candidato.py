"""Búsqueda prudente de OC candidatas a partir del proveedor seleccionado.

No equipara coincidencias a validaciones documentales y no actualiza resultados.
"""
import json, os, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

TICKET=os.getenv("CHILECOMPRA_TICKET","").strip()
if not TICKET: raise SystemExit("Falta CHILECOMPRA_TICKET")
CODE="2284-520-COT26"
API_CA="https://api2.mercadopublico.cl/v2/compra-agil/"
API_OC="https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
def fetch(url,headers):
    with urlopen(Request(url,headers=headers),timeout=40) as res: return json.load(res)
try:
    data=fetch(API_CA+CODE,{"ticket":TICKET,"Accept":"application/json"})
    p=data.get("payload") or {}
    if p.get("codigo")!=CODE: raise ValueError("Respuesta de otro proceso")
    selected=[o for o in p.get("proveedores_cotizando",[]) if o.get("proveedor_seleccionado") in (True,1,"1")]
    print("ofertas_seleccionadas",len(selected),flush=True)
    if len(selected)!=1: raise SystemExit("Sin seleccion unica: no avanzar")
    offer=selected[0]
    print("codigo_empresa_presente",bool(offer.get("codigo_empresa")),flush=True)
    print("id_oc_interno_presente",bool(offer.get("id_oc")),flush=True)
    print("campos_fechas",list((p.get("fechas") or {}).keys()),flush=True)
    print("campos_institucion",list((p.get("institucion") or {}).keys()),flush=True)
    # No se consulta masivamente sin identificar una fecha oficial de envío de OC.
except HTTPError as error:
    print("respuesta_http",error.code,flush=True)
except (URLError,TimeoutError,ValueError) as error:
    print("error",type(error).__name__,flush=True)
