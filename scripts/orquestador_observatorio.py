#!/usr/bin/env python3
"""Coordinación única: V1, resultados, OC, V2. Persistencia de etapa en ControlV2."""
import json,os,subprocess,sys
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
import gspread
from google.oauth2.service_account import Credentials

def ts():return datetime.now(timezone.utc).isoformat(timespec="seconds")
def main():
    creds=Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets"])
    wb=gspread.authorize(creds).open_by_key(os.environ["GOOGLE_SHEET_ID"])
    ws=wb.worksheet("ControlV2")
    rows=ws.get_all_values()
    required=["clave","tipo","fecha","pagina","estado","intentos","proximo_intento_utc","http","registros","actualizado_utc"]
    if not rows or rows[0][:10]!=required:raise RuntimeError("ControlV2 incompatible")
    records={}
    for i,r in enumerate(rows[1:],2):
        if r and r[0]:
            if r[0] in records:raise RuntimeError("Checkpoint duplicado "+r[0])
            records[r[0]]=(i,r)
    today=datetime.now(ZoneInfo("America/Santiago")).date()
    origin=datetime.strptime(os.getenv("ORQUESTADOR_FECHA_INICIAL","2026-10-15"),"%Y-%m-%d").date()
    if origin>=today:
        print("ORQUESTADOR_SIN_FECHAS_CERRADAS");return
    steps=[
        ("licitaciones_v1",["scripts/sync_chilecompra_sheets.py"],{"SYNC_MODALIDAD":"licitaciones"}),
        ("resultados_v1",["scripts/sync_resultados_licitaciones.py"],{}),
        ("ordenes_compra",["scripts/sync_ordenes_compra_sheets.py"],{})
    ]
    def update(key,kind,day,state,attempts,due="",status=""):
        row=[key,kind,day,"",state,attempts,due,status,"",ts()]
        if key in records:
            i,_=records[key];ws.update(range_name=f"A{i}:J{i}",values=[row],value_input_option="RAW")
        else:
            ws.append_row(row,value_input_option="RAW",table_range="A:J")
            i=len(ws.col_values(1));records[key]=(i,row)
        records[key]=(i,row)
    failures=0
    rate_limited=False
    for name,cmd,extra in steps:
        selected=None
        day=origin
        while day<today:
            label=day.isoformat();key=f"orquestador:{name}:{label}"
            prior=records.get(key,(None,[]))[1]
            if len(prior)>4 and prior[4] in ("completo","revision"):
                day+=timedelta(days=1);continue
            if len(prior)>6 and prior[6] and prior[6]>ts():
                # Procesamiento cronológico: no saltar una fecha en espera.
                print("ORQUESTADOR_ESPERA",name,label,prior[6]);break
            selected=(label,key,prior);break
        if not selected:
            print("ORQUESTADOR_ETAPA_AL_DIA",name);continue
        label,key,prior=selected
        count=int(prior[5]) if len(prior)>5 and prior[5] else 0
        env={**os.environ,**extra,"SYNC_FECHA_2026":label,"API_MAX_ATTEMPTS":"1"}
        # Sin bucles ni reintentos internos de orquestación.
        try:
            result=subprocess.run([sys.executable,*cmd],env=env,text=True,
                                  capture_output=True,timeout=600)
            print(f"ORQUESTADOR_ETAPA {name} {label} rc={result.returncode}")
            if result.stdout:print(result.stdout[-4500:])
            if result.stderr:print(result.stderr[-1500:],file=sys.stderr)
            ok=result.returncode==0
            rate_hit=("HTTP 429" in (result.stdout+"\n"+result.stderr) or
                      "Too Many Requests" in (result.stdout+"\n"+result.stderr) or
                      result.returncode==75)
            status="75" if rate_hit else str(result.returncode)
        except subprocess.TimeoutExpired:
            print("ORQUESTADOR_TIEMPO_AGOTADO",name,label)
            ok=False;status="timeout"
        if ok:
            update(key,name,label,"completo",count+1,status=status)
        else:
            failures+=1
            pause=3600 if status=="75" else min(3600,300*2**min(count,3))
            due=(datetime.now(timezone.utc)+timedelta(seconds=pause)).isoformat(timespec="seconds")
            update(key,name,label,"espera",count+1,due,status)
            print("ORQUESTADOR_ETAPA_DIFERIDA",name,label,due)
            if status=="75":
                rate_limited=True
                print("ORQUESTADOR_429: detener consultas adicionales de API en este ciclo")
                break
    # V2 usa su propia selección de fechas, checkpoints y circuit breaker.
    # Si hay HTTP 429 de V1/OC, se aplaza V2 en esta ejecución.
    else:
        result=subprocess.run([sys.executable,"scripts/v2_ciclo_github.py",
                                "--fecha","auto","--max-paginas","1","--max-detalles","1"],
                              text=True,capture_output=True,timeout=360)
        if result.stdout:print(result.stdout[-6000:])
        if result.stderr:print(result.stderr[-2000:],file=sys.stderr)
        if result.returncode:failures+=1
    print("ORQUESTADOR_FIN errores_componentes=",failures, "rate_limited=",rate_limited)
    if failures:print("ORQUESTADOR_RESULTADO_PARCIAL: fuente(s) pendiente(s); JSON publicable conserva datos previos")
    # Una falla de una fuente no impide publicar información ya confirmada en Sheets.
if __name__=="__main__":main()
