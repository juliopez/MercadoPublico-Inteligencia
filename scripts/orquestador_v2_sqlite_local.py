#!/usr/bin/env python3
"""Orquestador experimental V2: cola SQLite local, sin Sheets ni ETL originales."""
import argparse
import contextlib
import fcntl
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
    CREATE TABLE IF NOT EXISTS circuit (
      servicio TEXT PRIMARY KEY, consecutivos INTEGER NOT NULL DEFAULT 0,
      abierto_hasta TEXT NOT NULL DEFAULT '', actualizado TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS rate_limit (servicio TEXT PRIMARY KEY, siguiente_epoch REAL NOT NULL);
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
def reserve_request(con, min_interval=60, service='api_v2'):
    if min_interval < 0: raise ValueError('Intervalo invalido')
    con.execute('BEGIN IMMEDIATE')
    try:
        row=con.execute('SELECT siguiente_epoch FROM rate_limit WHERE servicio=?',(service,)).fetchone()
        now=time.time()
        scheduled=max(now, row['siguiente_epoch'] if row else now)
        con.execute('INSERT INTO rate_limit(servicio,siguiente_epoch) VALUES(?,?) ON CONFLICT(servicio) DO UPDATE SET siguiente_epoch=excluded.siguiente_epoch',(service,scheduled+min_interval))
        con.commit()
    except BaseException:
        con.rollback()
        raise
    delay=max(0.0,scheduled-time.time())
    if delay>0: time.sleep(delay)
    return delay

def circuit_open(con, service="api_v2"):
    r=con.execute("SELECT abierto_hasta FROM circuit WHERE servicio=?",(service,)).fetchone()
    return bool(r and r["abierto_hasta"] and r["abierto_hasta"]>stamp(utc()))

def circuit_record(con, http, service="api_v2", threshold=3, cooldown=1800):
    r=con.execute("SELECT consecutivos FROM circuit WHERE servicio=?",(service,)).fetchone()
    before=r["consecutivos"] if r else 0
    failure=http in (500,502,503,504) or http is None
    consecutivos=(before+1) if failure else 0
    # Ante HTTP 429 se suspende todo el servicio, no solo el trabajo individual.
    until=stamp(utc()+timedelta(seconds=(3600 if http==429 else cooldown))) if (http==429 or consecutivos>=threshold) else ""
    con.execute("""INSERT INTO circuit(servicio,consecutivos,abierto_hasta,actualizado)
        VALUES(?,?,?,?) ON CONFLICT(servicio) DO UPDATE SET
        consecutivos=excluded.consecutivos,abierto_hasta=excluded.abierto_hasta,
        actualizado=excluded.actualizado""",(service,consecutivos,until,stamp(utc())))
    return until

@contextlib.contextmanager
def execution_lock(root=ROOT):
    """Bloquea la ejecución HTTP entre procesos del mismo Ubuntu; el SO libera al morir."""
    root.mkdir(parents=True, exist_ok=True)
    path=root/'api_v2_ejecucion.lock'
    with path.open('a+b') as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Ya hay otra ejecución API V2 activa; ninguna solicitud realizada')
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

def reconcile_pages(con, fecha, root=ROOT):
    '''Recupera un JSON persistido antes del checkpoint; no sobrescribe ni consulta API.'''
    done={r['pagina'] for r in con.execute("SELECT pagina FROM jobs WHERE fecha=? AND estado='completo'",(fecha,))}
    seen=set()
    totals=set()
    for page in sorted(done):
        path=file_for(root,fecha,page)
        count,total,codes=valid_bytes(path.read_bytes(),page)
        if seen & codes: raise ValueError('duplicados entre páginas completadas')
        seen.update(codes);totals.add(total)
    if len(totals)>1: raise ValueError('paginación inconsistente')
    recovered=0
    for row in con.execute("SELECT pagina FROM jobs WHERE fecha=? AND estado!='completo' ORDER BY pagina",(fecha,)).fetchall():
        page=row['pagina']; path=file_for(root,fecha,page)
        if not path.exists(): continue
        try:
            count,total,codes=valid_bytes(path.read_bytes(),page)
            if (totals and total not in totals) or seen & codes: raise ValueError('página incompatible')
        except (OSError,ValueError,KeyError,TypeError,UnicodeError) as exc:
            print(f'Página {page}: archivo no reconciliable ({type(exc).__name__}); detenido')
            raise
        with con:
            con.execute("UPDATE jobs SET estado='completo',archivo=?,registros=?,paginas_total=?,http=200,error=NULL,disponible='',actualizado=? WHERE fecha=? AND pagina=?",(str(path),count,total,stamp(utc()),fecha,page))
            event(con,fecha,page,'recuperado_desde_archivo',200,0)
        seen.update(codes);totals.add(total);recovered+=1
    return recovered

def execute(con,args):
    ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
    if not ticket:
        raise SystemExit("Falta CHILECOMPRA_TICKET")
    recovered=reconcile_pages(con,args.fecha)
    if recovered: print(f'Páginas recuperadas desde disco sin HTTP: {recovered}')
    unique,prior_total=check_done(con,args.fecha)
    print(f"Registros únicos locales validados: {unique}; paginas reportadas: {prior_total}")
    start,end=day_range(args.fecha)
    calls=0
    while calls<args.max_solicitudes:
        if circuit_open(con):
            print("Circuit breaker V2 abierto: no se realizan solicitudes.",flush=True)
            break
        row=con.execute("""SELECT * FROM jobs WHERE fecha=? AND estado IN ('pendiente','espera')
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
        reserve_request(con)
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
                with con:
                    circuit_record(con,200)
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
                circuit_record(con,http)
            print(f"Página {page}: HTTP {http}, {elapsed}s; estado={state}; próximo intento={due or 'revisión manual'}")
            print("Detenido al primer fallo; sin reintentos en esta ejecución")
            break
        calls+=1
        # La reserva SQLite aplica el intervalo global entre inicios.
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
            with execution_lock(ROOT):
                execute(con,args)
    finally:
        con.close()
if __name__=="__main__":
    main()
