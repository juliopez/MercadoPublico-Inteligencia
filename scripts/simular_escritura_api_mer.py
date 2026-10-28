#!/usr/bin/env python3
"""Prepara un plan de escritura MER desde una transformación guardada; SOLO LECTURA.

Entrada: JSON transformado y snapshots JSON de Ofertas, Resultados y Proveedores.
No importa gspread, no consume API, no tiene opción de aplicar escrituras.
"""
import argparse,json,sys
from pathlib import Path
from planificar_upsert_api_mer import planificar
from resolver_proveedores_ofertas_mer import resolver_ofertas
from adaptar_detalle_compra_agil_mer import OFERTAS,RESULTADOS

def preparar(transformacion,tablas):
    if not isinstance(transformacion,dict):raise ValueError("Transformación inválida")
    ofertas=transformacion.get("ofertas")
    resultados=transformacion.get("resultados")
    if not isinstance(ofertas,list) or not isinstance(resultados,list):raise ValueError("Filas inválidas")
    if set(tablas)!={"Ofertas","Resultados","Proveedores"}:raise ValueError("Tablas requeridas no disponibles")
    cod=transformacion.get("codigo")
    if not cod or any(x.get("codigo")!=cod for x in ofertas+resultados):raise ValueError("Código inconsistente")
    res=resolver_ofertas(ofertas,tablas["Proveedores"])
    plans={}
    for name,new in (("Ofertas",res["ofertas"]),("Resultados",resultados)):
        plan=planificar(name,tablas[name],new)
        plans[name]={"nuevos":len(plan["insertar"]),"actualizaciones":len(plan["actualizar"]),
                     "sin_cambios":plan["sin_cambios"],"conflictos":len(plan["conflictos"])}
    return {"modo":"SOLO_LECTURA","codigo":cod,
            "identidad_resuelta":res["identidad_resuelta"],
            "identidad_pendiente":res["sin_identidad"],"tablas":plans,
            "aplicable":False,"razon":"Plan de diagnóstico; falta backup, lock y escritura verificada"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transformacion",required=True)
    p.add_argument("--snapshot",required=True,help="JSON de cabeceras y filas de tres tablas")
    a=p.parse_args()
    result=preparar(json.loads(Path(a.transformacion).read_text()),
                    json.loads(Path(a.snapshot).read_text()))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
