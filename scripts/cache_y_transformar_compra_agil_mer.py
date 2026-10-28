#!/usr/bin/env python3
"""Cache local de respuesta API V2 y transformación MER. No escribe Google Sheets.

Por defecto reutiliza el JSON ya guardado; --fetch es la ÚNICA ruta que llama a la API.
Respuestas y transformaciones siempre permanecen fuera del repositorio.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

from adaptar_detalle_compra_agil_mer import adaptar_detalle

CODE = re.compile(r"^[0-9]+-[0-9]+-COT[0-9]{2}$")
ROOT = "https://api2.mercadopublico.cl/v2/compra-agil/"
def private_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink(): raise ValueError("No escribir a enlaces simbólicos")
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    fd=os.open(path,flags,0o600)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
            f.write("\n")
    except BaseException:
        path.unlink(missing_ok=True)
        raise

def read_validated(path, code):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data,dict) or data.get("success") not in (True,"OK"):
        raise ValueError("Respuesta no válida")
    p=data.get("payload")
    if not isinstance(p,dict) or p.get("codigo")!=code:
        raise ValueError("Código no coincide con el respaldo")
    return data

def transform_cached(cache,code,out,clp=False):
    data=read_validated(cache,code)
    mer=adaptar_detalle(data,clp_verificado=clp)
    private_json(out,mer)
    digest=hashlib.sha256(Path(cache).read_bytes()).hexdigest()
    return {"codigo":code,"sha256_respuesta":digest,"ofertas":len(mer["ofertas"]),
            "resultados":len(mer["resultados"]),"moneda_validada":clp}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--codigo",required=True)
    p.add_argument("--dir-privado",required=True,help="Directorio local FUERA del repositorio")
    p.add_argument("--fetch",action="store_true",help="Autoriza UNA consulta API solo si no hay cache")
    p.add_argument("--clp-verificado",action="store_true",help="Solo tras verificar moneda con fuente oficial")
    args=p.parse_args()
    if not CODE.fullmatch(args.codigo): p.error("Código incorrecto")
    root=Path(args.dir_privado).expanduser().resolve()
    repo=Path(__file__).resolve().parent.parent
    if root==repo or repo in root.parents: p.error("Cache debe estar FUERA del repositorio")
    cache=root/"respuestas"/(args.codigo+".json")
    out=root/"transformadas"/(args.codigo+".json")
    if not cache.is_file():
        if not args.fetch:
            print("SIN_CACHE: no se consultó API; indicar ruta a respaldo existente o ejecutar luego --fetch",file=sys.stderr)
            return 2
        ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
        if not ticket: raise SystemExit("Falta CHILECOMPRA_TICKET")
        req=Request(ROOT+args.codigo,headers={"ticket":ticket,"Accept":"application/json"})
        with urlopen(req,timeout=40) as response:
            if response.status!=200: raise RuntimeError("HTTP distinto de 200")
            raw=response.read(8_000_001)
            if len(raw)>8_000_000: raise ValueError("JSON excede limite")
            data=json.loads(raw)
        if not isinstance(data,dict) or data.get("success") not in (True,"OK") or (data.get("payload") or {}).get("codigo")!=args.codigo:
            raise ValueError("Respuesta API inválida, no guardar")
        private_json(cache,data)
    summary=transform_cached(cache,args.codigo,out,args.clp_verificado)
    print(json.dumps(summary,ensure_ascii=False))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
