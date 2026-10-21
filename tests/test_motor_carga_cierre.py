#!/usr/bin/env python3
"""Pruebas locales del motor sin Google Sheets."""
import sys,json,sqlite3,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from motor_carga_cierre import TABLES,plan_local,simulacion

def bd():
 c=sqlite3.connect(":memory:")
 for t in TABLES:c.execute('CREATE TABLE "'+t+'" (pk TEXT PRIMARY KEY,fila TEXT NOT NULL)')
 return c
class TestMotor(unittest.TestCase):
 def test_altas_reintentos_y_preservacion(self):
  hist,op=bd(),bd()
  for t in TABLES:
   hist.execute('INSERT INTO "'+t+'" VALUES (?,?)',("A",json.dumps(["A","nuevo"])))
   hist.execute('INSERT INTO "'+t+'" VALUES (?,?)',("B",json.dumps(["B","historico"])))
   op.execute('INSERT INTO "'+t+'" VALUES (?,?)',("B",json.dumps(["B","operativo"])))
   op.execute('INSERT INTO "'+t+'" VALUES (?,?)',("C",json.dumps(["C","exclusivo"])))
  antes,despues=simulacion(hist,op)
  for t in TABLES:
   self.assertEqual(antes[t]["nuevos"],1)
   self.assertEqual(antes[t]["modificados"],1)
   self.assertEqual(despues[t]["nuevos"],0)
   self.assertEqual(despues[t]["modificados"],1)
   self.assertEqual(despues[t]["solo_operativo"],1)
  _,rep=simulacion(hist,op)
  self.assertTrue(all(rep[t]["nuevos"]==0 for t in TABLES))
 def test_politica_restringida(self):
  with self.assertRaises(ValueError):simulacion(bd(),bd(),politica="sobrescribir")
if __name__=="__main__":unittest.main()
