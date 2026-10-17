#!/usr/bin/env python3
"""Diagnóstico aislado: máximo tres páginas de diez procesos V2, sin Sheets."""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = "https://api2.mercadopublico.cl/v2/compra-agil"
OUT = Path("diagnostico_paginas_v2")
PARAMS = {
    "publicado_desde": "2026-10-15T00:00:00-03:00",
    "publicado_hasta": "2026-10-15T23:59:59-03:00",
    "tamano_pagina": 10,
}
def main():
    ticket = os.environ.get("CHILECOMPRA_TICKET", "").strip()
    if not ticket:
        raise SystemExit("Falta CHILECOMPRA_TICKET")
    OUT.mkdir(exist_ok=True)
    path = OUT / "resultados.json"
    resultados = []
    print("Prueba V2: hasta tres páginas, diez registros cada una; detener al primer fallo.", flush=True)
    try:
        for numero in (1, 2, 3):
            parametros = {**PARAMS, "numero_pagina": numero}
            req = Request(URL + "?" + urlencode(parametros), headers={
                "ticket": ticket, "Accept": "application/json",
                "User-Agent": "Observatorio-Diagnostico-Paginacion/1.0"})
            inicio = time.monotonic()
            registro = {"pagina": numero, "inicio_utc": datetime.now(timezone.utc).isoformat()}
            try:
                with urlopen(req, timeout=45) as resp:
                    registro["http"] = resp.status
                    raw = resp.read()
            except HTTPError as err:
                registro["http"] = err.code
                raw = err.read(1024)
            except (URLError, TimeoutError, OSError) as err:
                registro["error"] = type(err).__name__
                raw = None
            registro["segundos"] = round(time.monotonic() - inicio, 2)
            if registro.get("http") == 200 and raw is not None:
                try:
                    data = json.loads(raw)
                    payload = data.get("payload") if isinstance(data, dict) else None
                    items = payload.get("items") if isinstance(payload, dict) else None
                    pagination = payload.get("paginacion") if isinstance(payload, dict) else None
                    registro["items"] = len(items) if isinstance(items, list) else None
                    registro["total_paginas"] = pagination.get("total_paginas") if isinstance(pagination, dict) else None
                    registro["success"] = data.get("success") if isinstance(data, dict) else None
                    registro["valido"] = (
                        registro["success"] in (True, "OK")
                        and isinstance(items, list)
                        and isinstance(pagination, dict)
                        and len(items) <= 10
                    )
                except (ValueError, UnicodeError):
                    registro["valido"] = False
            else:
                registro["valido"] = False
                if raw is not None:
                    try:
                        errdata = json.loads(raw)
                        if isinstance(errdata, dict):
                            registro["mensaje"] = str(errdata.get("message") or errdata.get("mensaje") or "")[:120]
                    except (ValueError, UnicodeError):
                        pass
            resultados.append(registro)
            path.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(registro, ensure_ascii=False), flush=True)
            if not registro["valido"]:
                print("Detenido en la página", numero, "sin reintentos.", flush=True)
                break
            if numero < 3:
                print("Esperando 60 segundos antes de la siguiente página...", flush=True)
                time.sleep(60)
    except KeyboardInterrupt:
        print("Interrumpido por el usuario.", flush=True)
    finally:
        print("Resumen guardado en", path, "(sin cuerpos JSON ni credenciales).", flush=True)

if __name__ == "__main__":
    main()
