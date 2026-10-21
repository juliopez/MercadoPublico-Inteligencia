import sqlite3,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from exportar_operativo_sqlite import exportar

class Hoja:
 def __init__(self,rows):self.rows=rows
 def get_all_values(self):return self.rows
class Libro:
 def __init__(self,tables):self.tables=tables
 def worksheet(self,name):return Hoja(self.tables[name])

class ExportadorTest(unittest.TestCase):
 def test_seis_tablas_e_integridad(self):
  schema={t:["codigo","nombre"] for t in ("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")}
  book=Libro({t:[["codigo","nombre"],[t+"1","A"]] for t in schema})
  with tempfile.TemporaryDirectory() as d:
   dest=Path(d)/"operativo.sqlite";r=exportar(book,schema,dest)
   self.assertEqual(len(r["tablas"]),6)
   with sqlite3.connect(dest) as db:
    self.assertEqual(db.execute('SELECT COUNT(*) FROM Procesos').fetchone()[0],1)
    self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],"ok")
 def test_falla_no_reemplaza_snapshot_valido(self):
  with tempfile.TemporaryDirectory() as d:
   dest=Path(d)/"operativo.sqlite";dest.write_bytes(b"SNAPSHOT_ANTERIOR")
   book=Libro({"Procesos":[["codigo","nombre"],["DUP","X"],["DUP","Y"]]})
   with self.assertRaises(ValueError):exportar(book,{"Procesos":["codigo","nombre"]},dest)
   self.assertEqual(dest.read_bytes(),b"SNAPSHOT_ANTERIOR")
if __name__=="__main__":unittest.main()
