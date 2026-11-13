#!/usr/bin/env python3
"""Regenera exclusivamente agregados ausentes o desfasados. No modifica fuentes MER."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from generar_analitica_v2 import build  # noqa: E402

DATA = ROOT / "frontend-v2/data"
ENTIDADES = ("procesos", "ofertas", "resultados", "ordenescompra")


def main():
    catalogo = json.loads((DATA / "catalogo-publico.json").read_text(encoding="utf8"))
    reparados = []
    for item in catalogo["periodos"]:
        periodo = item["periodo"]
        for entidad in ENTIDADES:
            esperado = item["conteos"][entidad]
            archivo = DATA / "analitica" / periodo / (entidad + ".json")
            actual = None
            if archivo.is_file():
                try:
                    actual = json.loads(archivo.read_text(encoding="utf8"))
                except (ValueError, OSError):
                    pass
            if (not isinstance(actual, dict) or actual.get("registros") != esperado
                    or actual.get("periodo") != periodo or actual.get("entidad") != entidad):
                print("REGENERAR", periodo, entidad, "esperado", esperado, flush=True)
                build(periodo, entidad)
                reparados.append((periodo, entidad))
            nuevo = json.loads(archivo.read_text(encoding="utf8"))
            if (nuevo.get("registros") != esperado or nuevo.get("periodo") != periodo
                    or nuevo.get("entidad") != entidad
                    or not isinstance(nuevo.get("monto_total_clp"), int)
                    or nuevo["monto_total_clp"] < 0
                    or not isinstance(nuevo.get("registros_con_monto"), int)
                    or not 0 <= nuevo["registros_con_monto"] <= esperado):
                raise ValueError(f"Agregado inválido: {periodo}/{entidad}")
            print("VERIFICADO", periodo, entidad, esperado, flush=True)
    print("RESUMEN", json.dumps({"verificados":len(catalogo["periodos"])*len(ENTIDADES),"regenerados":reparados},ensure_ascii=False))


if __name__ == "__main__":
    main()
