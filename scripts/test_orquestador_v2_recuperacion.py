#!/usr/bin/env python3
"""Pruebas offline de reconciliación tras interrupción JSON→SQLite."""
import importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj
core=load("recovery_core","orquestador_v2_sqlite_local.py")
details=load("recovery_details","orquestador_v2_detalles_local.py")
DATE="2026-10-15"
def listing():
    return json.dumps({"success":"OK","payload":{"paginacion":{"total_paginas":10},"items":[{"codigo":"TEST-COT26"}]}}).encode()
def detail():
    return json.dumps({"success":"OK","payload":{"codigo":"TEST-COT26","institucion":{},
      "proveedores_cotizando":[],"productos_solicitados":[]}}).encode()
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.con=core.db_open(self.root/"control.sqlite3");core.initialize(self.con,DATE,2,False)
        details.install(self.con)
    def tearDown(self):
        self.con.close();self.tmp.cleanup()
    def test_antes_de_guardar_pendiente(self):
        self.assertEqual(core.reconcile_pages(self.con,DATE,self.root),0)
        self.assertEqual(self.con.execute("SELECT estado FROM jobs WHERE pagina=1").fetchone()[0],"pendiente")
    def test_archivo_pagina_sin_checkpoint(self):
        core.write_atomic(core.file_for(self.root,DATE,1),listing())
        self.assertEqual(core.reconcile_pages(self.con,DATE,self.root),1)
        self.assertEqual(core.reconcile_pages(self.con,DATE,self.root),0)
        self.assertEqual(self.con.execute("SELECT estado FROM jobs WHERE pagina=1").fetchone()[0],"completo")
    def test_checkpoint_pagina_no_se_repite(self):
        core.write_atomic(core.file_for(self.root,DATE,1),listing())
        core.reconcile_pages(self.con,DATE,self.root)
        self.assertEqual(core.reconcile_pages(self.con,DATE,self.root),0)
    def test_detalle_guardado_sin_checkpoint(self):
        with self.con:
            self.con.execute("INSERT INTO detail_jobs(codigo,actualizado) VALUES (?,?)",("TEST-COT26",core.stamp(core.utc())))
        path=self.root/"detalles/TEST-COT26.json";core.write_atomic(path,detail())
        self.assertEqual(details.reconcile_details(self.con,self.root),1)
        self.assertEqual(details.reconcile_details(self.con,self.root),0)
        self.assertEqual(self.con.execute("SELECT estado FROM detail_jobs").fetchone()[0],"completo")
    def test_detalle_no_guardado_pendiente(self):
        with self.con:
            self.con.execute("INSERT INTO detail_jobs(codigo,actualizado) VALUES (?,?)",("TEST-COT26",core.stamp(core.utc())))
        self.assertEqual(details.reconcile_details(self.con,self.root),0)
    def test_json_ilegible_no_se_confirma(self):
        core.write_atomic(core.file_for(self.root,DATE,1),b'{}')
        with self.assertRaises(ValueError):
            core.reconcile_pages(self.con,DATE,self.root)
        self.assertEqual(self.con.execute("SELECT estado FROM jobs WHERE pagina=1").fetchone()[0],"pendiente")
if __name__=="__main__":unittest.main(verbosity=2)
