import json,sqlite3,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from auditar_referencias_cierre import auditar,schema,TABLES

def banco():
 db=sqlite3.connect(":memory:")
 for t in TABLES:db.execute('CREATE TABLE "'+t+'" (pk TEXT PRIMARY KEY, fila TEXT)')
 return db
def poner(db,t,s,vals):
 db.execute('INSERT INTO "'+t+'" VALUES (?,?)',(vals[0],json.dumps(vals)))
class ReferenciasTest(unittest.TestCase):
 def test_corte_externo_es_observacion(self):
  db=banco();s=schema()
  a=[""]*len(s["OrdenesCompra"]);a[0]="OC1";a[1]="PROC_ANTERIOR"
  poner(db,"OrdenesCompra",s,a)
  out=auditar(db,s)
  self.assertFalse(out["errores_bloqueantes"])
  self.assertEqual(out["observaciones"]["oc_proceso_fuera_de_corte"],1)
  self.assertFalse(out["traslado_autorizado"])
 def test_resultado_de_oferta_ajena_bloquea(self):
  db=banco();s=schema()
  for pk in ("P1","P2"):
   a=[""]*len(s["Procesos"]);a[0]=pk;poner(db,"Procesos",s,a)
  a=[""]*len(s["Ofertas"]);a[0]="OF1";a[1]="P2";poner(db,"Ofertas",s,a)
  a=[""]*len(s["Resultados"]);a[0]="P1";a[1]="OF1";poner(db,"Resultados",s,a)
  out=auditar(db,s)
  self.assertEqual(out["errores_bloqueantes"]["resultado_oferta_de_otro_proceso"],1)
  self.assertEqual(out["estado"],"AUDITORIA_BLOQUEADA")
if __name__=="__main__":unittest.main()
