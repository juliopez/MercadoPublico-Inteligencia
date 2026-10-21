#!/usr/bin/env python3
"""Prueba local sin red del clasificador de conciliación MER."""
import json,sqlite3,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from conciliar_cierre_mensual import comparar
class ComparadorTest(unittest.TestCase):
 def test_cuatro_estados(self):
  db=sqlite3.connect(":memory:")
  db.execute('CREATE TABLE "Procesos" (pk TEXT PRIMARY KEY,fila TEXT NOT NULL)')
  db.executemany('INSERT INTO Procesos VALUES (?,?)',[("A",json.dumps(["A","igual"])),("B",json.dumps(["B","nuevo"])),("C",json.dumps(["C","historico"]))])
  res=comparar(db,"Procesos",{"A":["A","igual"],"C":["C","operativo"],"D":["D","sin_historico"]})
  self.assertEqual([res[k] for k in ("nuevos","modificados","sin_cambios","solo_operativo")],[1,1,1,1])
  self.assertEqual(res["filas_historico"],3)
  self.assertEqual(res["filas_operativo"],3)
if __name__=="__main__":unittest.main()
