#!/usr/bin/env python3
"""Una petición diagnóstica al listado V2 de Compra Ágil. No modifica Sheets."""
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api2.mercadopublico.cl/v2/compra-agil"

def main():
    ticket = os.environ.get("CHILECOMPRA_TICKET", "").strip()
    if not ticket:
        raise SystemExit("Falta CHILECOMPRA_TICKET; configura la variable en Ubuntu")
    # Fecha fija de diagnóstico, no una descarga del mes completo.
    params = {
        "publicado_desde": "2026-10-15T00:00:00-03:00",
        "publicado_hasta": "2026-10-15T23:59:59-03:00",
        "tamano_pagina": 10,
        "numero_pagina": 1,
    }
    req = Request(BASE + "?" + urlencode(params),
                  headers={"ticket": ticket, "Accept": "application/json",
                           "User-Agent": "Observatorio-Diagnostico-Listado/1.0"})
    print("Una consulta: listado V2, 2026-10-15, pagina 1, tamano 10", flush=True)
    inicio = time.monotonic()
    try:
        with urlopen(req, timeout=45) as response:
            status = response.status
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
            retry_after = response.headers.get("Retry-After", "")
    except HTTPError as error:
        status = error.code
        raw = error.read(2048)
        content_type = error.headers.get("Content-Type", "")
        retry_after = error.headers.get("Retry-After", "")
    except (URLError, TimeoutError, OSError) as error:
        print(json.dumps({"error": type(error).__name__,
                          "segundos": round(time.monotonic() - inicio, 2)}))
        return
    result = {"http": status, "segundos": round(time.monotonic() - inicio, 2),
              "bytes": len(raw), "content_type": content_type,
              "retry_after": retry_after or None}
    if status != 200:
        result["estado"] = "error_http"
        # Mostrar solamente mensajes de error; nunca cabeceras ni ticket.
        try:
            body = json.loads(raw)
            if isinstance(body, dict):
                keys = ("message", "mensaje", "error", "detail", "details", "errors", "title")
                result["respuesta_error"] = {k: str(body[k])[:400] for k in keys if k in body}
                if not result["respuesta_error"]:
                    result["claves_error"] = list(body.keys())[:12]
            else:
                result["respuesta_error_tipo"] = type(body).__name__
        except (ValueError, UnicodeDecodeError):
            result["respuesta_error_texto"] = raw.decode("utf-8", errors="replace")[:400]
    else:
        try:
            data = json.loads(raw)
            payload = data.get("payload") if isinstance(data, dict) else None
            page = payload.get("paginacion") if isinstance(payload, dict) else None
            items = payload.get("items") if isinstance(payload, dict) else None
            result["json_valido"] = True
            result["success"] = data.get("success") if isinstance(data, dict) else None
            result["items_recibidos"] = len(items) if isinstance(items, list) else None
            result["total_paginas"] = page.get("total_paginas") if isinstance(page, dict) else None
            result["estructura_esperada"] = isinstance(items, list) and isinstance(page, dict)
            # No mostrar identificadores, cotizaciones ni valores individuales.
        except (ValueError, UnicodeDecodeError):
            result["json_valido"] = False
    print("parametros_sin_ticket=" + json.dumps(params, ensure_ascii=False), flush=True)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    print("Fin. No se han guardado datos ni modificado los ETL originales.", flush=True)

if __name__ == "__main__":
    main()
