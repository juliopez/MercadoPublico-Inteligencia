#!/usr/bin/env python3
"""Extracción puntual, aislada y de solo lectura de procesos relacionados con LoBa.

No escribe en Google Sheets ni modifica los ETL del Observatorio.
Guarda la respuesta oficial cruda por código y un manifiesto de ejecución.
"""
import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

DEFAULT_CODES = [
    "425-339-COT26",
    "425-325-COT26",
    "3179-290-COT26",
    "577290-85-COT26",
    "1549-3882-COT26",
    "839-4-COT26",
]
BASE_V1 = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
BASE_V2 = "https://api2.mercadopublico.cl/v2/compra-agil"
CODE_PATTERN = re.compile(r"^[0-9]+-[0-9]+-[A-Z0-9]+$", re.I)

def request_json(url, headers, timeout=45):
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.load(response), response.status
    except HTTPError as exc:
        if exc.code == 429:
            raise RuntimeError("HTTP 429: detener todas las consultas; respetar límite de ChileCompra") from exc
        raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--codes", nargs="+", default=DEFAULT_CODES, help="Códigos exactos; por defecto seis casos LoBa")
    parser.add_argument("--out", default="salida_loba")
    parser.add_argument("--delay", type=float, default=3.0)
    args = parser.parse_args()
    ticket = os.environ.get("CHILECOMPRA_TICKET", "").strip()
    if not ticket:
        raise SystemExit("Falta CHILECOMPRA_TICKET; ninguna consulta realizada")
    codes = list(dict.fromkeys(c.strip().upper() for c in args.codes))
    if not codes or len(codes) > 20 or any(not CODE_PATTERN.fullmatch(c) for c in codes):
        raise SystemExit("Se admiten entre 1 y 20 códigos válidos")
    if args.delay < 2.0:
        raise SystemExit("La pausa mínima entre solicitudes es 2 segundos")
    directory = Path(args.out)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "codigos_solicitados": codes,
                "resultados": [], "advertencia": "La consulta no verifica participación ni adjudicación de LoBa."}
    for index, code in enumerate(codes):
        if index:
            time.sleep(args.delay)
        v2 = bool(re.search(r"-COT[0-9]+$", code))
        if v2:
            url = BASE_V2 + "/" + quote(code, safe="")
            headers = {"Accept": "application/json", "ticket": ticket}
        else:
            url = BASE_V1 + "?" + urlencode({"codigo": code, "ticket": ticket})
            headers = {"Accept": "application/json"}
        status = {"codigo": code, "api": "v2_compra_agil_detalle" if v2 else "v1_licitaciones_por_codigo"}
        try:
            data, http = request_json(url, headers)
            if not isinstance(data, dict):
                raise ValueError("Respuesta no es objeto JSON")
            destination = directory / (code + ".json")
            destination.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            status.update({"http": http, "estado": "recuperado_sin_validar_estructura", "archivo": destination.name})
        except HTTPError as exc:
            status.update({"http": exc.code, "estado": "error_http"})
            if exc.code in (401, 403, 404):
                status["observacion"] = "Revisar autenticación, existencia del proceso o disponibilidad del endpoint"
        except (URLError, TimeoutError, ValueError) as exc:
            status.update({"estado": "error_respuesta", "tipo_error": type(exc).__name__})
        except RuntimeError as exc:
            status.update({"http": 429, "estado": "detenido_limite"})
            manifest["resultados"].append(status)
            print("DETENIDO_HTTP_429", code, flush=True)
            break
        manifest["resultados"].append(status)
        print(code, status["estado"], flush=True)
    (directory / "manifiesto.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("FIN", len(manifest["resultados"]), "de", len(codes))
    if len(manifest["resultados"]) < len(codes) or any(x["estado"] != "recuperado_sin_validar_estructura" for x in manifest["resultados"]):
        raise SystemExit(2)

if __name__ == "__main__":
    main()
