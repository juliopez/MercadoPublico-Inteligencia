#!/usr/bin/env python3
"""Un ciclo V2 con presupuesto y resumen. Se programa externamente; no escribe en Sheets."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DB=ROOT/"orquestacion_v2_local"/"control.sqlite3"
DETAIL=ROOT/"scripts"/"orquestador_v2_detalles_local.py"
LOGDIR=ROOT/"orquestacion_v2_local"/"informes"

def counts():
    import sqlite3
    if not DB.exists():return {}
    con=sqlite3.connect(f"file:{DB}?mode=ro",uri=True)
    try:
        return dict(con.execute("SELECT estado, COUNT(*) FROM detail_jobs GROUP BY estado").fetchall())
    finally:con.close()

def main():
    parser=argparse.ArgumentParser(description="Un ciclo de detalles API V2, acotado y recuperable")
    parser.add_argument("--max-solicitudes",type=int,default=5)
    parser.add_argument("--max-duracion",type=int,default=420)
    args=parser.parse_args()
    if not 1<=args.max_solicitudes<=5 or not 120<=args.max_duracion<=900:
        parser.error("Límites admitidos: 1-5 solicitudes y 120-900 segundos")
    before=counts()
    if not before: raise SystemExit("La cola no existe o está vacía; inicializarla primero")
    command=[sys.executable,str(DETAIL),"ejecutar","--max-solicitudes",str(args.max_solicitudes),
             "--max-duracion",str(args.max_duracion)]
    started=datetime.now(timezone.utc)
    try:
        proc=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=args.max_duracion+75)
        code=proc.returncode;out=proc.stdout[-12000:];err=proc.stderr[-2000:]
    except subprocess.TimeoutExpired:
        code=124;out="";err="La ejecución excedió el margen externo de seguridad"
    after=counts()
    record={"inicio_utc":started.isoformat(),"fin_utc":datetime.now(timezone.utc).isoformat(),
            "estado_antes":before,"estado_despues":after,"codigo_salida":code,
            "detalle_terminal":out,"error_terminal":err}
    LOGDIR.mkdir(parents=True,exist_ok=True)
    name=started.strftime("%Y%m%dT%H%M%SZ")
    path=LOGDIR/f"ciclo_{name}.json"
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Ciclo terminado. Estados:",json.dumps(after,ensure_ascii=False))
    print("Informe:",path)
    if code:print("Advertencia: salida no exitosa; revisar informe")
    return code
if __name__=="__main__":sys.exit(main())
