import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from adaptadores_traslado_cierre import ejecutar
PLAN={"estado":"SIMULACION_SIN_TRASLADO","periodo":"2026-10","id_original":"ID","antes":{"nombre":"MER_2026_10_OPERATIVO","carpeta":"O"},"despues":{"nombre":"MER_2026_10","carpeta":"H"}}
class TestAdapters(unittest.TestCase):
 def test_reinicio_tras_drive_movido(self):
  x={"drive":{"id":"ID","nombre":"MER_2026_10_OPERATIVO","carpeta":"O"},"cat":{"periodos":{"2026-10":{"tipo":"operativo","id":"ID"}}}}
  events=[];moved=[]
  def ld(id):return copy.deepcopy(x["drive"])
  def lc():return copy.deepcopy(x["cat"])
  def mv(id,src,dst,name):
   moved.append(id);x["drive"]={"id":id,"nombre":name,"carpeta":dst}
  def save(v):x["cat"]=copy.deepcopy(v)
  def log(kind,data):
   events.append(kind)
   if kind=="DRIVE_CONFIRMADO" and len(moved)==1:raise RuntimeError("corte simulado")
  with self.assertRaises(RuntimeError):
   ejecutar(PLAN,ld,lc,mv,save,log,autorizar=True)
  self.assertEqual(len(moved),1)
  self.assertEqual(x["cat"]["periodos"]["2026-10"]["tipo"],"operativo")
  out=ejecutar(PLAN,ld,lc,mv,save,lambda *_:None,autorizar=True)
  self.assertEqual(out["situacion"],"FINALIZADO")
  self.assertEqual(len(moved),1)
  self.assertEqual(x["cat"]["periodos"]["2026-10"]["id"],"ID")
 def test_sin_autorizacion_no_cambia(self):
  with self.assertRaises(PermissionError):
   ejecutar(PLAN,lambda _:None,lambda:None,lambda *a:self.fail("move"),lambda *_:None,lambda *_:None)
if __name__=="__main__":unittest.main()
