#!/usr/bin/env python3
"""Benchmark aislado con fragmentos públicos reales; nunca escribe en frontend-v2."""
import argparse
import json
import resource
import tempfile
import time
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

REPO=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("indexador",REPO/"scripts/indexar_busqueda_frontend_v2.py")
module=module_from_spec(spec);spec.loader.exec_module(module)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--periodo",default="2026-06")
    ap.add_argument("--entidad",default="ofertas")
    ap.add_argument("--fragmentos",type=int,default=50)
    args=ap.parse_args()
    catalog=json.loads((REPO/"frontend-v2/data/catalogo-publico.json").read_text(encoding="utf8"))
    entry=next(p for p in catalog["periodos"] if p["periodo"]==args.periodo)
    paths=entry["partes"][args.entidad][:args.fragmentos]
    count=0
    # Solo se leen los fragmentos públicos que forman la muestra; no se alteran.
    for rel in paths:
        count+=len(json.loads((REPO/"frontend-v2"/rel).read_text(encoding="utf8")))
    with tempfile.TemporaryDirectory(prefix="benchmark-real-v2-") as tmp:
        root=Path(tmp)
        (root/"data").mkdir()
        (root/"data"/"partes").symlink_to(REPO/"frontend-v2/data/partes",target_is_directory=True)
        sample={"periodos":[{"periodo":args.periodo,"conteos":{args.entidad:count},"partes":{args.entidad:paths}}]}
        (root/"data/catalogo-publico.json").write_text(json.dumps(sample),encoding="utf8")
        start=time.monotonic()
        module.build(args.periodo,args.entidad,root)
        elapsed=round(time.monotonic()-start,3)
        output=root/"data/busqueda"/args.periodo/args.entidad
        files=list(output.glob("*.json"))
        metrics={"tipo":"benchmark_historico_muestra","periodo":args.periodo,"entidad":args.entidad,
                 "fragmentos":len(paths),"registros":count,"segundos":elapsed,
                 "archivos":len(files),"bytes_total":sum(f.stat().st_size for f in files),
                 "bytes_mayor_archivo":max((f.stat().st_size for f in files),default=0),
                 "memoria_maxima_kb":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        print(json.dumps(metrics,ensure_ascii=False))
if __name__=="__main__":
    main()
