#!/usr/bin/env python3
"""Exporta una instantánea pública de solo lectura desde Google Sheets privado."""
import json,os
from datetime import datetime,timezone
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

NAMES=("Procesos","Ofertas","Resultados")
# Lista explícita: no se publica RUT, identificadores internos de OC, metadatos de control ni credenciales.
PUBLIC={
"Procesos":("codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre","monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas","motivo_seleccion","url_detalle","categoria","subcategoria","modalidad"),
"Ofertas":("codigo","proveedor","monto_ofertado_clp","fecha_oferta","estado_oferta","seleccionado","id_cotizacion"),
"Resultados":("codigo","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","validado","id_cotizacion_ganadora","monto_oferta_seleccionada_clp","estado_verificacion_oc")
}
def main():
    sa=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    cred=Credentials.from_service_account_info(sa,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    book=gspread.authorize(cred).open_by_key(os.environ["GOOGLE_SHEET_ID"])
    result={"fecha_actualizacion":datetime.now(timezone.utc).isoformat(),"fuente":"Google Sheets privado, extracto publicado","tablas":{}}
    for name in NAMES:
        values=book.worksheet(name).get_all_values()
        if not values: raise RuntimeError("Hoja vacía: "+name)
        heads=values[0]
        needed=PUBLIC[name]
        absent=[col for col in needed if col not in heads]
        if absent:raise RuntimeError(f"Faltan columnas en {name}: {absent}")
        indices=[heads.index(col) for col in needed]
        result["tablas"][name.lower()]=[
          {key:(row[i] if i<len(row) else "") for key,i in zip(needed,indices)}
          for row in values[1:] if row and row[0].strip()
        ]
    output=Path("data/observatorio.json")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EXPORTACION_OK",*(f"{k}={len(v)}" for k,v in result["tablas"].items()))
if __name__=="__main__":main()
