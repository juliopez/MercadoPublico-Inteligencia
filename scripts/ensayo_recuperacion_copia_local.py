#!/usr/bin/env python3
"""Ensayo offline de recuperación contra COPIA SQLite+JSON; jamás modifica originales."""
import importlib.util
import json
import sqlite3
import tempfile
from pathlib import Path
from shutil import copy2

BASE=Path("orquestacion_v2_local")
SOURCE=Path(__file__).with_name("orquestador_v2_sqlite_local.py")
spec=importlib.util.spec_from_file_location("v2_sandbox_recovery",SOURCE)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)

def main():
    original_db=BASE/"control.sqlite3"
    if not original_db.exists():
        raise SystemExit("Falta control.sqlite3; no se realiza ninguna modificación")
    with tempfile.TemporaryDirectory(prefix="v2_recuperacion_aislada_") as temp:
        root=Path(temp)/"copia"
        root.mkdir()
        # SQLite Backup API incorpora transacciones WAL sin alterar la base original.
        src=sqlite3.connect(f"file:{original_db.resolve()}?mode=ro",uri=True)
        dst=sqlite3.connect(root/"control.sqlite3")
        try:src.backup(dst)
        finally:src.close();dst.close()
        con=core.db_open(root/"control.sqlite3")
        try:
            row=con.execute("SELECT fecha,pagina,archivo FROM jobs WHERE estado='completo' ORDER BY fecha,pagina LIMIT 1").fetchone()
            if row is None: raise RuntimeError("No existe página completa para ensayar")
            date,page=row["fecha"],row["pagina"]
            original=Path(row["archivo"])
            if not original.is_file():raise RuntimeError("Archivo de origen no existe")
            cloned=core.file_for(root,date,page)
            cloned.parent.mkdir(parents=True,exist_ok=True)
            copy2(original,cloned)
            before_bytes=original.read_bytes()
            # Copiar las demás páginas completas para verificar consistencia.
            for old in con.execute("SELECT fecha,pagina,archivo FROM jobs WHERE fecha=? AND estado='completo'",(date,)).fetchall():
                f=Path(old['archivo'])
                if not f.is_file(): raise RuntimeError('Página original ausente')
                target=core.file_for(root,old['fecha'],old['pagina'])
                target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists(): copy2(f,target)
            # Simular: JSON ya escrito pero se perdió el checkpoint.
            with con:
                con.execute("UPDATE jobs SET estado='pendiente',archivo=NULL,registros=NULL,http=NULL WHERE fecha=? AND pagina=?",(date,page))
            recovered=core.reconcile_pages(con,date,root=root)
            after=con.execute("SELECT estado,archivo,http FROM jobs WHERE fecha=? AND pagina=?",(date,page)).fetchone()
            assert recovered==1,(recovered,dict(after))
            assert after["estado"]=="completo" and after["http"]==200
            assert cloned.read_bytes()==before_bytes
            assert original.read_bytes()==before_bytes
            print(f"PRUEBA AISLADA OK: página {page}, fecha {date}; checkpoint recuperado sin HTTP")
            # Ensayo independiente para detalles.
            table=con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detail_jobs'").fetchone()
            if not table:
                print("Detalle: tabla no presente; omitido")
                return
            detail=con.execute("SELECT codigo,archivo FROM detail_jobs WHERE estado='completo' ORDER BY codigo LIMIT 1").fetchone()
            if detail is None:
                print("Detalle: ninguno completo; omitido")
                return
            detail_original=Path(detail["archivo"])
            if not detail_original.is_file():raise RuntimeError("Archivo detalle original ausente")
            code=detail["codigo"]
            detail_copy=root/"detalles"/(code+".json")
            detail_copy.parent.mkdir(parents=True,exist_ok=True)
            copy2(detail_original,detail_copy)
            raw_original=detail_original.read_bytes()
            with con:
                con.execute("UPDATE detail_jobs SET estado='pendiente',archivo=NULL,http=NULL WHERE codigo=?",(code,))
            detail_source=Path(__file__).with_name("orquestador_v2_detalles_local.py")
            s=importlib.util.spec_from_file_location("v2_sandbox_detail",detail_source)
            module=importlib.util.module_from_spec(s);s.loader.exec_module(module)
            n=module.reconcile_details(con,root=root)
            check=con.execute("SELECT estado,http FROM detail_jobs WHERE codigo=?",(code,)).fetchone()
            assert n==1 and check["estado"]=="completo" and check["http"]==200
            assert detail_copy.read_bytes()==raw_original==detail_original.read_bytes()
            print(f"PRUEBA AISLADA OK: detalle {code}; checkpoint recuperado sin HTTP")
        finally:
            con.close()
    print("Directorio temporal eliminado; originales intactos.")
if __name__=="__main__":
    main()
