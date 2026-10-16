"""Diagnóstico acotado del vínculo CA-OC documentado, sin exponer valores sensibles."""
import os, json, time
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ticket=os.environ.get("CHILECOMPRA_TICKET","")
if not ticket: raise SystemExit("Falta CHILECOMPRA_TICKET")
codes=("2284-520-COT26","425-325-COT26")
for code in codes:
    url="https://api2.mercadopublico.cl/v2/compra-agil/"+code
    t=time.monotonic()
    try:
        with urlopen(Request(url,headers={"ticket":ticket,"Accept":"application/json"}),timeout=35) as response:
            data=json.load(response)
        payload=data.get("payload") or {}
        oc=payload.get("orden_compra") or {}
        selected=payload.get("proveedores_cotizando") or []
        ocid=payload.get("id_orden_compra") or oc.get("id_orden_compra") or oc.get("id_oc")
        print("codigo",code,"HTTP",response.status,"duracion",round(time.monotonic()-t,2),flush=True)
        print("campos_payload",json.dumps(list(payload.keys()),ensure_ascii=False),flush=True)
        print("orden_id_presente",bool(ocid),"cotizaciones",len(selected),flush=True)
        if selected and isinstance(selected[0],dict):
            print("campos_cotizacion",json.dumps(list(selected[0].keys()),ensure_ascii=False),flush=True)
            print("cantidad_marcadas_ganadoras",sum(x.get("proveedor_seleccionado") in (1,True) for x in selected),flush=True)
    except HTTPError as e:
        print("codigo",code,"HTTP",e.code,"duracion",round(time.monotonic()-t,2),flush=True)
    except (URLError,TimeoutError,ValueError) as e:
        print("codigo",code,"error",type(e).__name__,"duracion",round(time.monotonic()-t,2),flush=True)
