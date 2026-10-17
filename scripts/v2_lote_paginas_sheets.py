#!/usr/bin/env python3
"""Lote acotado de páginas V2 para GitHub Actions; reutiliza checkpoints de ControlV2."""
import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT=Path(__file__).with_name("v2_primera_escritura_sheets.py")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fecha",required=True)
    p.add_argument("--pagina-inicial",type=int,default=1)
    p.add_argument("--max-paginas",type=int,default=3)
    a=p.parse_args()
    if not 1<=a.pagina_inicial<=10000 or not 1<=a.max_paginas<=3:
        p.error("Rango inválido: hasta tres páginas por ciclo")
    started=time.monotonic()
    queried=0
    for page in range(a.pagina_inicial,a.pagina_inicial+a.max_paginas):
        if time.monotonic()-started>420:
            print("LOTE_V2_LIMITE_TIEMPO: se preservan checkpoints anteriores")
            break
        if queried:
            # Pausa entre las solicitudes a ChileCompra; no cuenta páginas ya completas.
            since=time.monotonic()-last_query
            if since<60:time.sleep(60-since)
        last_query=time.monotonic()
        cmd=[sys.executable,str(SCRIPT),"--fecha",a.fecha,"--pagina",str(page),"--escribir"]
        proc=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
        if proc.stdout:print(proc.stdout.strip(),flush=True)
        if proc.stderr:print(proc.stderr.strip(),file=sys.stderr,flush=True)
        if proc.returncode:raise SystemExit(proc.returncode)
        if "V2_SHEETS_OK:" in proc.stdout:queried+=1
        elif "CHECKPOINT_COMPLETO:" in proc.stdout:continue
        else:
            print("LOTE_V2_PAUSADO: página en espera, error HTTP o respuesta no procesada")
            break
    print("LOTE_V2_FIN: páginas nuevas exitosas",queried)
if __name__=="__main__":main()
