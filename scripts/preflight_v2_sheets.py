#!/usr/bin/env python3
"""Prevalidación de Google Sheets para el nuevo ETL V2; solo lectura y sin API ChileCompra."""
import json
import os
import sys
import gspread
from google.oauth2.service_account import Credentials

REQUIRED={
 "Procesos":{"codigo","nombre","fecha_publicacion","modalidad"},
 "Ofertas":{"codigo","proveedor","monto_ofertado_clp","id_cotizacion"},
 "Resultados":{"codigo","adjudicatario","validado"},
 "Control":{"variable","valor"},
}
def main():
    raw=os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON","")
    sheet_id=os.environ.get("GOOGLE_SHEET_ID","")
    if not raw or not sheet_id:raise RuntimeError("Faltan credenciales o ID de Sheet")
    info=json.loads(raw)
    cred=Credentials.from_service_account_info(info,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    book=gspread.authorize(cred).open_by_key(sheet_id)
    for name,necessary in REQUIRED.items():
        sh=book.worksheet(name)
        header=sh.row_values(1)
        if len(header)!=len(set(header)):
            raise RuntimeError(f"{name}: cabeceras repetidas")
        missing=necessary-set(header)
        if missing:raise RuntimeError(f"{name}: faltan {sorted(missing)}")
        print(f"OK {name}: {len(header)} columnas; {sh.row_count} filas de capacidad")
    control=book.worksheet("Control")
    # Reservar solo tras constatar que el rango no contenga datos.
    occupied=control.get("U1:AD15")
    if any(str(cell).strip() for row in occupied for cell in row):
        print("AVISO: Control!U1:AD15 contiene datos; no reservar ni sobrescribir")
        raise RuntimeError("No es seguro usar la zona candidata de checkpoints")
    print("OK zona candidata Control!U1:AD15 libre (comprobación parcial, sin reserva)")
    print("PREFLIGHT_V2_OK: autenticación, esquemas y zona candidata; 0 escrituras, 0 llamadas ChileCompra")
if __name__=="__main__":
    try: main()
    except Exception as e:
        print("PREFLIGHT_V2_ERROR:",str(e),file=sys.stderr)
        sys.exit(1)
