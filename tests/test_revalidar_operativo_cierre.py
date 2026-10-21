#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from conciliar_cierre_mensual import huella_tabla
from revalidar_operativo_cierre import cotejar
class TestHuella(unittest.TestCase):
 def test_independiente_del_orden(self):
  a={"b":["b","2"],"a":["a","1"]}
  b={"a":["a","1"],"b":["b","2"]}
  self.assertEqual(huella_tabla(a),huella_tabla(b))
 def test_cambio_con_misma_cantidad(self):
  antes=huella_tabla({"A":["A","1"]})
  despues=huella_tabla({"A":["A","2"]})
  self.assertNotEqual(antes,despues)
  with self.assertRaises(ValueError):cotejar({},despues,antes)
 def test_no_acepta_conciliacion_antigua(self):
  with self.assertRaises(ValueError):cotejar({},"x","")
if __name__=="__main__":unittest.main()
