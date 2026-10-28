#!/usr/bin/env python3
"""Read-only API field probe. Emits presence flags only; never raw records or credentials."""
import json, os, urllib.request, urllib.error
from urllib.parse import urlencode

CODES = {"compra_agil": "839-4-COT26", "licitacion": "1000-24-LE26"}
TARGETS = {
 "compra_agil": {
  "ofertas": {"id_cotizacion": "id_cotizacion", "proveedor": "razon_social",
              "monto_ofertado_clp": "monto_total", "fecha_oferta": "fecha_creacion",
              "seleccionado": "proveedor_seleccionado", "rut_proveedor_cot": "rut_proveedor"},
  "resultados": {"id_cotizacion_ganadora": "id_cotizacion",
                 "monto_oferta_seleccionada_clp": "monto_total"}
 },
 "licitacion": {"resultados": {"adjudicatario": "Nombre", "monto_adjudicado_clp": "Monto",
                              "fecha_resultado": "Fecha"}}
}
def request(url,headers):
    r=urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(r,timeout=25) as x:
            return x.status,json.load(x)
    except urllib.error.HTTPError as x:
        x.close()
        return x.code,None
    except (TimeoutError, urllib.error.URLError, ValueError):
        return "timeout_or_network",None

def exists(obj,key):
    return isinstance(obj,dict) and key in obj and obj[key] is not None and obj[key]!=""
def main():
    token=os.getenv("CHILECOMPRA_TICKET","").strip()
    if not token:
        print(json.dumps({"status":"blocked_missing_secret"}));return 2
    v2="https://api2.mercadopublico.cl/v2/compra-agil/"+CODES["compra_agil"]
    v1="https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?"+urlencode({"codigo":CODES["licitacion"],"ticket":token})
    status,doc=request(v2,{"ticket":token,"Accept":"application/json","User-Agent":"MER-V2-field-probe"})
    summary={"endpoint":"compra_agil_detalle_v2","code":CODES["compra_agil"],"http":status}
    if status==200 and isinstance(doc,dict):
        payload=doc.get("payload")
        if isinstance(payload,dict):
            arr=payload.get("proveedores_cotizando")
            summary["payload_valid"]=str(payload.get("codigo"))==CODES["compra_agil"]
            summary["offers_container_is_list"]=isinstance(arr,list)
            summary["offers_count"]=len(arr) if isinstance(arr,list) else None
            if isinstance(arr,list) and arr:
                summary["ofertas"]={out:any(exists(x,source) for x in arr) for out,source in TARGETS["compra_agil"]["ofertas"].items()}
                winners=[x for x in arr if isinstance(x,dict) and x.get("proveedor_seleccionado") in (True,1,"1")]
                summary["selected_offers_count"]=len(winners)
                summary["resultados"]={out:any(exists(x,source) for x in winners) for out,source in TARGETS["compra_agil"]["resultados"].items()}
            else:
                summary["ofertas"]={"status":"no_offers_in_sample"}
    print(json.dumps(summary,ensure_ascii=False))
    status,doc=request(v1,{"Accept":"application/json","User-Agent":"MER-V2-field-probe"})
    summary={"endpoint":"licitacion_detalle_v1","code":CODES["licitacion"],"http":status}
    if status==200 and isinstance(doc,dict):
        ls=doc.get("Listado")
        a=next((x.get("Adjudicacion") for x in ls if isinstance(x,dict) and x.get("CodigoExterno")==CODES["licitacion"]),None) if isinstance(ls,list) else None
        summary["match_found"]=isinstance(a,dict)
        if isinstance(a,dict):
            summary["resultados"]={out:exists(a,source) for out,source in TARGETS["licitacion"]["resultados"].items()}
            summary["resultados"]["adjudicatario_alt"]=exists(a,"NombreProveedor")
    print(json.dumps(summary,ensure_ascii=False))
    return 0 if status==200 else 1
if __name__=="__main__":
    raise SystemExit(main())
