#!/usr/bin/env python3
"""Reparación acotada de 1349 licitaciones importadas del listado V1 del 15-10-2026.
No consulta ChileCompra. No modifica otras filas ni importa ofertas.
"""
import os,json
from google.oauth2.service_account import Credentials
import gspread
STATES={"5":"Publicada","6":"Cerrada","7":"Desierta","8":"Adjudicada","18":"Revocada","19":"Suspendida"}
cred=Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),scopes=["https://www.googleapis.com/auth/spreadsheets"])
ws=gspread.authorize(cred).open_by_key(os.environ["GOOGLE_SHEET_ID"]).worksheet("Procesos")
values=ws.get_all_values()
if values[0][0]!="codigo" or values[0][4]!="fecha_publicacion" or values[0][19]!="modalidad":
    raise SystemExit("Esquema inesperado. Sin escrituras.")
targets=[]
for n,row in enumerate(values[1:],start=2):
    if len(row)>19 and row[19].strip()=="Licitación" and not row[4].strip() and row[0].strip():
        targets.append((n,row))
if len(targets)!=1349:
    raise SystemExit(f"Precondición incumplida: encontrados {len(targets)} de 1349; sin escrituras. Revisar manualmente.")
ops=[]
for n,row in targets:
    code=row[2].strip()
    status=STATES.get(code,"Código "+code if code else "No informado")
    ops.append({"range":f"Procesos!C{n}","values":[[status]]})
    ops.append({"range":f"Procesos!E{n}","values":[["2026-10-15"]]})
print("PLAN_REPARACION filas",len(targets),"fecha_inferida_de_consulta_diaria","2026-10-15",flush=True)
for i in range(0,len(ops),200):
    ws.spreadsheet.values_batch_update({"valueInputOption":"RAW","data":ops[i:i+200]})
check=ws.get_all_values()
bad=[n for n,_ in targets if len(check[n-1])<5 or check[n-1][4]!="2026-10-15" or check[n-1][2].isdigit()]
if bad:raise SystemExit(f"VERIFICACION_FALLIDA {len(bad)} filas")
print("REPARACION_OK",len(targets),"sin_duplicar_procesos",flush=True)
