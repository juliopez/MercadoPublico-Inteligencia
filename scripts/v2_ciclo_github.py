#!/usr/bin/env python3
"""Ciclo único V2 desde GitHub Actions; no programa ejecuciones por sí solo."""
import argparse,json,os,subprocess,sys,time
from datetime import datetime,timezone
import gspread
from google.oauth2.service_account import Credentials

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fecha",required=True)
    p.add_argument("--max-paginas",type=int,default=1)
    p.add_argument("--max-detalles",type=int,default=1)
    p.add_argument("--tope-pagina",type=int,default=496)
    a=p.parse_args()
    if not 0<=a.max_paginas<=2 or not 0<=a.max_detalles<=2 or not 1<=a.tope_pagina<=10000:
        p.error("Máximo 2 páginas, 2 detalles y tope positivo")
    datetime.strptime(a.fecha,"%Y-%m-%d")
    cred=Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets"])
    sheet=gspread.authorize(cred).open_by_key(os.environ["GOOGLE_SHEET_ID"])
    control=sheet.worksheet("ControlV2")
    rows=control.get_all_values()
    if not rows or rows[0][:10]!=["clave","tipo","fecha","pagina","estado","intentos","proximo_intento_utc","http","registros","actualizado_utc"]:
        raise RuntimeError("ControlV2: cabecera incompatible")
    indexed={r[0]:r for r in rows[1:] if r}
    if len(indexed)!=sum(1 for r in rows[1:] if r and r[0]):
        raise RuntimeError("Checkpoints duplicados, detenido")
    now=datetime.now(timezone.utc).isoformat(timespec="seconds")
    pages=[]
    for page in range(1,a.tope_pagina+1):
        r=indexed.get(f"compra_agil:{a.fecha}:pagina:{page}:10",[])
        if len(r)>4 and r[4] in ("completo","revision"):continue
        if len(r)>6 and r[6] and r[6]>now:continue
        pages.append(page)
        if len(pages)>=a.max_paginas:break
    # Si se excluyen los listados, no generar páginas.
    if not a.max_paginas:pages=[]
    commands=[]
    for page in pages:
        commands.append([sys.executable,"scripts/v2_primera_escritura_sheets.py",
                         "--fecha",a.fecha,"--pagina",str(page),"--escribir"])
    for _ in range(a.max_detalles):
        commands.append([sys.executable,"scripts/v2_detalle_sheets.py","--codigo","auto"])
    for i,cmd in enumerate(commands):
        if i:time.sleep(61)
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
        print(p.stdout.strip(),flush=True)
        if p.stderr:print(p.stderr.strip(),file=sys.stderr,flush=True)
        if p.returncode:raise SystemExit(p.returncode)
        # No continuar tras el primer fallo o suspensión de la API.
        log=p.stdout
        if any(k in log for k in ("HTTP_","ERROR_RED","EN_ESPERA","NO_CONSULTA","CIRCUITO_ABIERTO","FRECUENCIA_ESPERA")):
            print("V2_CICLO_PAUSADO: revisar checkpoint; se conserva progreso")
            break
    print("V2_CICLO_FINALIZADO")
if __name__=="__main__":main()
