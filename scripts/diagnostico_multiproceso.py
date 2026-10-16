#!/usr/bin/env python3
"""Diagnóstico multi-proceso de detalles Compra Ágil. Sin escrituras."""
import json, os, sys, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime, timezone
from pathlib import Path

CODES=["2284-520-COT26","425-325-COT26","2927-370-COT26"]
ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
if not ticket: sys.exit("Falta CHILECOMPRA_TICKET")
out=Path("output/diagnostico-multiproceso")
out.mkdir(parents=True,exist_ok=True)
results=[]
for i,code in enumerate(CODES):
    if i: time.sleep(3)
    record={"codigo":code,"fecha_utc":datetime.now(timezone.utc).isoformat(),
            "http":None,"estado":"pendiente","ofertas":None,"seleccionados":None}
    try:
        with urlopen(Request("https://api2.mercadopublico.cl/v2/compra-agil/"+code,
             headers={"ticket":ticket,"Accept":"application/json"}),timeout=35) as resp:
            data=json.load(resp)
            record["http"]=resp.status
        p=data.get("payload") or {}
        if p.get("codigo")!=code:raise ValueError("Codigo inesperado")
        offers=p.get("proveedores_cotizando") or []
        record.update(estado="ok",ofertas=len(offers),
           seleccionados=sum(o.get("proveedor_seleccionado") in (True,1,"1") for o in offers))
    except HTTPError as err:
        record.update(http=err.code,estado="error_http",retry_after=err.headers.get("Retry-After"))
    except (URLError,TimeoutError,ValueError) as err:
        record.update(estado="error_conexion_o_datos",tipo_error=type(err).__name__)
    results.append(record)
    print(json.dumps(record,ensure_ascii=False),flush=True)
(out/"diagnostico.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
print("RESUMEN",json.dumps({"consultados":len(results),
 "correctos":sum(r["estado"]=="ok" for r in results),
 "fallidos":sum(r["estado"]!="ok" for r in results),
 "escrituras_sheets":0}),flush=True)
