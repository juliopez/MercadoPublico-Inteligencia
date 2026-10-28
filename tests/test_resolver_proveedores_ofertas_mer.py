import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from resolver_proveedores_ofertas_mer import resolver_ofertas
HEADER=["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"]
class TestResolver(unittest.TestCase):
 def test_match_normalizado(self):
  r=resolver_ofertas([{"rut_proveedor_cot":"76.511.768-2","id_proveedor":""}],[HEADER,["rut:765117682","765117682","Proveedor","","OC","RUT_SIN_CONTRASTE"]])
  self.assertEqual(r["ofertas"][0]["id_proveedor"],"rut:765117682")
 def test_no_inventar(self):
  r=resolver_ofertas([{"rut_proveedor_cot":"11-1","id_proveedor":""}],[HEADER])
  self.assertEqual(r["sin_identidad"],1)
 def test_ambiguo(self):
  with self.assertRaises(ValueError):resolver_ofertas([], [HEADER,["a","12"],["b","12"]])
if __name__=="__main__":unittest.main()
