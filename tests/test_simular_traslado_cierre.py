import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from simular_traslado_cierre import planificar
def base():
 return {"periodos":{"2026-10":{"tipo":"operativo","id":"id-original"}},"carpetas":{"operativo":"folder-origen","historicos":"folder-destino"},"excluidos":{}}
def aprobado():
 return {"periodo":"2026-10","estado":"CANDIDATO_A_APROBACION_SUPERVISADA","cierre_autorizado":False,"traslado_autorizado":False}
class TrasladoTest(unittest.TestCase):
 def test_preserva_id_y_no_escribe(self):
  out=planificar("2026-10",base(),aprobado())
  self.assertEqual(out["id_original"],"id-original")
  self.assertEqual(out["despues"]["nombre"],"MER_2026_10")
  self.assertFalse(out["autorizado_para_mover"])
 def test_rechaza_cierre_incompleto(self):
  a=aprobado();a["estado"]="BLOQUEADO"
  with self.assertRaises(ValueError):planificar("2026-10",base(),a)
 def test_rechaza_hoja_excluida(self):
  c=base();c["excluidos"]={"viejo":"id-original"}
  with self.assertRaises(ValueError):planificar("2026-10",c,aprobado())
 def test_rechaza_evaluacion_con_permisos_incorrectos(self):
  a=aprobado();a["traslado_autorizado"]=True
  with self.assertRaises(ValueError):planificar("2026-10",base(),a)
if __name__=="__main__":unittest.main()
