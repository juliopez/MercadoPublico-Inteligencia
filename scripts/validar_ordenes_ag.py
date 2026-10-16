"""Muestra acotada de órdenes AG para validar referencias a Compra Ágil."""
import json,os,time
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ticket=os.environ.get("CHILECOMPRA_TICKET")
if not ticket: raise SystemExit("Falta CHILECOMPRA_TICKET")
base="https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
def consult(params):
    url=base+"?"+urlencode(dict(params,ticket=ticket))
    with urlopen(Request(url,headers={"Accept":"application/json"}),timeout=35) as response:
        return json.load(response)
listado=consult({"fecha":"07102026"}).get("Listado") or []
print("ordenes_listadas",len(listado),flush=True)
summary={"examinadas":0,"ag":0,"ag_con_codigo_licitacion":0}
for entry in listado[:25]:
    code=entry.get("Codigo")
    if not code: continue
    try:
        records=consult({"codigo":code}).get("Listado") or []
    except (HTTPError,URLError,TimeoutError,ValueError) as exc:
        print("consulta_fallida",type(exc).__name__,flush=True)
        continue
    if not records: continue
    item=records[0]
    summary["examinadas"]+=1
    if item.get("CodigoTipo")=="AG" or item.get("Tipo")=="AG":
        summary["ag"]+=1
        ref=item.get("CodigoLicitacion")
        if ref: summary["ag_con_codigo_licitacion"]+=1
        print("orden_ag","referencia_presente",bool(ref),"referencia_formato_cot",str(ref or "").endswith("-COT26"),flush=True)
    time.sleep(.3)
print("resumen",json.dumps(summary,ensure_ascii=False),flush=True)
