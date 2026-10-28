import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from simular_escritura_api_mer import preparar
from adaptar_detalle_compra_agil_mer import OFERTAS,RESULTADOS
from resolver_proveedores_ofertas_mer import resolver_ofertas
P=["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"]
class Simular(unittest.TestCase):
 def test_simulacion(self):
  t={"codigo":"839-4-COT26","ofertas":[{"codigo":"839-4-COT26","id_cotizacion":"100","rut_proveedor_cot":"76.511.768-2"}],
     "resultados":[{"codigo":"839-4-COT26","id_cotizacion_ganadora":"100","validado":"No"}]}
  snap={"Ofertas":[list(OFERTAS)],"Resultados":[list(RESULTADOS)],
        "Proveedores":[P,["rut:765117682","765117682","Ejemplo","","OC","RUT_SIN_CONTRASTE"]]}
  r=preparar(t,snap)
  self.assertEqual(r["identidad_resuelta"],1)
  self.assertEqual(r["tablas"]["Ofertas"]["nuevos"],1)
  self.assertEqual(r["tablas"]["Resultados"]["nuevos"],1)
  self.assertFalse(r["aplicable"])
 def test_falla_sin_snapshot(self):
  with self.assertRaises(ValueError):preparar({"codigo":"x","ofertas":[],"resultados":[]},{})
if __name__=="__main__":unittest.main()
