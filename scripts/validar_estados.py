"""Valida estados de Compra Ágil mediante búsquedas puntuales por id."""
import os, json, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
base="https://api2.mercadopublico.cl/v2/compra-agil"
ticket=os.environ.get("CHILECOMPRA_TICKET")
if not ticket:
    raise SystemExit("Falta CHILECOMPRA_TICKET")
codes=["425-325-COT26","2927-370-COT26"]
for code in codes:
    started=time.monotonic()
    url=base+"?"+urlencode({"id":code})
    try:
        with urlopen(Request(url,headers={"ticket":ticket,"Accept":"application/json"}),timeout=35) as response:
            data=json.load(response)
        items=(data.get("payload") or {}).get("items") or []
        print("codigo",code,"http",response.status,"cantidad",len(items),"segundos",round(time.monotonic()-started,2))
        for item in items[:1]:
            estado=item.get("estado") or {}
            motivos=item.get("motivos") or {}
            resumen=item.get("resumen") or {}
            print("estado",json.dumps(estado,ensure_ascii=False))
            print("motivo_seleccion_informado",bool(motivos.get("motivo_seleccion")))
            print("total_ofertas_recibidas",resumen.get("total_ofertas_recibidas"))
            print("campos_adicionales",json.dumps(list(item.keys()),ensure_ascii=False))
    except HTTPError as exc:
        print("codigo",code,"http",exc.code)
    except (URLError,TimeoutError,ValueError) as exc:
        print("codigo",code,"error",type(exc).__name__)
