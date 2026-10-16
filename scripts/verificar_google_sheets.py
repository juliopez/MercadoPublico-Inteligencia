#!/usr/bin/env python3
"""Verificación de SOLO LECTURA de la cuenta de servicio contra Google Sheets."""
import json
import os
import sys

import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
if not raw or not sheet_id:
    sys.exit("CONFIG_ERROR: faltan GOOGLE_SERVICE_ACCOUNT_JSON o GOOGLE_SHEET_ID")
try:
    identity = json.loads(raw)
except json.JSONDecodeError:
    sys.exit("CONFIG_ERROR: GOOGLE_SERVICE_ACCOUNT_JSON no contiene JSON válido")
if not isinstance(identity, dict) or not identity.get("client_email") or not identity.get("private_key"):
    sys.exit("CONFIG_ERROR: credencial JSON incompleta")

try:
    credentials = Credentials.from_service_account_info(
        identity, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    client = gspread.authorize(credentials)
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.worksheet("Procesos")
    header = sheet.row_values(1)
    expected = ["codigo", "nombre", "estado", "convocatoria", "fecha_publicacion",
                "fecha_cierre", "fecha_ultimo_cambio", "monto_disponible_clp",
                "organismo_comprador", "rut_organismo", "unidad_compra", "region",
                "total_ofertas_recibidas", "motivo_seleccion", "url_detalle"]
    if header[:15] != expected:
        sys.exit("SCHEMA_ERROR: los 15 encabezados originales no coinciden")
    print("AUTH_OK: cuenta de servicio autenticada correctamente")
    print("SHEET_OK: archivo y pestaña Procesos accesibles")
    print("HEADERS_OK: 15 columnas originales verificadas")
    print("COLUMNA_SINCRONIZACION_PRESENTE:", "fecha_sincronizacion" in header)
    print("LECTURA_OK: ninguna celda fue modificada")
except (SpreadsheetNotFound, WorksheetNotFound):
    sys.exit("ACCESS_ERROR: no se encuentra el libro o la pestaña; compruebe permisos e ID")
except APIError as error:
    print("API_ERROR: verifique acceso a Sheets API y permisos. HTTP",error.response.status_code)
    sys.exit(1)
