import json,sqlite3,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from politica_conciliacion_cierre import conciliar_fila,auditar
class PoliticaTest(unittest.TestCase):
 def test_completa_vacios_y_preserva_datos(self):
  r,changes,conflicts=conciliar_fila(["id","monto","estado","fecha"],["P1","","Abierta","2026-10-21"],["P1","100","","2026-10-21"])
  self.assertEqual(r,["P1","100","Abierta","2026-10-21"])
  self.assertEqual(changes,["monto"]);self.assertFalse(conflicts)
 def test_conflicto_no_sobrescribe(self):
  r,changes,conflicts=conciliar_fila(["id","estado"],["P1","Abierta"],["P1","Cerrada"])
  self.assertEqual(r,["P1","Abierta"]);self.assertEqual(conflicts,["estado"])
 def test_clave_divergente_bloquea(self):
  with self.assertRaises(ValueError):conciliar_fila(["id","nombre"],["A","a"],["B","b"])
 def test_auditoria_reporta_conflicto(self):
  def mk(rows):
   d=sqlite3.connect(":memory:");d.execute('CREATE TABLE "Procesos" (pk TEXT PRIMARY KEY,fila TEXT)')
   for x in rows:d.execute('INSERT INTO Procesos VALUES (?,?)',(x[0],json.dumps(x)))
   return d
  result=auditar(mk([["P","B"],["N","C"]]),mk([["P","A"],["O","D"]]),{"Procesos":["id","estado"]})
  self.assertEqual(result["estado"],"BLOQUEADO_CONFLICTOS")
  self.assertEqual(result["tablas"]["Procesos"]["conteos"]["solo_operativos"],1)
  self.assertEqual(result["tablas"]["Procesos"]["conteos"]["nuevos"],1)
if __name__=="__main__":unittest.main()
