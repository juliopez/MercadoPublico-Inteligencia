#!/usr/bin/env python3
"""Verificación aislada del contrato frontend-v2 mediante datos sintéticos; sin API, sin Pages."""
import json, pathlib, tempfile
from exportar_ofertas_resultados_preview import exportar_tablas,esquema

def ejecutar():
    schema=esquema()
    o={k:"" for k in schema["Ofertas"]}
    o.update({"id_cotizacion":"TEST-API-0001","codigo":"TEST-20261028-COT26",
      "proveedor":"PROVEEDOR FICTICIO - ENSAYO","fecha_oferta":"2026-10-28",
      "seleccionado":"1","fuente":"SIMULACION"})
    r={k:"" for k in schema["Resultados"]}
    r.update({"codigo":"TEST-20261028-COT26","id_cotizacion_ganadora":"TEST-API-0001",
      "fuente":"SIMULACION","validado":"NO: ENSAYO","estado_verificacion_oc":"NO VERIFICADA"})
    tablas={n:[schema[n],[d[k] for k in schema[n]]] for n,d in (("Ofertas",o),("Resultados",r))}
    with tempfile.TemporaryDirectory(prefix="mer_preview_aislado_") as tmp:
        root=pathlib.Path(tmp)
        manifest=exportar_tablas(tablas,"2026-10",root/"preview")
        assert manifest["conteos"]=={"ofertas":1,"resultados":1}
        for entity in ("ofertas","resultados"):
            for rel in manifest["partes"][entity]:
                # Rutas de catálogo deben coincidir exactamente con el contrato del frontend.
                assert rel.startswith(f"data/partes/{entity}/2026-10/")
                f=root/"preview"/rel.removeprefix("data/")
                assert f.exists(),rel
                rows=json.loads(f.read_text())
                assert len(rows)==1
                for record in rows:
                    assert "rut_proveedor_cot" not in record
                    assert "id_proveedor" not in record
                    assert "fuente" not in record
        print(json.dumps({"estado":"PREVIEW_AISLADO_VALIDADO","conteos":manifest["conteos"],
                          "publicado_en_pages":False,"api_consultada":False}))
if __name__=="__main__":ejecutar()
