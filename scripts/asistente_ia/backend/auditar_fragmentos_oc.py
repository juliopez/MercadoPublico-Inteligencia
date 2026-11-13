#!/usr/bin/env python3
"""Auditoría local de solo lectura: catálogo, fragmentos OC y agregados. No reescribe archivos."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "frontend-v2"
CATALOGO = ROOT / "data/catalogo-publico.json"


def main():
    catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))
    resultados = []
    for item in catalogo["periodos"]:
        periodo = item["periodo"]
        partes = item["partes"]["ordenescompra"]
        filas = 0
        faltantes = []
        for ruta in partes:
            if not ruta.startswith(f"data/partes/ordenescompra/{periodo}/") or ".." in Path(ruta).parts:
                raise ValueError(f"Ruta de fragmento no permitida: {ruta}")
            archivo = ROOT / ruta
            if not archivo.is_file():
                faltantes.append(ruta)
                continue
            datos = json.loads(archivo.read_text(encoding="utf-8"))
            if not isinstance(datos, list):
                raise ValueError(f"Fragmento no es lista: {ruta}")
            filas += len(datos)
        esperado = item["conteos"]["ordenescompra"]
        agregado_path = ROOT / f"data/analitica/{periodo}/ordenescompra.json"
        agregado = json.loads(agregado_path.read_text(encoding="utf-8"))
        registro = {
            "periodo": periodo,
            "fragmentos": len(partes),
            "faltantes": len(faltantes),
            "filas_fragmentos": filas,
            "catalogo": esperado,
            "agregado": agregado["registros"],
            "delta_fragmentos_catalogo": filas - esperado,
            "delta_agregado_catalogo": agregado["registros"] - esperado,
            "delta_fragmentos_agregado": filas - agregado["registros"],
        }
        resultados.append(registro)
        print(json.dumps(registro, ensure_ascii=False))
        if faltantes:
            print(json.dumps({"periodo": periodo, "faltantes_ejemplo": faltantes[:5]}, ensure_ascii=False))
    print("RESUMEN", json.dumps({"periodos": len(resultados), "fragmentos_igual_catalogo": sum(r["delta_fragmentos_catalogo"] == 0 and r["faltantes"] == 0 for r in resultados), "fragmentos_igual_agregado": sum(r["delta_fragmentos_agregado"] == 0 and r["faltantes"] == 0 for r in resultados)}, ensure_ascii=False))
    if any(r["faltantes"] or r["delta_fragmentos_catalogo"] or r["delta_fragmentos_agregado"] for r in resultados):
        sys.exit(1)


if __name__ == "__main__":
    main()
