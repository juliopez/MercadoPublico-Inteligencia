#!/usr/bin/env python3
"""Pruebas offline de exclusión mutua y liberación al interrumpir."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE=Path(__file__).with_name("orquestador_v2_sqlite_local.py")
spec=importlib.util.spec_from_file_location("v2_lock_test",SOURCE)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def test_segunda_ejecucion_bloqueada(self):
        with core.execution_lock(self.root):
            with self.assertRaisesRegex(RuntimeError,"otra ejecución"):
                with core.execution_lock(self.root):
                    pass
    def test_se_libera_tras_excepcion(self):
        try:
            with core.execution_lock(self.root):
                raise ValueError("fallo simulado")
        except ValueError:
            pass
        with core.execution_lock(self.root):
            self.assertTrue(True)
    def test_se_libera_tras_keyboard_interrupt(self):
        with self.assertRaises(KeyboardInterrupt):
            with core.execution_lock(self.root):
                raise KeyboardInterrupt
        with core.execution_lock(self.root):
            self.assertTrue(True)
    def test_persistencia_no_afectada(self):
        db=core.db_open(self.root/"control.sqlite3")
        try:
            core.initialize(db,"2026-10-15",2,False)
            with core.execution_lock(self.root):
                self.assertEqual(db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],2)
        finally:
            db.close()
if __name__=="__main__":
    unittest.main(verbosity=2)
