#!/usr/bin/env python3
"""Benchmark reproducible de índice v2: solo datos sintéticos, sin Sheets."""
import json
import resource
import tempfile
import time
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/indexar_busqueda_frontend_v2.py"
spec=spec_from_file_location("indice_v2",SCRIPT)
mod=module_from_spec(spec)
spec.loader.exec_module(mod)

def main():
    n=20000
    with tempfile.TemporaryDirectory(prefix="busqueda-v2-bench-") as tmp:
        root=Path(tmp)
        parts=[]
        for block in range((n+999)//1000):
            folder=root/"data"/"partes"/"procesos"/"2026-06"
            folder.mkdir(parents=True,exist_ok=True)
            name=f"{block+1:04d}.json"
            records=[{"codigo":f"1000-{block*1000+i}-LE26",
                      "nombre":f"Capacitación digital y servicios tecnológicos programa {i%19}",
                      "organismo_comprador":f"Municipalidad de Santiago departamento {i%15}"}
                     for i in range(min(1000,n-block*1000))]
            (folder/name).write_text(json.dumps(records,ensure_ascii=False),encoding="utf-8")
            parts.append(f"data/partes/procesos/2026-06/{name}")
        manifest={"periodos":[{"periodo":"2026-06","conteos":{"procesos":n},"partes":{"procesos":parts}}]}
        (root/"data"/"catalogo-publico.json").write_text(json.dumps(manifest),encoding="utf-8")
        started=time.monotonic()
        mod.build("2026-06","procesos",root)
        elapsed=round(time.monotonic()-started,3)
        output=root/"data"/"busqueda"/"2026-06"/"procesos"
        files=list(output.glob("*.json"))
        total=sum(p.stat().st_size for p in files)
        largest=max((p.stat().st_size for p in files),default=0)
        meta=json.loads((output/"meta.json").read_text(encoding="utf-8"))
        assert meta["conteo"]==n
        assert meta["formato"]=="referencias_fragmento_fila"
        print(json.dumps({"tipo":"benchmark_sintetico","filas":n,"segundos":elapsed,
                          "archivos":len(files),"bytes_total":total,
                          "bytes_mayor_archivo":largest,
                          "memoria_maxima_kb":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
                         ensure_ascii=False))
if __name__=="__main__":
    main()
