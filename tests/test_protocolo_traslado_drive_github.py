import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from protocolo_traslado_drive_github import paso
P={"estado":"SIMULACION_SIN_TRASLADO","periodo":"2026-10","id_original":"ID","antes":{"nombre":"MER_2026_10_OPERATIVO","carpeta":"O"},"despues":{"nombre":"MER_2026_10","carpeta":"H"}}
def meta(moved=False):return {"id":"ID","nombre":P["despues" if moved else "antes"]["nombre"],"carpeta":P["despues" if moved else "antes"]["carpeta"]}
def cat(done=False):return {"periodos":{"2026-10":{"id":"ID","tipo":"historico" if done else "operativo"}}}
class TestProtocolo(unittest.TestCase):
 def test_antes_de_mover(self):self.assertEqual(paso(P,meta(),cat(),"PREPARADO")["situacion"],"PENDIENTE_MOVER_DRIVE")
 def test_drive_movido_catalogo_antiguo(self):self.assertEqual(paso(P,meta(True),cat(),"DRIVE_CONFIRMADO")["situacion"],"PENDIENTE_ACTUALIZAR_CATALOGO")
 def test_finalizado(self):self.assertEqual(paso(P,meta(True),cat(True),"FINALIZADO")["situacion"],"FINALIZADO")
 def test_catalogo_adelantado_no_reparar_a_ciegas(self):self.assertEqual(paso(P,meta(),cat(True),"PREPARADO")["situacion"],"INCONSISTENCIA_CATALOGO_ADELANTADO")
 def test_no_finalizar_si_falta_catalogo(self):
  with self.assertRaises(ValueError):paso(P,meta(True),cat(),"FINALIZADO")
if __name__=="__main__":unittest.main()
