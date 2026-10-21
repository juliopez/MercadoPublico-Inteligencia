import json,sqlite3,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from cargador_cierre_mer_v2 import cargar_con_respaldo,TABLAS

class WS:
 def __init__(self):self.data={};self.row_count=100;self.col_count=2
class Book:
 def __init__(self):self.sheets={t:WS() for t in TABLAS}
 def worksheet(self,t):return self.sheets[t]
 def worksheets(self):return list(self.sheets.values())

class RecoveryTest(unittest.TestCase):
 def test_interrupcion_y_reanudacion_sin_duplicados(self):
  db=sqlite3.connect(":memory:")
  for t in TABLAS:
   db.execute('CREATE TABLE "'+t+'" (pk TEXT PRIMARY KEY,fila TEXT)')
   db.execute('INSERT INTO "'+t+'" VALUES (?,?)',("A",json.dumps(["A","dato"])))
  book=Book();eventos=[];count=[0]
  def read(ws,cols):return {k:(i+2,v) for i,(k,v) in enumerate(ws.data.items())}
  def backup(book,schemas,p):return {"sha256":"abc","archivo":"respaldo_prueba.zip"}
  def log(kind,data):eventos.append(kind)
  def failure(ws,cols,rows,current):
   count[0]+=1
   for pk,row in rows:ws.data.setdefault(pk,row)
   if count[0]==2:raise RuntimeError("corte simulado después de escribir")
   return {"nuevos":len(rows)}
  cols={t:["id","valor"] for t in TABLAS}
  with self.assertRaises(RuntimeError):
   cargar_con_respaldo(book,db,cols,"2026-10",read,failure,backup,log)
  self.assertIn("CARGA_INTERRUMPIDA",eventos)
  self.assertNotIn("CARGA_VERIFICADA",eventos)
  self.assertEqual(len(book.worksheet("Ofertas").data),1)
  def normal(ws,cols,rows,current):
   n=0
   for pk,row in rows:
    if pk not in ws.data:ws.data[pk]=row;n+=1
   return {"nuevos":n}
  result=cargar_con_respaldo(book,db,cols,"2026-10",read,normal,backup,log)
  self.assertEqual(result["estado"],"DATOS_CARGADOS_Y_VERIFICADOS_PENDIENTES_DE_AUDITORIA")
  self.assertFalse(result["traslado_autorizado"])
  self.assertTrue(all(len(book.worksheet(t).data)==1 for t in TABLAS))
  self.assertEqual(eventos.count("CARGA_VERIFICADA"),1)
 def test_error_en_bitacora_impide_avance(self):
  db=sqlite3.connect(":memory:")
  for t in TABLAS:db.execute('CREATE TABLE "'+t+'" (pk TEXT PRIMARY KEY,fila TEXT)')
  book=Book()
  def failing_log(kind,data):
   if kind=="RESPALDO_VERIFICADO":raise RuntimeError("fallo de bitácora")
  with self.assertRaises(RuntimeError):
   cargar_con_respaldo(book,db,{t:["id","valor"] for t in TABLAS},"2026-10",
    lambda ws,cols:{},lambda *a:self.fail("No debe escribir"),lambda *a:{"sha256":"abc","archivo":"x"},failing_log)
if __name__=="__main__":unittest.main()
