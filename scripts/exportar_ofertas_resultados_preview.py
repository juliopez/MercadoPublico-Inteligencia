#!/usr/bin/env python3
"""Genera fragmentos V2 de Ofertas y Resultados en un destino aislado.

Sin API, sin credenciales, sin Google Sheets y sin cambios en frontend-v2/data.
Entrada: JSON con clave tablas -> Ofertas/Resultados como matrices (cabecera + filas).
"""
import argparse,json,pathlib,tempfile,shutil
from importlib.util import spec_from_file_location,module_from_spec

def esquema():
    p=pathlib.Path(__file__).resolve().parent/"importador_historicos_v2.py"
    spec=spec_from_file_location("mer_esquema",p)
    m=module_from_spec(spec);spec.loader.exec_module(m)
    return m.SCHEMA

PUBLIC={
 "Ofertas":("ofertas",("id_cotizacion","codigo","proveedor","monto_ofertado_clp","fecha_oferta","seleccionado")),
 "Resultados":("resultados",("codigo","id_cotizacion_ganadora","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","validado","monto_oferta_seleccionada_clp","estado_verificacion_oc"))
}
def exportar_tablas(tablas,periodo,destino):
    if not isinstance(periodo,str) or len(periodo)!=7 or periodo[4]!="-":raise ValueError("Período inválido")
    schema=esquema()
    dest=pathlib.Path(destino)
    if dest.exists() and any(dest.iterdir()):raise ValueError("Destino debe estar vacío")
    # Cortar antes de escribir si hay datos inválidos.
    salida={};manifest={"periodo":periodo,"conteos":{},"partes":{}}
    for tabla,(entidad,fields) in PUBLIC.items():
        vals=tablas.get(tabla)
        if not isinstance(vals,list) or not vals or vals[0]!=schema[tabla]:
            raise ValueError("Cabecera no coincide: "+tabla)
        cols={x:i for i,x in enumerate(vals[0])}
        unique=set();records=[]
        for raw in vals[1:]:
            if not isinstance(raw,list) or len(raw)>len(cols):raise ValueError("Fila incompatible")
            r=(raw+[""]*len(cols))[:len(cols)]
            d=dict(zip(vals[0],r))
            key=(d["codigo"],d["id_cotizacion"]) if tabla=="Ofertas" else (d["codigo"],d["id_cotizacion_ganadora"])
            if not all(key) or key in unique:raise ValueError("PK vacía o duplicada")
            unique.add(key)
            records.append({f:d[f] for f in fields})
        records.sort(key=lambda x:(x["codigo"],x.get("id_cotizacion",x.get("id_cotizacion_ganadora",""))))
        salida[entidad]=records
    dest.mkdir(parents=True,exist_ok=True)
    for entidad,records in salida.items():
        directory=dest/"partes"/entidad/periodo
        directory.mkdir(parents=True)
        paths=[]
        for n in range(0,len(records),1000):
            fn=f"{n//1000+1:04d}.json"
            (directory/fn).write_text(json.dumps(records[n:n+1000],ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
            paths.append(f"data/partes/{entidad}/{periodo}/{fn}")
        manifest["conteos"][entidad]=len(records)
        manifest["partes"][entidad]=paths
    (dest/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return manifest
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tablas-json",required=True)
    p.add_argument("--periodo",required=True)
    p.add_argument("--destino",required=True)
    a=p.parse_args()
    root=pathlib.Path(__file__).resolve().parents[1]
    output=pathlib.Path(a.destino).resolve()
    if root==output or root in output.parents:
        p.error("Salida aislada fuera del repositorio obligatoria")
    data=json.loads(pathlib.Path(a.tablas_json).read_text(encoding="utf-8"))
    print(json.dumps(exportar_tablas(data,a.periodo,output),ensure_ascii=False))
if __name__=="__main__":main()
