#!/usr/bin/env python3
"""Recuperacion extraordinaria de licitaciones por API. No escribe MER ni publica datos."""
import argparse
import csv
import datetime as dt
import json
import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

API = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
COLS = ["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre",
        "monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas",
        "motivo_seleccion","url_detalle","fecha_sincronizacion","categoria","subcategoria","modalidad"]
TRANSIENTES = {429, 500, 502, 503, 504}

def valor(obj, key):
    x = (obj or {}).get(key)
    return "" if x is None else str(x).strip()

def presupuesto(r):
    if (valor(r,"CodigoMoneda").upper(), valor(r,"Estimacion"), valor(r,"VisibilidadMonto")) != ("CLP","1","1"):
        return ""
    try:
        x = Decimal(valor(r,"MontoEstimado"))
        return str(x.quantize(Decimal("1"), rounding=ROUND_HALF_UP)) if x.is_finite() else ""
    except (InvalidOperation, ValueError):
        return ""

def convertir(r):
    f = r.get("Fechas") or {}
    c = r.get("Comprador") or {}
    return dict(codigo=valor(r,"CodigoExterno"), nombre=valor(r,"Nombre"),
        estado=valor(r,"Estado"), convocatoria=valor(r,"TipoConvocatoria"),
        fecha_publicacion=valor(f,"FechaPublicacion"), fecha_cierre=valor(f,"FechaCierre"),
        monto_disponible_clp=presupuesto(r), organismo_comprador=valor(c,"NombreOrganismo"),
        region=valor(c,"RegionUnidad"), total_ofertas_recibidas=valor(r,"TotalOfertasRecibidas"),
        motivo_seleccion="", url_detalle="", fecha_sincronizacion="",
        categoria="", subcategoria="", modalidad="Licitación")

class Cliente:
    def __init__(self, ticket, pausa, timeout):
        self.ticket, self.pausa, self.timeout = ticket, pausa, timeout
        self.ultima = 0.0

    def consultar(self, **params):
        params["ticket"] = self.ticket
        url = API + "?" + urllib.parse.urlencode(params)
        for intento in range(5):
            espera = self.pausa - (time.monotonic() - self.ultima)
            if espera > 0:
                time.sleep(espera)
            self.ultima = time.monotonic()
            try:
                req = urllib.request.Request(url, headers={"Accept":"application/json"})
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    data = json.load(response)
                if not isinstance(data, dict) or not isinstance(data.get("Listado"), list):
                    raise ValueError("Respuesta API sin Listado valido")
                return data
            except urllib.error.HTTPError as exc:
                if exc.code not in TRANSIENTES or intento == 4:
                    raise
                print("HTTP_TRANSITORIO", exc.code, "REINTENTO", intento + 1, flush=True)
            except (TimeoutError, urllib.error.URLError):
                if intento == 4:
                    raise
                print("ERROR_RED_REINTENTO", intento + 1, flush=True)
            time.sleep(min(300, 30 * (2 ** intento)))
        raise RuntimeError("Reintentos agotados")

def inicializar(db):
    db.execute("CREATE TABLE IF NOT EXISTS listados (fecha TEXT PRIMARY KEY, cantidad INTEGER, guardado TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS codigos (codigo TEXT PRIMARY KEY)")
    db.execute("CREATE TABLE IF NOT EXISTS detalles (codigo TEXT PRIMARY KEY, json TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS fallos (codigo TEXT PRIMARY KEY, error TEXT)")
    db.commit()

def cargar_listados(db, cliente, desde, hasta):
    fecha = desde
    while fecha <= hasta:
        dia = fecha.isoformat()
        if db.execute("SELECT 1 FROM listados WHERE fecha=?", (dia,)).fetchone():
            print("LISTADO_EXISTENTE", dia, flush=True)
        else:
            datos = cliente.consultar(fecha=fecha.strftime("%d%m%Y"))
            items = datos["Listado"]
            codigos = {valor(x,"CodigoExterno") for x in items if isinstance(x,dict)}
            codigos.discard("")
            with db:
                db.executemany("INSERT OR IGNORE INTO codigos(codigo) VALUES(?)",
                               [(c,) for c in codigos])
                db.execute("INSERT INTO listados VALUES(?,?,?)",
                           (dia,len(items),dt.datetime.now(dt.timezone.utc).isoformat()))
            print("LISTADO_OK", dia, "FILAS", len(items), "CODIGOS", len(codigos), flush=True)
        fecha += dt.timedelta(days=1)

