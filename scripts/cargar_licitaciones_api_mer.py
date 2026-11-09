#!/usr/bin/env python3
"""Carga verificada de licitaciones API en MER operativo. No toca otras pestañas."""
import argparse
import csv
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
ZONE=ZoneInfo("America/Santiago")

def cargar_modulo():
    spec=importlib.util.spec_from_file_location("etl_zip",ROOT/"scripts/etl_zip_dos_fuentes.py")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",required=True,type=Path)
    p.add_argument("--aplicar",action="store_true")
    p.add_argument("--salida",default="salida_operativa")
    a=p.parse_args()
    mes=dt.datetime.now(ZONE).strftime("%Y-%m")
    config=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
    destino=config["periodos"].get(mes)
    if not destino or destino.get("tipo")!="operativo":
        raise SystemExit("BLOQUEO: no existe MER operativo para "+mes)
    mod=cargar_modulo()
    cols=mod.importar().SCHEMA["Procesos"]
    with a.csv.open(encoding="utf-8-sig",newline="") as f:
        lector=csv.DictReader(f)
        if lector.fieldnames!=cols:raise ValueError("Contrato CSV incompatible")
        rows={}
        for r in lector:
            codigo=r["codigo"].strip().upper()
            if not codigo or not r["fecha_publicacion"].startswith(mes):
                raise ValueError("Codigo o periodo invalido en CSV")
            if codigo in rows:raise ValueError("PK duplicada en CSV: "+codigo)
            rows[codigo]=[r[c] for c in cols]
    if not rows:
        print("SIN_LICITACIONES_DEL_MES; MER no modificado",flush=True)
        return
    if not a.aplicar:
        print("SIMULACION filas="+str(len(rows)),flush=True)
        return
    import gspread
    from google.oauth2.service_account import Credentials
    cred=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS","")
    if not cred or not Path(cred).is_file():
        raise RuntimeError("Credencial Google local no disponible")
    auth=Credentials.from_service_account_file(cred,scopes=["https://www.googleapis.com/auth/spreadsheets"])
    book=gspread.authorize(auth).open_by_key(destino["id"])
    ws=book.worksheet("Procesos")
    current=mod.solicitud_con_reintentos(lambda:mod.worksheet_rows(ws,cols),"Procesos lectura")
    # Preservar registros existentes y sus campos enriquecidos; solo insertar PK nuevas.
    pendientes={k:v for k,v in rows.items() if k not in current}
    nuevos=len(pendientes)
    modificados=0
    # El contrato exige respaldo completo de las seis pestañas, no solo Procesos.
    projected=sum(x.row_count*x.col_count for x in book.worksheets())
    if projected+nuevos*len(cols)>10_000_000:
        raise ValueError("Limite de celdas excedido")
    if not pendientes:
        print("SIN_NUEVOS_PROCESOS; datos existentes preservados",flush=True)
        return
    respaldo=mod.respaldo_local(book,mod.importar().SCHEMA,mes)
    print("RESPALDO_VERIFICADO",respaldo["archivo"],flush=True)
    aplicados=mod.aplicar_tabla(ws,cols,sorted(pendientes.items()),current)
    after=mod.solicitud_con_reintentos(lambda:mod.worksheet_rows(ws,cols),"Procesos verificacion")
    if len(after)!=len(current)+nuevos:
        raise ValueError("Cantidad de PK posterior no coincide")
    for codigo,row in pendientes.items():
        if codigo not in after or after[codigo][1]!=row:
            raise ValueError("Lectura posterior incorrecta: "+codigo)
    out=ROOT/a.salida
    out.mkdir(parents=True,exist_ok=True)
    reporte={"periodo":mes,"fuente":"API_licitaciones_v1","estado":"CARGA_VERIFICADA",
             "fecha_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
             "filas_fuente":len(rows),"nuevos":nuevos,"modificados":modificados,
             "aplicados":aplicados,"respaldo":respaldo}
    (out/"licitaciones_api_carga.json").write_text(json.dumps(reporte,indent=2,ensure_ascii=False),encoding="utf-8")
    print("CARGA_LICITACIONES_API_VERIFICADA",json.dumps(reporte,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
