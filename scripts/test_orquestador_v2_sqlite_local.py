#!/usr/bin/env python3
"""Pruebas aisladas con HTTP simulado. Sin solicitudes de red ni escrituras a Sheets."""
import argparse
import importlib.util
import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

SOURCE = Path(__file__).with_name("orquestador_v2_sqlite_local.py")
spec=importlib.util.spec_from_file_location("orquestador_v2_test",SOURCE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
DAY="2026-10-15"
def body(page,code):
    return json.dumps({"success":"OK","payload":{"paginacion":{"total_paginas":10},
        "items":[{"codigo":code}]}}).encode()
class Response:
    status=200
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self):return self.data
def error(code):
    return HTTPError("https://example.invalid",code,"simulado",{},io.BytesIO(b'{"message":"simulado"}'))
class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)/"test"
        self.con=mod.db_open(self.root/"control.sqlite3")
        self.oldroot=mod.ROOT
        mod.ROOT=self.root
        mod.initialize(self.con,DAY,3,False)
        self.args=argparse.Namespace(fecha=DAY,max_solicitudes=1,pausa=30)
        self.env=patch.dict(os.environ,{"CHILECOMPRA_TICKET":"TICKET_FICTICIO_NO_REAL"})
        self.env.start()
        self.sleep=patch.object(mod.time,"sleep",return_value=None)
        self.sleep.start()
        self.jitter=patch.object(mod.random,"randint",return_value=0)
        self.jitter.start()
    def tearDown(self):
        self.jitter.stop();self.sleep.stop();self.env.stop()
        self.con.close();mod.ROOT=self.oldroot;self.temp.cleanup()
    def job(self,page):
        return self.con.execute("SELECT * FROM jobs WHERE fecha=? AND pagina=?",(DAY,page)).fetchone()
    def run_once(self,thing):
        with patch.object(mod,"urlopen",side_effect=[thing] if isinstance(thing,BaseException) else None,
                          return_value=None if isinstance(thing,BaseException) else thing) as api:
            mod.execute(self.con,self.args)
            return api.call_count
    def test_200_guarda_json_y_omite_completados(self):
        self.assertEqual(self.run_once(Response(body(1,"A-COT26"))),1)
        self.assertEqual(self.job(1)["estado"],"completo")
        self.assertTrue(Path(self.job(1)["archivo"]).is_file())
        self.assertEqual(self.run_once(Response(body(2,"B-COT26"))),1)
        self.assertEqual(self.job(1)["intentos"],1)
        self.assertEqual(mod.check_done(self.con,DAY)[0],2)
    def test_500_504_aplazan_y_no_borran_completos(self):
        self.run_once(Response(body(1,"A-COT26")))
        self.run_once(error(500))
        j=self.job(2)
        self.assertEqual((j["estado"],j["http"],j["intentos"]),("espera",500,1))
        self.assertTrue(j["disponible"])
        self.assertEqual(mod.check_done(self.con,DAY)[0],1)
        self.con.execute("UPDATE jobs SET disponible='' WHERE fecha=? AND pagina=2",(DAY,))
        self.con.commit()
        self.run_once(error(504))
        self.assertEqual(self.job(2)["http"],504)
        self.assertEqual(self.job(2)["intentos"],2)
        self.assertEqual(mod.check_done(self.con,DAY)[0],1)
    def test_429_suspendido(self):
        self.run_once(error(429))
        j=self.job(1)
        self.assertEqual((j["estado"],j["http"]),("espera",429))
        due=datetime.fromisoformat(j["disponible"])
        self.assertGreaterEqual((due-datetime.now(timezone.utc)).total_seconds(),3595)
    def test_400_revision_sin_reintento(self):
        self.run_once(error(400))
        self.assertEqual(self.job(1)["estado"],"revision")
        self.assertEqual(self.run_once(Response(body(2,"B-COT26"))),1)
        self.assertEqual(self.job(1)["intentos"],1)
        self.assertEqual(self.job(2)["estado"],"completo")
    def test_espera_no_disponible_no_se_consulta(self):
        self.run_once(error(504))
        self.assertEqual(self.run_once(Response(body(2,"B-COT26"))),1)
        self.assertEqual(self.job(1)["intentos"],1)
    def test_duplicado_entre_paginas_se_bloquea(self):
        self.run_once(Response(body(1,"A-COT26")))
        self.run_once(Response(body(2,"A-COT26")))
        self.assertEqual(self.job(2)["estado"],"revision")
        self.assertFalse(mod.file_for(self.root,DAY,2).exists())
        self.assertEqual(mod.check_done(self.con,DAY)[0],1)
if __name__=="__main__":
    unittest.main(verbosity=2)
