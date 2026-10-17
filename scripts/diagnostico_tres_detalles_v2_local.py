#!/usr/bin/env python3
"""Diagnóstico controlado de tres detalles Compra Ágil V2 desde Ubuntu."""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

CODES = ("425-339-COT26", "425-325-COT26", "3179-290-COT26")
BASE = "https://api2.mercadopublico.cl/v2/compra-agil/"
DIR = Path("diagnostico_detalles_v2")

def main():
    ticket = os.environ.get("CHILECOMPRA_TICKET", "").strip()
    if not ticket:
        raise SystemExit("Falta CHILECOMPRA_TICKET en el entorno")
    DIR.mkdir(exist_ok=True)
    manifest = DIR / "resultados.json"
    if manifest.exists():
        print("Ya existe resultados.json: no se sobrescribe ni repite la prueba.", flush=True)
        print("Para analizar resultados: cat diagnostico_detalles_v2/resultados.json")
        return
    records = []
    print("Tres detalles, un pedido por código; sin reintentos. Pausa 60 s.", flush=True)
    for index, code in enumerate(CODES):
        if index:
            print("Esperando 60 segundos...", flush=True)
            time.sleep(60)
        start = time.monotonic()
        result = {"codigo": code, "inicio_utc": datetime.now(timezone.utc).isoformat()}
        request = Request(BASE + quote(code, safe=""), headers={
            "ticket": ticket,
            "Accept": "application/json",
            "User-Agent": "Observatorio-Diagnostico-Detalle/1.0"})
        raw = None
        try:
            with urlopen(request, timeout=45) as response:
                result["http"] = response.status
                raw = response.read()
                result["bytes"] = len(raw)
        except HTTPError as error:
            result["http"] = error.code
            raw = error.read(2048)
            result["bytes_error"] = len(raw)
        except (URLError, TimeoutError, OSError) as error:
            result["error"] = type(error).__name__
        result["segundos"] = round(time.monotonic() - start, 2)
        if result.get("http") == 200 and raw is not None:
            try:
                data = json.loads(raw)
                result["json_valido"] = isinstance(data, (dict, list))
                if result["json_valido"]:
                    path = DIR / (code + ".json")
                    temp = path.with_suffix(".json.tmp")
                    temp.write_bytes(raw)
                    os.replace(temp, path)
                    result["archivo_guardado"] = str(path)
            except (ValueError, UnicodeError, OSError):
                result["json_valido"] = False
        elif raw:
            try:
                err = json.loads(raw)
                if isinstance(err, dict):
                    message = err.get("message") or err.get("mensaje")
                    if message is not None:
                        result["mensaje"] = str(message)[:200]
                    elif "errors" in err:
                        result["error_estructura"] = "errors"
            except (ValueError, UnicodeError):
                pass
        records.append(result)
        tmp = manifest.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, manifest)
        print(json.dumps(result, ensure_ascii=False), flush=True)
        if result.get("http") == 429:
            print("HTTP 429: detenido; no más consultas.", flush=True)
            break
    print("Resultados:", manifest, flush=True)
    print("Sin cambios a Sheets ni a los ETL originales.", flush=True)

if __name__ == "__main__":
    main()
