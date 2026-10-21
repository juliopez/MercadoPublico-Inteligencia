import json,sqlite3,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from cargador_cierre_mer_v2 import cargar_con_respaldo,TABLAS

class FakeWS:
 def __init__(self,rows):self.rows=rows;self.row_count=100;self.col_count=2
class FakeBook:
 def __init__(self):self.sheets={t:FakeWS({}) for t in TABLAS}
 def worksheet(self,t):return self.sheets[t]
 def worksheets(self):return list(self.sheets.values())
def make_db():
 db=sqlite3.connect(":memory:")
 for t in TABLAS:
  db.execute('CREATE TABLE "'+t+'" (pk TEXT PRIMARY KEY,fila TEXT)')
  db.execute('INSERT INTO "'+t+'" VALUES (?,?)',("A",json.dumps(["A","dato"])))
 return db
class PruebaCargador(unittest.TestCase):
 def test_respaldo_y_verificacion(self):
  db=make_db();book=FakeBook();hist=[]
  def read(ws,cols):return {k:(idx+2,v) for idx,(k,v) in enumerate(ws.rows.items())}
  def apply(ws,cols,rows,current):
   for pk,row in rows:ws.rows.setdefault(pk,row)
   return {"nuevos":len(rows)}
  def backup(book,schemas,periodo):
   hist.append("respaldo");return {"sha256":"abc","archivo":"ejemplo.zip"}
  def log(etapa,data):hist.append(etapa)
  res=cargar_con_respaldo(book,db,{t:["codigo","valor"] for t in TABLAS},"2026-10",read,apply,backup,log)
  self.assertEqual(hist[0],"respaldo")
  self.assertIn("CARGA_VERIFICADA",hist)
  self.assertFalse(res["traslado_autorizado"])
  self.assertEqual(len(book.worksheet("Procesos").rows),1)
 def test_cambios_bloquean_antes_respaldo(self):
  db=make_db();book=FakeBook();book.worksheet("Ofertas").rows={"A":["A","distinto"]}
  hit=[]
  def read(ws,cols):return {k:(i+2,v) for i,(k,v) in enumerate(ws.rows.items())}
  with self.assertRaises(ValueError):
   cargar_con_respaldo(book,db,{t:["codigo","valor"] for t in TABLAS},"2026-10",read,lambda *a:None,lambda *a:hit.append("respaldo"),lambda *a:None)
  self.assertEqual(hit,[])
if __name__=="__main__":unittest.main()
