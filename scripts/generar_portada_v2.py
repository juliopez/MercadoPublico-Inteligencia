#!/usr/bin/env python3
"""Genera la portada oficial V2 en la raíz de Pages sin duplicar los JSON.

El código y los datos permanecen bajo frontend-v2/ para no romper consultas
existentes (incluida la verificación de catálogo de la API nocturna).
"""
from pathlib import Path
import argparse

HEAD = '<head><meta charset="utf-8">'
TAIL = '</body>'
BASE = '<base href="./frontend-v2/">'
NAVIGATION = """<script>
// Resolver anclas dentro de la misma portada: <base> solo rige recursos y fetch.
document.addEventListener('click',event=>{
 const a=event.target.closest('a[href^="#"]');
 if(!a)return;
 const hash=a.getAttribute('href');
 if(!hash||hash==='#')return;
 const target=document.getElementById(decodeURIComponent(hash.slice(1)));
 if(!target)return;
 event.preventDefault();
 history.replaceState(null,'',location.pathname+location.search+hash);
 target.scrollIntoView({behavior:'smooth',block:'start'});
});
</script>
"""

def render(source):
    if HEAD not in source or TAIL not in source:
        raise ValueError("V2 no contiene las anclas HTML esperadas")
    if BASE in source:
        raise ValueError("V2 original ya contiene base; revisar antes de duplicar")
    if 'DESARROLLO</span>' in source:
        raise ValueError("No publicar una portada marcada como desarrollo")
    return source.replace(HEAD, HEAD + BASE, 1).replace(TAIL, NAVIGATION + TAIL, 1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--origen", default="frontend-v2/index.html")
    p.add_argument("--salida", default="_pages/index.html")
    a=p.parse_args()
    source=Path(a.origen).read_text(encoding="utf-8")
    result=render(source)
    dest=Path(a.salida)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(result, encoding="utf-8")
    print("PORTADA_V2_GENERADA", dest, "bytes",len(result.encode("utf-8")))

if __name__=="__main__":
    main()
