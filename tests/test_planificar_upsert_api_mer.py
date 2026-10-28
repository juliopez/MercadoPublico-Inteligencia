import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from planificar_upsert_api_mer import planificar
from adaptar_detalle_compra_agil_mer import OFERTAS,RESULTADOS
class TestPlan(unittest.TestCase):
 def test_inserciones_repetibles(self):
  r={"codigo":"839-4-COT26","id_cotizacion":"42","proveedor":"ABC"}
  p=planificar("Ofertas",[list(OFERTAS)],[r]);self.assertEqual(len(p["insertar"]),1)
  existente=[list(OFERTAS),[p["insertar"][0][k] for k in OFERTAS]]
  q=planificar("Ofertas",existente,[r]);self.assertEqual(q["sin_cambios"],1)
 def test_completar_sin_pisar(self):
  r=["" for _ in RESULTADOS];r[0]="839-4-COT26";r[1]="42";r[7]="Validado"
  p=planificar("Resultados",[list(RESULTADOS),r],[{"codigo":"839-4-COT26","id_cotizacion_ganadora":"42","validado":"No","fuente":"API"}])
  self.assertEqual(len(p["conflictos"]),1)
  self.assertEqual(p["actualizar"][0]["valores"]["validado"],"Validado")
 def test_clave_duplicada(self):
  with self.assertRaises(ValueError):planificar("Ofertas",[list(OFERTAS)],[{"codigo":"x","id_cotizacion":"1"}]*2)
 def test_cabecera(self):
  with self.assertRaises(ValueError):planificar("Ofertas",[["codigo"]],[])
if __name__=="__main__":unittest.main()
