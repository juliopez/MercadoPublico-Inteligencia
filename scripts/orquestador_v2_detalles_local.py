#!/usr/bin/env python3
"""Cola experimental de detalles V2. No ejecuta red salvo accion 'ejecutar' explícita."""
import argparse
import importlib.util
import json
import os
import random
import sqlite3
import time
from datetime import timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

SOURCE=Path(__file__).with_name("orquestador_v2_sqlite_local.py")
spec=importlib.util.spec_from_file_location("orquestador_lista_v2",SOURCE)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
ROOT=Path("orquestacion_v2_local")
def validar_detalle(raw, codigo):
    data=json.loads(raw)
    if not isinstance(data,dict) or data.get('success') not in ('OK',True): raise ValueError('success invalido')
    if data.get('errors'): raise ValueError('errors no vacio')
    payload=data.get('payload')
    if not isinstance(payload,dict) or str(payload.get('codigo',''))!=codigo: raise ValueError('codigo incorrecto')
    if not isinstance(payload.get('institucion'),dict): raise ValueError('institucion invalida')
    if not isinstance(payload.get('proveedores_cotizando'),list): raise ValueError('proveedores_cotizando invalido')
    if not isinstance(payload.get('productos_solicitados'),list): raise ValueError('productos_solicitados invalido')
    return data

def install(con):
    con.execute("""CREATE TABLE IF NOT EXISTS detail_jobs(
      codigo TEXT PRIMARY KEY, estado TEXT NOT NULL DEFAULT 'pendiente',
      intentos INTEGER NOT NULL DEFAULT 0, disponible TEXT NOT NULL DEFAULT '',
      http INTEGER, error TEXT, archivo TEXT, actualizado TEXT NOT NULL
    )""")
    con.commit()
def seed(con,date):
    items={}
    for row in con.execute("SELECT archivo FROM jobs WHERE fecha=? AND estado='completo'",(date,)):
        data=json.loads(Path(row["archivo"]).read_text(encoding="utf-8"))
        for item in data["payload"]["items"]:
            code=str(item["codigo"])
            items[code]=True
    with con:
        for code in sorted(items):
            con.execute("""INSERT OR IGNORE INTO detail_jobs(codigo,actualizado)
                           VALUES(?,?)""",(code,core.stamp(core.utc())))
    print(f"Códigos de detalle encontrados en listados: {len(items)}")
def report(con):
    print(json.dumps({r["estado"]:r["n"] for r in con.execute(
        "SELECT estado, COUNT(*) n FROM detail_jobs GROUP BY estado")},ensure_ascii=False))
    r=con.execute("SELECT consecutivos,abierto_hasta FROM circuit WHERE servicio='api_v2'").fetchone()
    if r:print("Circuit breaker V2:",dict(r))
def run(con,maximum):
    ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
    if not ticket:raise SystemExit("Falta CHILECOMPRA_TICKET")
    for _ in range(maximum):
        if core.circuit_open(con):
            print("Circuit breaker abierto: sin consultas")
            break
        j=con.execute("""SELECT * FROM detail_jobs WHERE estado IN ('pendiente','espera')
             AND (disponible='' OR disponible<=?) ORDER BY codigo LIMIT 1""",
             (core.stamp(core.utc()),)).fetchone()
        if not j:
            print("No hay detalles elegibles")
            break
        code=j["codigo"]
        req=Request(core.BASE+"/"+quote(code,safe=""),headers={"ticket":ticket,"Accept":"application/json",
            "User-Agent":"Observatorio-Detalles-Tolerante/1.0"})
        core.reserve_request(con)
        started=time.monotonic();http=None;raw=None;error=None;retry=None
        try:
            with urlopen(req,timeout=45) as response:
                http=response.status;raw=response.read()
        except HTTPError as exc:
            http=exc.code;retry=exc.headers.get("Retry-After");exc.close();error="HTTP"
        except (URLError,TimeoutError,OSError) as exc:
            error=type(exc).__name__
        path=None
        if http==200 and raw:
            try:
                parsed=validar_detalle(raw,code)
                if not isinstance(parsed,dict):
                    raise ValueError("Detalle no es objeto JSON")
                # Las respuestas exitosas deben preservarse, no asumir estado de adjudicación.
                path=ROOT/"detalles"/(code+".json")
                core.write_atomic(path,raw)
            except (ValueError,OSError,UnicodeError) as exc:
                error="detalle_invalido";path=None
        n=j["intentos"]+1
        if path:
            state="completo";delay=0
        elif http in (400,401,403):
            state="revision";delay=0
        elif http==429:
            state="espera";delay=max(3600,int(retry)) if retry and retry.isdigit() else 3600
        else:
            state="espera";delay=min(3600,300*2**min(n-1,3))+random.randint(0,60)
        due=core.stamp(core.utc()+timedelta(seconds=delay)) if delay else ""
        with con:
            con.execute("""UPDATE detail_jobs SET estado=?,intentos=?,disponible=?,http=?,error=?,
                        archivo=?,actualizado=? WHERE codigo=?""",
                        (state,n,due,http,error,str(path) if path else None,core.stamp(core.utc()),code))
            core.circuit_record(con,http if path or http!=200 else None)
        print(f"{code}: HTTP {http}, {round(time.monotonic()-started,2)} s, {state}, próximo={due or '-'}")
        if state!="completo":
            print("Detenido tras fallo; reintento diferido")
            break
def main():
    p=argparse.ArgumentParser()
    p.add_argument("accion",choices=("iniciar","estado","ejecutar"))
    p.add_argument("--fecha",default="2026-10-15")
    p.add_argument("--max-solicitudes",type=int,default=1)
    a=p.parse_args()
    if not 1<=a.max_solicitudes<=2:p.error("Máximo dos solicitudes por ejecución")
    con=core.db_open(ROOT/"control.sqlite3")
    try:
        install(con)
        if a.accion=="iniciar":seed(con,a.fecha)
        elif a.accion=="ejecutar":
            with core.execution_lock(ROOT):
                run(con,a.max_solicitudes)
        report(con)
    finally:con.close()
if __name__=="__main__":
    main()
