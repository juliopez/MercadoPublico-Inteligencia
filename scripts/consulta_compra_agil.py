#!/usr/bin/env python3
"""Consulta exploratoria de Compra Ágil v2: NO publica resultados en Pages."""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CODES = [
    "425-325-COT26",
    "1549-3882-COT26",
    "5956-122-COT26",
    "3179-290-COT26",
    "839-4-COT26",
]
ROOT = "https://api2.mercadopublico.cl/v2/compra-agil"
OUT = Path("output/consulta")
CODE_RE = re.compile(r"^[0-9]+-[0-9]+-COT[0-9]{2}$")

def main():
    token = os.environ.get("CHILECOMPRA_TICKET", "").strip()
    if not token:
        print("ERROR: Configure CHILECOMPRA_TICKET como GitHub Actions Secret.", file=sys.stderr)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    for code in CODES:
        if not CODE_RE.fullmatch(code):
            raise ValueError("Código inválido")
        req = Request(
            f"{ROOT}/{code}",
            headers={"ticket": token, "Accept": "application/json", "User-Agent": "MercadoPublico-Inteligencia/0.1"},
        )
        item = {"codigo": code, "consultado_utc": datetime.now(timezone.utc).isoformat()}
        try:
            with urlopen(req, timeout=35) as response:
                body = response.read(4_000_000)
                data = json.loads(body)
                item["http_status"] = response.status
                # Archivo local en artefacto privado de ejecución, NO repositorio público.
                (OUT / f"{code}.json").write_text(
                    json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                item["tipo_raiz"] = type(data).__name__
                item["claves_raiz"] = list(data.keys()) if isinstance(data, dict) else []
                print(f"{code}: respuesta HTTP {response.status}")
        except HTTPError as exc:
            item["http_status"] = exc.code
            item["error"] = "HTTP error (sin exponer credenciales ni cuerpo)"
            print(f"{code}: error HTTP {exc.code}")
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            item["error"] = type(exc).__name__
            print(f"{code}: {type(exc).__name__}")
        summary.append(item)
        time.sleep(1)
    (OUT / "resumen.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0 if all(x.get("http_status") == 200 for x in summary) else 1

if __name__ == "__main__":
    sys.exit(main())