def recuperar(db, cliente, limite):
    pendientes = db.execute("""
        SELECT c.codigo FROM codigos c
        LEFT JOIN detalles d ON d.codigo=c.codigo
        WHERE d.codigo IS NULL ORDER BY c.codigo
    """).fetchall()
    if limite:
        pendientes = pendientes[:limite]
    print("DETALLES_POR_CONSULTAR",len(pendientes),flush=True)
    for i,(codigo,) in enumerate(pendientes,1):
        try:
            respuesta = cliente.consultar(codigo=codigo)
            detalle = next((r for r in respuesta["Listado"]
                            if isinstance(r,dict) and valor(r,"CodigoExterno")==codigo),None)
            if detalle is None:
                raise ValueError("Detalle no encontrado o codigo no coincide")
            with db:
                db.execute("INSERT OR REPLACE INTO detalles VALUES(?,?)",
                           (codigo,json.dumps(detalle,ensure_ascii=False)))
                db.execute("DELETE FROM fallos WHERE codigo=?",(codigo,))
            print("OK",i,codigo,flush=True)
        except Exception as exc:
            with db:
                db.execute("INSERT OR REPLACE INTO fallos VALUES(?,?)",
                           (codigo,type(exc).__name__ + ": " + str(exc)[:120]))
            print("ERROR",i,codigo,type(exc).__name__,flush=True)

def exportar(db, carpeta, mes):
    registros = [convertir(json.loads(x[0])) for x in
                 db.execute("SELECT json FROM detalles ORDER BY codigo")]
    grupos = {
        "procesos_mes.csv":[r for r in registros if r["fecha_publicacion"].startswith(mes)],
        "otros_periodos.csv":[r for r in registros if r["fecha_publicacion"] and not r["fecha_publicacion"].startswith(mes)],
        "sin_fecha.csv":[r for r in registros if not r["fecha_publicacion"]]
    }
    for nombre, filas in grupos.items():
        with (carpeta/nombre).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=COLS)
            w.writeheader()
            w.writerows(filas)
    with (carpeta/"detalles_originales.jsonl").open("w",encoding="utf-8") as f:
        for (raw,) in db.execute("SELECT json FROM detalles ORDER BY codigo"):
            f.write(raw+"\n")
    with (carpeta/"errores.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(["codigo","error"])
        w.writerows(db.execute("SELECT codigo,error FROM fallos ORDER BY codigo"))
    total=db.execute("SELECT COUNT(*) FROM codigos").fetchone()[0]
    informe={"mes":mes,"codigos_unicos_listados":total,
             "detalles_guardados":len(registros),"pendientes":max(0,total-len(registros)),
             "procesos_mes":len(grupos["procesos_mes.csv"]),
             "otros_periodos":len(grupos["otros_periodos.csv"]),
             "sin_fecha":len(grupos["sin_fecha.csv"]),
             "errores":db.execute("SELECT COUNT(*) FROM fallos").fetchone()[0],
             "dias_consultados":db.execute("SELECT COUNT(*) FROM listados").fetchone()[0],
             "escritura_mer":False,"publicacion":False}
    (carpeta/"informe.json").write_text(json.dumps(informe,indent=2,ensure_ascii=False),encoding="utf-8")
    print("INFORME",json.dumps(informe,ensure_ascii=False),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--desde",default="2026-11-01")
    p.add_argument("--hasta",default="2026-11-09")
    p.add_argument("--mes",default="2026-11")
    p.add_argument("--limite",type=int,default=100,help="0 = todos los pendientes")
    p.add_argument("--pausa",type=float,default=10)
    p.add_argument("--timeout",type=int,default=45)
    p.add_argument("--directorio",default=str(Path.home()/"mercadopublico-recuperacion-licitaciones"/"masivo"))
    a=p.parse_args()
    if a.limite<0 or a.pausa<2:
        p.error("limite >= 0; pausa >= 2")
    desde,hasta=dt.date.fromisoformat(a.desde),dt.date.fromisoformat(a.hasta)
    if hasta<desde:
        p.error("Rango de fechas invalido")
    ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
    if not ticket:
        raise SystemExit("BLOQUEO: cargar CHILECOMPRA_TICKET desde el entorno local")
    carpeta=Path(a.directorio).expanduser()
    carpeta.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(carpeta/"checkpoint.sqlite3",timeout=30)
    inicializar(db)
    cliente=Cliente(ticket,a.pausa,a.timeout)
    try:
        cargar_listados(db,cliente,desde,hasta)
        recuperar(db,cliente,a.limite)
    finally:
        exportar(db,carpeta,a.mes)
        db.close()

if __name__=="__main__":
    main()
