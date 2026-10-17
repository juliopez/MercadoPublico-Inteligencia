#!/usr/bin/env python3
"""Pruebas offline de circuit breaker y cola de detalles. Sin red."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

DIR=Path(__file__).resolve().parent
def load(file,name):
    spec=importlib.util.spec_from_file_location(name,DIR/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
core=load("orquestador_v2_sqlite_local.py","core_circuit_test")
details=load("orquestador_v2_detalles_local.py","details_queue_test")
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.con=core.db_open(self.root/"state.sqlite")
        details.install(self.con)
    def tearDown(self):
        self.con.close();self.tmp.cleanup()
    def test_circuit_abre_tras_tres_fallos(self):
        with self.con:
            self.assertEqual(core.circuit_record(self.con,504),"")
            self.assertEqual(core.circuit_record(self.con,500),"")
            until=core.circuit_record(self.con,503)
        self.assertTrue(until)
        self.assertTrue(core.circuit_open(self.con))
    def test_exito_reinicia_consecutivos(self):
        with self.con:
            core.circuit_record(self.con,504)
            core.circuit_record(self.con,200)
        row=self.con.execute("SELECT * FROM circuit WHERE servicio='api_v2'").fetchone()
        self.assertEqual(row["consecutivos"],0)
        self.assertFalse(core.circuit_open(self.con))
    def test_429_abre_inmediatamente(self):
        with self.con: core.circuit_record(self.con,429)
        self.assertTrue(core.circuit_open(self.con))
    def test_cola_detalles_inicia_sin_http(self):
        folder=self.root/"source";folder.mkdir()
        data={"success":"OK","payload":{"paginacion":{"total_paginas":1},
            "items":[{"codigo":"TEST-1-COT26"},{"codigo":"TEST-2-COT26"}]}}
        f=folder/"pagina_0001.json";f.write_text(json.dumps(data),encoding="utf-8")
        self.con.execute("INSERT INTO jobs(fecha,pagina,estado,archivo,actualizado) VALUES(?,?,?,?,?)",
            ("2026-10-15",1,"completo",str(f),core.stamp(core.utc())))
        self.con.commit()
        details.seed(self.con,"2026-10-15")
        details.seed(self.con,"2026-10-15")
        row=self.con.execute("SELECT count(*) FROM detail_jobs").fetchone()
        self.assertEqual(row[0],2)
        with patch.object(details,"urlopen",side_effect=AssertionError("No debe llamar HTTP")):
            details.report(self.con)
    def test_circuito_bloquea_detalles_antes_de_http(self):
        with self.con:core.circuit_record(self.con,429)
        with patch.dict(details.os.environ,{"CHILECOMPRA_TICKET":"FICTICIO"}):
            with patch.object(details,"urlopen",side_effect=AssertionError("HTTP prohibido")):
                details.run(self.con,1)
if __name__=="__main__":
    unittest.main(verbosity=2)
