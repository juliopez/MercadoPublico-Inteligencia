import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from preparar_transaccion_api_mer import preparar_transaccion
from adaptar_detalle_compra_agil_mer import OFERTAS,RESULTADOS
P=["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"]
class TestTransaccion(unittest.TestCase):
 def test_snapshot_y_lock(self):
  with tempfile.TemporaryDirectory() as tmp:
   lock=Path(tmp)/".mer_escritura_compartida.lock";lock.touch()
   snap={"Ofertas":[list(OFERTAS)],"Resultados":[list(RESULTADOS)],"Proveedores":[P]}
   trans={"codigo":"839-4-COT26","ofertas":[{"codigo":"839-4-COT26","id_cotizacion":"1"}],"resultados":[]}
   resumen,plan=preparar_transaccion(trans,snap,lock)
   self.assertEqual(resumen["tablas"]["Ofertas"]["nuevos"],1)
   self.assertEqual(len(plan["Ofertas"]["insertar"]),1)
 def test_lock_inexistente(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):preparar_transaccion({}, {}, Path(tmp)/"missing.lock")
if __name__=="__main__":unittest.main()
