#!/usr/bin/env python3
"""Pruebas offline de separación global de solicitudes V2 entre conexiones SQLite."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

source=Path(__file__).with_name("orquestador_v2_sqlite_local.py")
spec=importlib.util.spec_from_file_location("orq_rate_test",source)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)

class TestRateLimit(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        path=Path(self.temp.name)/"ctrl.sqlite"
        self.a=core.db_open(path)
        self.b=core.db_open(path)
    def tearDown(self):
        self.a.close();self.b.close();self.temp.cleanup()
    def test_primera_solicitud_sin_espera(self):
        with patch.object(core.time,"time",return_value=1000.0):
            with patch.object(core.time,"sleep") as sleeper:
                delay=core.reserve_request(self.a)
        self.assertEqual(delay,0)
        sleeper.assert_not_called()
    def test_segunda_cola_debe_esperar(self):
        with patch.object(core.time,"time",return_value=1000.0):
            with patch.object(core.time,"sleep"):
                core.reserve_request(self.a)
            with patch.object(core.time,"sleep") as sleeper:
                delay=core.reserve_request(self.b)
        self.assertEqual(delay,60.0)
        sleeper.assert_called_once_with(60.0)
    def test_tres_reservas_acumulan_intervalos(self):
        with patch.object(core.time,"time",return_value=1000.0):
            with patch.object(core.time,"sleep") as sleeper:
                delays=[core.reserve_request(x) for x in (self.a,self.b,self.a)]
        self.assertEqual(delays,[0,60,120])
        self.assertEqual(sleeper.call_count,2)
    def test_intervalo_persistente_entre_conexiones(self):
        with patch.object(core.time,"time",return_value=1000.0):
            with patch.object(core.time,"sleep"):
                core.reserve_request(self.a)
        self.a.close()
        self.a=core.db_open(Path(self.temp.name)/"ctrl.sqlite")
        with patch.object(core.time,"time",return_value=1030.0):
            with patch.object(core.time,"sleep") as sleeper:
                delay=core.reserve_request(self.a)
        self.assertEqual(delay,30)
        sleeper.assert_called_once_with(30)
if __name__=="__main__":
    unittest.main(verbosity=2)
