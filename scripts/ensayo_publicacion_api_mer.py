#!/usr/bin/env python3
"""Ensayo de publicación completo y sintético, sin APIs ni Google Sheets de producción."""
import json,pathlib,tempfile
from exportar_ofertas_resultados_preview import exportar_tablas,esquema

def ejecutar():
    schema=esquema()
    oferta={k:"" for k in schema["Ofertas"]}
    oferta.update(id_cotizacion="TEST-API-0001",codigo="TEST-20261028-COT26",proveedor="PROVEEDOR FICTICIO",seleccionado="1")
    resultado={k:"" for k in schema["Resultados"]}
    resultado.update(codigo="TEST-20261028-COT26",id_cotizacion_ganadora="TEST-API-0001",validado="NO: ENSAYO")
    tablas={n:[schema[n],[row[k] for k in schema[n]]] for n,row in (("Ofertas",oferta),("Resultados",resultado))}
    with tempfile.TemporaryDirectory() as d:
        base=pathlib.Path(d)/"data"
        manifest=exportar_tablas(tablas,"2026-10",base)
        if manifest["conteos"]!={"ofertas":1,"resultados":1}:raise ValueError("Conteos no coinciden")
        # Contrato idéntico al catálogo de Pages, pero solo en directorio temporal.
        catalog={"version":"2.0","periodos":[{"periodo":"2026-10","conteos":manifest["conteos"],"partes":manifest["partes"]}]}
        for entity,paths in manifest["partes"].items():
            rows=0
            for path in paths:
                f=base/path.removeprefix("data/")
                if not f.exists():raise ValueError("Falta fragmento: "+path)
                records=json.loads(f.read_text())
                if not isinstance(records,list):raise ValueError("Fragmento inválido")
                rows+=len(records)
            if rows!=catalog["periodos"][0]["conteos"][entity]:raise ValueError("Integridad fallida")
        print(json.dumps({"estado":"PREVIEW_VERIFICADA","conteos":manifest["conteos"],
                          "api":False,"sheets_produccion":False,"pages":False}))
if __name__=="__main__":ejecutar()
