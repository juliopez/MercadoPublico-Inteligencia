#!/usr/bin/env python3
"""Plan de consolidación MER v2 (sin conectarse a Sheets ni publicar JSON).

Lee el catálogo y selecciona exactamente una hoja por período.
Solo incluye históricos auditados + hoja operativa del mes vigente en Santiago.
"""
import argparse, datetime as dt, json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
def plan(catalogo,periodo_actual):
    periodos=catalogo["periodos"]
    out=[]
    for mes,item in sorted(periodos.items()):
        if mes>periodo_actual:continue
        tipo=item.get("tipo")
        if tipo=="historico":
            if "auditad" not in item.get("estado","").lower():continue
        elif tipo=="operativo":
            if mes!=periodo_actual:continue
        else:continue
        if not item.get("id"):raise ValueError("Falta ID: "+mes)
        out.append({"periodo":mes,"tipo":tipo,"spreadsheet_id":item["id"],"estado":item.get("estado")})
    if not out:raise ValueError("Ningún período elegible")
    if len({x["periodo"] for x in out})!=len(out):raise ValueError("Períodos duplicados")
    return out
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--salida",default="salida_operativa/plan_consolidacion.json")
    args=parser.parse_args()
    now=dt.datetime.now(ZoneInfo("America/Santiago"))
    catalogo=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf8"))
    selected=plan(catalogo,now.strftime("%Y-%m"))
    objeto={"creado_chile":now.isoformat(),"modo":"PLAN_SOLO_LECTURA",
            "periodo_vigente":now.strftime("%Y-%m"),"archivos":selected,
            "tablas_frontend":["procesos","ofertas","resultados","ordenescompra"],
            "regla":"Seleccionar por catálogo, no carpeta; hojas futuras y períodos operativos pasados excluidos"}
    path=Path(args.salida);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(obj,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
