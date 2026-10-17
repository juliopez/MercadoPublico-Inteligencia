#!/usr/bin/env python3
"""Pruebas offline de selección puntual para un reintento diferido V2."""
import importlib.util, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
p=Path(__file__).with_name("orquestador_v2_detalles_local.py")
spec=importlib.util.spec_from_file_location("detalle_puntual_test",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.con=m.core.db_open(self.root/"ctrl.sqlite");m.install(self.con)
  with self.con:
   self.con.execute("INSERT INTO detail_jobs(codigo,estado,disponible,actualizado) VALUES ('TEST-COT26','espera','2999-01-01T00:00:00+00:00','x')")
 def tearDown(self):
  self.con.close();self.tmp.cleanup()
 def test_no_consulta_antes_de_plazo(self):
  with patch.dict(m.os.environ,{"CHILECOMPRA_TICKET":"FICTICIO"}), patch.object(m,"urlopen",side_effect=AssertionError("No HTTP")):
   m.run(self.con,1,420,"TEST-COT26")
  self.assertEqual(self.con.execute("SELECT intentos FROM detail_jobs").fetchone()[0],0)
 def test_no_consulta_codigo_ausente(self):
  with patch.dict(m.os.environ,{"CHILECOMPRA_TICKET":"FICTICIO"}), patch.object(m,"urlopen",side_effect=AssertionError("No HTTP")):
   m.run(self.con,1,420,"OTRO-COT26")
 def test_no_consulta_codigo_completo(self):
  with self.con:self.con.execute("UPDATE detail_jobs SET estado='completo' WHERE codigo='TEST-COT26'")
  with patch.dict(m.os.environ,{"CHILECOMPRA_TICKET":"FICTICIO"}), patch.object(m,"urlopen",side_effect=AssertionError("No HTTP")):
   m.run(self.con,1,420,"TEST-COT26")
if __name__=="__main__":unittest.main(verbosity=2)
