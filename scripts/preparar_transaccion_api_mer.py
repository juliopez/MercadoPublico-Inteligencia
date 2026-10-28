#!/usr/bin/env python3
"""Preparación segura de escritura MER: plan, respaldo y verificación local.

Sin acceso de red y sin aplicar cambios a Sheets. Utiliza el mismo lock
fcntl de la conciliación para ensayar exclusión mutua.
"""
import argparse,fcntl,hashlib,json,os,pathlib,sys
from datetime import datetime,timezone
from simular_escritura_api_mer import preparar
from planificar_upsert_api_mer import planificar
from resolver_proveedores_ofertas_mer import resolver_ofertas
from adaptar_detalle_compra_agil_mer import OFERTAS,RESULTADOS

def desarrollar(transformacion,snapshot):
    resumen=preparar(transformacion,snapshot)
    enriquecidas=resolver_ofertas(transformacion["ofertas"],snapshot["Proveedores"])["ofertas"]
    planes={}
    for tabla,filas in (("Ofertas",enriquecidas),("Resultados",transformacion["resultados"])):
        p=planificar(tabla,snapshot[tabla],filas)
        # Los conflictos no pueden tratarse como escrituras válidas automáticas.
        planes[tabla]={"insertar":p["insertar"],"actualizar":p["actualizar"],
                       "conflictos":p["conflictos"],"sin_cambios":p["sin_cambios"]}
    return resumen,planes

def preparar_transaccion(transformacion,snapshot,lockpath):
    lockpath=pathlib.Path(lockpath)
    if not lockpath.is_file():
        # No crear un lock ficticio: este ejecutor no está autorizado a operar producción.
        raise ValueError("Lock compartido no disponible: sólo se permite probar sobre lock existente")
    with lockpath.open("a+") as h:
        try: fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as e:raise RuntimeError("MER ocupado") from e
        try:return desarrollar(transformacion,snapshot)
        finally:fcntl.flock(h,fcntl.LOCK_UN)

def main():
    ap=argparse.ArgumentParser(description="DRY RUN estricto; no existe --aplicar")
    ap.add_argument("--transformacion",required=True)
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--lock",required=True)
    ap.add_argument("--respaldo",required=True,help="Ruta privada inexistente para snapshot")
    args=ap.parse_args()
    trans_path=pathlib.Path(args.transformacion)
    snap_path=pathlib.Path(args.snapshot)
    trans=json.loads(trans_path.read_text(encoding="utf-8"))
    snapshot=json.loads(snap_path.read_text(encoding="utf-8"))
    summary,plans=preparar_transaccion(trans,snapshot,args.lock)
    dest=pathlib.Path(args.respaldo)
    if dest.exists() or dest.is_symlink():raise FileExistsError("Respaldo existente")
    dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    # Snapshot de tres tablas, exclusivamente local y privado; no usar GitHub artifacts.
    fd=os.open(dest,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        json.dump(snapshot,f,ensure_ascii=False)
        f.write("\n")
    summary["snapshot_sha256"]=hashlib.sha256(dest.read_bytes()).hexdigest()
    summary["requiere_resolver_conflictos"]=any(p["conflictos"] for p in plans.values())
    summary["aplicable"]=False
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
