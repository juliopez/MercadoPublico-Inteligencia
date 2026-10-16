#!/usr/bin/env python3
"""Prueba reversible de escritura de Google Sheets usando hoja temporal exclusiva."""
import json
import os
import sys
from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import WorksheetNotFound

raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
if not raw or not sheet_id:
    sys.exit("CONFIG_ERROR: faltan credenciales Google o ID de Sheets")
try:
    info = json.loads(raw)
    credentials = Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
except (ValueError, KeyError) as error:
    sys.exit("CONFIG_ERROR: credencial JSON inválida")

client = gspread.authorize(credentials)
workbook = client.open_by_key(sheet_id)
name = "Prueba_Conexion"
try:
    workbook.worksheet(name)
except WorksheetNotFound:
    pass
else:
    sys.exit("SAFEGUARD: ya existe Prueba_Conexion. No modificar ni eliminar hoja ajena.")

created = None
try:
    created = workbook.add_worksheet(title=name, rows=5, cols=3)
    stamp = datetime.now(timezone.utc).isoformat()
    expected = [["prueba", "fecha_utc", "resultado"], ["gitHub_actions", stamp, "ESCRITURA_OK"]]
    created.update(range_name="A1:C2", values=expected, value_input_option="RAW")
    actual = created.get("A1:C2")
    if actual != expected:
        raise RuntimeError("VERIFY_ERROR: los valores leídos no coinciden con lo escrito")
    print("WRITE_OK: hoja temporal creada y fila escrita")
    print("READ_BACK_OK: los valores coinciden exactamente")
finally:
    if created is not None:
        workbook.del_worksheet(created)
        print("CLEANUP_OK: hoja temporal eliminada")
print("FIN_OK: otras pestañas no modificadas")
