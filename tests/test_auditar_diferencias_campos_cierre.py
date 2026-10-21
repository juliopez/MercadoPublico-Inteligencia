import json,sqlite3,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from auditar_diferencias_campos_cierre import diferencias
def make(rows):
 db=sqlite3.connect(":memory:")
 db.execute('CREATE TABLE "Procesos" (pk TEXT PRIMARY KEY,fila TEXT)')
 for r in rows:db.execute('INSERT INTO Procesos VALUES (?,?)',(r[0],json.dumps(r)))
 return db
class DiferenciasTest(unittest.TestCase):
 def test_campos_y_filas_preservados(self):
  src=make([["A","nombre nuevo"],["B","igual"],["C","nuevo"]])
  dst=make([["A","nombre anterior"],["B","igual"],["D","solo operativo"]])
  r=diferencias(src,dst,{"Procesos":["codigo","nombre"]})["Procesos"]
  self.assertEqual((r["nuevos"],r["modificados"],r["iguales"],r["solo_operativo"]),(1,1,1,1))
  self.assertEqual(r["campos_modificados"]["nombre"],1)
  self.assertEqual(r["muestras_pk_por_campo"]["nombre"],["A"])
 def test_inconsistencia_filas_bloquea(self):
  src=make([["A","nombre","exceso"]]);dst=make([])
  with self.assertRaises(ValueError):diferencias(src,dst,{"Procesos":["codigo","nombre"]})
if __name__=="__main__":unittest.main()
