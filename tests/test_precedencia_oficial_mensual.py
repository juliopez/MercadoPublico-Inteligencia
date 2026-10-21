import json,sqlite3,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from cargador_cierre_mer_v2 import preparar_carga_conciliada,TABLAS

class PrioridadHistoricoMensual(unittest.TestCase):
 def test_historico_oficial_reemplaza_y_conserva_solo_operativos(self):
  schemas={t:["codigo","estado","monto"] for t in TABLAS}
  db=sqlite3.connect(":memory:")
  estado={}
  for t in TABLAS:
   db.execute('CREATE TABLE "'+t+'" (pk TEXT PRIMARY KEY,fila TEXT NOT NULL)')
   db.execute('INSERT INTO "'+t+'" VALUES (?,?)',("A",json.dumps(["A","OFICIAL",""])))
   db.execute('INSERT INTO "'+t+'" VALUES (?,?)',("B",json.dumps(["B","NUEVO","200"])))
   estado[t]={"A":(2,["A","OPERATIVO","100"]),"Z":(3,["Z","SOLO_OPERATIVO","300"])}
  policy={"periodo":"2026-10","fuente_prioritaria":"HISTORICO_OFICIAL_MENSUAL","estado":"PRECEDENCIA_OFICIAL_DOCUMENTADA"}
  filas,stats=preparar_carga_conciliada(db,schemas,estado,policy)
  for t in TABLAS:
   rows=dict(filas[t])
   self.assertEqual(rows["A"],["A","OFICIAL",""])
   self.assertEqual(rows["B"],["B","NUEVO","200"])
   self.assertNotIn("Z",rows)
   self.assertEqual(stats[t]["actualizados_por_fuente_oficial"],1)
   self.assertEqual(stats[t]["solo_operativo_conservado"],1)
 def test_rechazo_fuente_no_aprobada(self):
  with self.assertRaises(ValueError):
   preparar_carga_conciliada(None,{t:["codigo"] for t in TABLAS},{t:{} for t in TABLAS},{"estado":"BLOQUEADO"})
if __name__=="__main__":unittest.main()
