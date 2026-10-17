#!/usr/bin/env python3
"""Orquestador experimental V2: cola SQLite local, sin Sheets ni ETL originales."""
import argparse
import json
import os
import random
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

BASE = "https://api2.mercadopublico.cl/v2/compra-agil"
ROOT = Path("orquestacion_v2_local")
CHILE = ZoneInfo("America/Santiago")
def utc():
    return datetime.now(timezone.utc)
def stamp(d):
    return d.isoformat(timespec="seconds")
def db_open(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS jobs (
      id INTEGER PRIMARY KEY, fecha TEXT NOT NULL, pagina INTEGER NOT NULL,
      estado TEXT NOT NULL DEFAULT 'pendiente', intentos INTEGER NOT NULL DEFAULT 0,
      disponible TEXT NOT NULL DEFAULT '', http INTEGER, error TEXT,
      archivo TEXT, registros INTEGER, paginas_total INTEGER,
      actualizado TEXT NOT NULL, UNIQUE(fecha,pagina)
    );
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY, fecha TEXT, pagina INTEGER,
      evento TEXT, http INTEGER, segundos REAL, cuando TEXT
    );
    """)
    return con
def day_range(date):
    d=datetime.strptime(date,"%Y-%m-%d").date()
    start=datetime.combine(d, datetime.min.time(),CHILE)
    end=datetime.combine(d+timedelta(days=1),datetime.min.time(),CHILE)-timedelta(seconds=1)
    return start.isoformat(timespec="seconds"),end.isoformat(timespec="seconds")
def valid_bytes(raw, page):
    obj=json.loads(raw)
    if not isinstance(obj,dict) or obj.get("success") not in (True,"OK"):
        raise ValueError("success no reconocido")
    payload=obj.get("payload")
    if not isinstance(payload,dict):
        raise ValueError("payload no valido")
    items=payload.get("items")
    pg=payload.get("paginacion")
    if not isinstance(items,list) or not isinstance(pg,dict):
        raise ValueError("estructura no valida")
    total=int(pg.get("total_paginas",0))
    if total<page or len(items)>10 or (not items and page<total):
        raise ValueError("paginacion o cantidad incoherente")
    codes=[x.get("codigo") for x in items if isinstance(x,dict)]
    if len(codes)!=len(items) or not all(codes) or len(set(codes))!=len(codes):
        raise ValueError("codigos ausentes o duplicados")
    return len(items),total,set(map(str,codes))
def file_for(root,date,page):
    return root/date/f"pagina_{page:04d}.json"
def write_atomic(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".json.tmp")
    tmp.write_bytes(raw)
    os.replace(tmp,path)
def event(con,date,page,kind,http=None,seconds=None):
    con.execute("INSERT INTO events(fecha,pagina,evento,http,segundos,cuando) VALUES (?,?,?,?,?,?)",
                (date,page,kind,http,seconds,stamp(utc())))
def initialize(con, date, n, legacy):
    now=stamp(utc())
    for p in range(1,n+1):
        con.execute("INSERT OR IGNORE INTO jobs(fecha,pagina,actualizado) VALUES (?,?,?)",(date,p,now))
    if legacy:
        folders=sorted(Path("extraccion_v2_local").glob(date+"_*"))
        if len(folders)!=1:
            raise ValueError("Importación requiere exactamente un directorio legado para la fecha")
        seen=set()
        for p in range(1,n+1):
            source=folders[0]/f"pagina_{p:04d}.json"
            if not source.exists():
                continue
            raw=source.read_bytes()
            count,total,codes=valid_bytes(raw,p)
            if seen.intersection(codes):
                raise ValueError("Duplicados entre archivos legados")
            seen.update(codes)
            dest=file_for(ROOT,date,p)
            if dest.exists():
                valid_bytes(dest.read_bytes(),p)
            else:
                write_atomic(dest,raw)
            con.execute("""UPDATE jobs SET estado='completo',archivo=?,registros=?,paginas_total=?,
                           actualizado=?, error=NULL WHERE fecha=? AND pagina=?""",
                        (str(dest),count,total,now,date,p))
            event(con,date,p,"importado")
        print(f"Importados o verificados {len(seen)} códigos de archivos locales existentes")
    con.commit()
def check_done(con,date):
    seen=set()
    known_totals=set()
    for j in con.execute("SELECT * FROM jobs WHERE fecha=? AND estado='completo' ORDER BY pagina",(date,)):
        file=Path(j["archivo"] or "")
        if not file.is_file():
            raise ValueError(f"Archivo ausente para pagina {j['pagina']}")
        count,total,codes=valid_bytes(file.read_bytes(),j["pagina"])
        if count != j["registros"] or seen.intersection(codes):
            raise ValueError(f"Inconsistencia en pagina {j['pagina']}")
        known_totals.add(total)
        seen.update(codes)
    if len(known_totals)>1:
        raise ValueError("Cambió total de páginas, requiere revisión")
    return len(seen),next(iter(known_totals),None)
def show(con,date):
    rows=con.execute("SELECT estado,COUNT(*) n FROM jobs WHERE fecha=? GROUP BY estado",(date,)).fetchall()
    print(json.dumps({"fecha":date,"estados":{r["estado"]:r["n"] for r in rows}},ensure_ascii=False))
    for j in con.execute("SELECT pagina,estado,intentos,http,error,disponible FROM jobs WHERE fecha=? ORDER BY pagina",(date,)):
        print(dict(j))
def execute(con,args):
    ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
    if not ticket:
        raise SystemExit("Falta CHILECOMPRA_TICKET")
    unique,prior_total=check_done(con,args.fecha)
    print(f"Registros únicos locales validados: {unique}; paginas reportadas: {prior_total}")
    start,end=day_range(args.fecha)
    calls=0
    while calls<args.max_solicitudes:
        row=con.execute("""SELECT * FROM jobs WHERE fecha=? AND estado!='completo'
          AND (disponible='' OR disponible<=?) ORDER BY pagina LIMIT 1""",
          (args.fecha,stamp(utc()))).fetchone()
        if row is None:
            print("No hay tareas disponibles: completadas o en espera de reintento")
            break
        page=row["pagina"]
        if prior_total and page>prior_total:
            print("Página fuera de rango; detener")
            break
        params={"publicado_desde":start,"publicado_hasta":end,"numero_pagina":page,"tamano_pagina":10}
        req=Request(BASE+"?"+urlencode(params),headers={"ticket":ticket,"Accept":"application/json",
          "User-Agent":"Observatorio-Orquestador-Experimental/1.0"})
        t=time.monotonic(); raw=None; http=None; issue=None; retry=None
        try:
            with urlopen(req,timeout=45) as resp:
                http=resp.status;raw=resp.read()
        except HTTPError as e:
            http=e.code;retry=e.headers.get("Retry-After");e.close();issue="HTTP"
        except (URLError,TimeoutError,OSError) as e:
            issue=type(e).__name__
        elapsed=round(time.monotonic()-t,2)
        if http==200 and raw:
            try:
                count,total,codes=valid_bytes(raw,page)
                if prior_total is not None and total!=prior_total:
                    raise ValueError("total_paginas cambio")
                existing=set()
                for old in con.execute("SELECT pagina,archivo FROM jobs WHERE fecha=? AND estado='completo'",(args.fecha,)):
                    existing.update(valid_bytes(Path(old["archivo"]).read_bytes(),old["pagina"])[2])
                if existing.intersection(codes):
                    raise ValueError("codigos duplicados entre paginas")
                dest=file_for(ROOT,args.fecha,page)
                write_atomic(dest,raw)
                with con:
                    con.execute("""UPDATE jobs SET estado='completo',intentos=intentos+1,
                      disponible='',http=200,error=NULL,archivo=?,registros=?,paginas_total=?,actualizado=?
                      WHERE fecha=? AND pagina=?""",(str(dest),count,total,stamp(utc()),args.fecha,page))
                    event(con,args.fecha,page,"completo",200,elapsed)
                prior_total=total
                print(f"Página {page}: HTTP 200, {count} registros, {elapsed}s, guardada")
            except (ValueError,KeyError,TypeError,UnicodeError,OSError) as e:
                issue="validacion:"+str(e)[:90]
                if "duplicados" in issue or "total_paginas" in issue:
                    http=422
        if http!=200 or issue:
            attempts=row["intentos"]+1
            if http in (400,401,403,422):
                state="revision"; delay=0
            elif http==429:
                state="espera";delay=3600
                if retry and retry.isdigit():
                    delay=max(delay,int(retry))
            else:
                state="espera"
                delay=min(3600,300*2**min(attempts-1,3))+random.randint(0,60)
            due=stamp(utc()+timedelta(seconds=delay)) if delay else ""
            with con:
                con.execute("""UPDATE jobs SET estado=?,intentos=?,disponible=?,http=?,error=?,actualizado=?
                  WHERE fecha=? AND pagina=?""",
                  (state,attempts,due,http,issue or "respuesta_no_valida",stamp(utc()),args.fecha,page))
                event(con,args.fecha,page,state,http,elapsed)
            print(f"Página {page}: HTTP {http}, {elapsed}s; estado={state}; próximo intento={due or 'revisión manual'}")
            print("Detenido al primer fallo; sin reintentos en esta ejecución")
            break
        calls+=1
        if calls<args.max_solicitudes:
            time.sleep(args.pausa)
    show(con,args.fecha)
def main():
    p=argparse.ArgumentParser(description="Orquestador experimental V2 con cola SQLite local")
    p.add_argument("accion",choices=["iniciar","ejecutar","estado"])
    p.add_argument("--fecha",default="2026-10-15")
    p.add_argument("--paginas",type=int,default=10)
    p.add_argument("--importar-local",action="store_true")
    p.add_argument("--max-solicitudes",type=int,default=2)
    p.add_argument("--pausa",type=int,default=60)
    args=p.parse_args()
    if not 1<=args.paginas<=10 or not 1<=args.max_solicitudes<=3 or args.pausa<30:
        p.error("Máximo 10 páginas, 3 solicitudes por ejecución y pausa mínima 30s")
    day_range(args.fecha)
    con=db_open(ROOT/"control.sqlite3")
    try:
        if args.accion=="iniciar":
            initialize(con,args.fecha,args.paginas,args.importar_local)
            show(con,args.fecha)
        elif args.accion=="estado":
            show(con,args.fecha)
        else:
            execute(con,args)
    finally:
        con.close()
if __name__=="__main__":
    main()
