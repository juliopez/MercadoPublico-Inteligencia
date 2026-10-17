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
        if name!="Control" and len(header)!=len(set(header)):
            raise RuntimeError(f"{name}: cabeceras repetidas")
        if name=="Control" and header[:2]!=["variable","valor"]:
            raise RuntimeError("Control!A1:B1 no coincide con variable, valor")
        missing=necessary-(set(header[:2]) if name=="Control" else set(header))
        if missing:raise RuntimeError(f"{name}: faltan {sorted(missing)}")
        print(f"OK {name}: {len(header)} columnas; {sh.row_count} filas de capacidad")
    try:
        dedicated=book.worksheet("ControlV2")
    except gspread.WorksheetNotFound:
        print("ControlV2: aún no existe; se creará al habilitar la escritura V2")
    else:
        print(f"ControlV2: ya existe, {dedicated.col_count} columnas")
    print("PREFLIGHT_V2_OK: autenticación y esquemas validados; 0 escrituras, 0 llamadas ChileCompra")
if __name__=="__main__":
    try: main()
    except Exception as e:
        print("PREFLIGHT_V2_ERROR:",str(e),file=sys.stderr)
        sys.exit(1)
