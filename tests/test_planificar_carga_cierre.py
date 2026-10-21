#!/usr/bin/env python3
"""Pruebas offline de la política de carga, sin Google/Drive."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from planificar_carga_cierre import evaluar,TABLAS
class TestPlan(unittest.TestCase):
 def fixture(self):
  return {"estado":"CONCILIACION_INFORMATIVA_REQUIERE_REVISION",
          "periodo":"2026-10","spreadsheet_id":"sheet_prueba",
          "observaciones_paquete":{"selecciones_ambiguas":2},
          "tablas":{t:{"nuevos":1,"modificados":1,"sin_cambios":2,
                       "solo_operativo":1,"filas_historico":4,"filas_operativo":4} for t in TABLAS}}
 def test_conserva_y_bloquea(self):
  p=evaluar(self.fixture())
  self.assertFalse(p["autorizado_para_escribir"])
  self.assertFalse(p["autorizado_para_mover"])
  self.assertEqual(p["acciones_candidatas"]["Procesos"]["solo_operativo_sin_borrado"],1)
  self.assertTrue(p["alertas"])
 def test_rechaza_conteos_inconsistentes(self):
  x=self.fixture();x["tablas"]["Ofertas"]["filas_historico"]=9
  with self.assertRaises(ValueError):evaluar(x)
 def test_rechaza_tablas_ausentes(self):
  x=self.fixture();del x["tablas"]["Proveedores"]
  with self.assertRaises(ValueError):evaluar(x)
if __name__=="__main__":unittest.main()
