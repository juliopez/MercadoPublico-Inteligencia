#!/usr/bin/env python3
"""Extractor experimental de listados V2: local, reanudable y sin Google Sheets."""
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

BASE = "https://api2.mercadopublico.cl/v2/compra-agil"

def write_atomic(path, data):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)

def validated(path, expected_page, size):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        payload = data["payload"]
        items = payload["items"]
        pages = int(payload["paginacion"]["total_paginas"])
        if data.get("success") not in (True, "OK") or not isinstance(items, list):
            return None
        if not 1 <= len(items) <= size or pages < expected_page:
            return None
        codes = [item.get("codigo") for item in items if isinstance(item, dict)]
        if len(codes) != len(items) or any(not c for c in codes) or len(set(codes)) != len(codes):
            return None
        return pages, len(items)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None

def page_codes(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(item["codigo"]) for item in data["payload"]["items"]}

def main():
    parser = argparse.ArgumentParser(description="Extractor local incremental, sin escrituras a Sheets")
    parser.add_argument("--fecha", default="2026-10-15")
    parser.add_argument("--max-paginas", type=int, default=3)
    parser.add_argument("--pausa", type=int, default=60)
    parser.add_argument("--q", default="")
    parser.add_argument("--salida", default="extraccion_v2_local")
    args = parser.parse_args()
    if not 1 <= args.max_paginas <= 10:
        parser.error("En esta etapa se permiten solamente 1 a 10 páginas por ejecución")
    if args.pausa < 30:
        parser.error("La pausa mínima experimental es de 30 segundos")
    if len(args.q) > 120:
        parser.error("Filtro demasiado largo")
    try:
        day = datetime.strptime(args.fecha, "%Y-%m-%d").date()
    except ValueError:
        parser.error("Fecha inválida (AAAA-MM-DD)")
    if day > datetime.now(ZoneInfo("America/Santiago")).date():
        parser.error("La fecha no puede ser futura")
    ticket = os.environ.get("CHILECOMPRA_TICKET", "").strip()
    if not ticket:
        parser.error("Falta CHILECOMPRA_TICKET")
    local = ZoneInfo("America/Santiago")
    start = datetime.combine(day, datetime.min.time(), tzinfo=local).isoformat(timespec="seconds")
    end = (datetime.combine(day + timedelta(days=1), datetime.min.time(), tzinfo=local) - timedelta(seconds=1)).isoformat(timespec="seconds")
    params = {"publicado_desde": start, "publicado_hasta": end, "tamano_pagina": 10}
    if args.q:
        params["q"] = args.q
    signature = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:12]
    out = Path(args.salida) / f"{day}_{signature}"
    out.mkdir(parents=True, exist_ok=True)
    log = out / "manifest.json"
    history = []
    if log.exists():
        try:
            history = json.loads(log.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
        except (ValueError, OSError):
            history = []
    print(f"Directorio: {out} | paginas maximas: {args.max_paginas} | tamano: 10", flush=True)
    total_pages = None
    seen = set()
    for number in range(1, args.max_paginas + 1):
        pagefile = out / f"pagina_{number:04d}.json"
        previous = validated(pagefile, number, 10) if pagefile.exists() else None
        if previous:
            pages, count = previous
            if total_pages is not None and pages != total_pages:
                print("Paginación inconsistente en caché; detenido", flush=True)
                break
            overlap = seen.intersection(page_codes(pagefile))
            if overlap:
                print(f"Duplicados entre páginas en archivo guardado: {len(overlap)}; detenido", flush=True)
                break
            seen.update(page_codes(pagefile))
            total_pages = pages
            print(f"Pagina {number}: guardada y validada ({count} registros), sin consultar API", flush=True)
            if number >= total_pages:
                break
            continue
        if pagefile.exists():
            print(f"Pagina {number}: archivo previo inválido, detenido para revisión", flush=True)
            break
        req = Request(BASE+"?"+urlencode({**params,"numero_pagina":number}), headers={
            "ticket":ticket, "Accept":"application/json", "User-Agent":"Observatorio-Extractor-Experimental/1.0"})
        start_time=time.monotonic()
        record={"pagina":number,"fecha_utc":datetime.now().astimezone().isoformat()}
        raw=None
        try:
            with urlopen(req,timeout=45) as response:
                record["http"]=response.status
                raw=response.read()
        except HTTPError as exc:
            record["http"]=exc.code
            record["error"]="HTTP"
        except (URLError,TimeoutError,OSError) as exc:
            record["error"]=type(exc).__name__
        record["segundos"]=round(time.monotonic()-start_time,2)
        if record.get("http")==200 and raw is not None:
            tmp=out/f"pagina_{number:04d}.json.tmp"
            try:
                tmp.write_bytes(raw)
                check=validated(tmp,number,10)
                if check is None:
                    record["error"]="json_o_estructura_invalida"
                    tmp.unlink(missing_ok=True)
                else:
                    pages,count=check
                    if total_pages is not None and pages != total_pages:
                        record["error"]="paginacion_inconsistente"
                        tmp.unlink(missing_ok=True)
                    else:
                        overlap = seen.intersection(page_codes(tmp))
                        if overlap:
                            record["error"] = "duplicados_entre_paginas"
                            record["duplicados"] = len(overlap)
                            tmp.unlink(missing_ok=True)
                        else:
                            total_pages=pages
                            seen.update(page_codes(tmp))
                            os.replace(tmp,pagefile)
                            record.update({"registros":count,"total_paginas":pages,"guardado":True})
            except (OSError,UnicodeError,ValueError) as exc:
                record["error"]="error_guardado_o_validacion"
                tmp.unlink(missing_ok=True)
        history.append(record)
        write_atomic(log,history)
        print(json.dumps(record,ensure_ascii=False),flush=True)
        if not record.get("guardado"):
            print("Se detuvo al primer error; sin reintentos.",flush=True)
            break
        if number>=total_pages:
            break
        if number<args.max_paginas:
            print(f"Esperando {args.pausa} segundos...",flush=True)
            time.sleep(args.pausa)
    print(f"Códigos únicos en páginas validadas: {len(seen)}", flush=True)
    print(f"Resumen técnico: {log}",flush=True)
    print("No se publicaron datos ni se modificaron ETL originales.",flush=True)

if __name__=="__main__":
    main()
