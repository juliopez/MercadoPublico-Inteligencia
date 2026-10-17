#!/usr/bin/env python3
"""Diagnóstico mínimo V1/V2 ChileCompra: sin persistir cuerpos ni credenciales."""
import json
import os
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def test(label, url, headers, timeout=40):
    req=Request(url, headers=headers)
    start=time.monotonic()
    result={"api":label,"inicio_utc":datetime.now(timezone.utc).isoformat()}
    try:
        with urlopen(req,timeout=timeout) as resp:
            result["http"]=resp.status
            result["content_type"]=resp.headers.get("Content-Type","")
            result["retry_after"]=resp.headers.get("Retry-After")
            # No descargar ni persistir el cuerpo completo.
    except HTTPError as exc:
        result["http"]=exc.code
        result["retry_after"]=exc.headers.get("Retry-After")
        result["content_type"]=exc.headers.get("Content-Type","")
    except (URLError, TimeoutError, OSError) as exc:
        result["error"]=type(exc).__name__
    finally:
        result["segundos"]=round(time.monotonic()-start,2)
    return result

def main():
    ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
    if not ticket:
        raise SystemExit("Falta CHILECOMPRA_TICKET en el entorno")
    common={"Accept":"application/json","User-Agent":"Observatorio-Diagnostico-Comparativo/1.0"}
    v1="https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?"+urlencode({"codigo":"1017312-6-LR26","ticket":ticket})
    v2="https://api2.mercadopublico.cl/v2/compra-agil/425-339-COT26"
    a=test("V1_licitacion_por_codigo",v1,common)
    print(json.dumps(a,ensure_ascii=False),flush=True)
    if a.get("http")==429:
        print("Detenido por HTTP 429; no se consulta V2")
        return
    time.sleep(5)
    b=test("V2_compra_agil_por_codigo",v2,{**common,"ticket":ticket})
    print(json.dumps(b,ensure_ascii=False),flush=True)
    print("Diagnóstico finalizado: dos consultas como máximo; ningún dato de proceso almacenado.")

if __name__=="__main__":
    main()
