import sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from exportar_ofertas_resultados_preview import exportar_tablas,esquema
class ExportPreview(unittest.TestCase):
 def setUp(self):self.s=esquema()
 def test_fragmentos_y_privacidad(self):
  with tempfile.TemporaryDirectory() as t:
   o=dict(zip(self.s["Ofertas"],[""]*9));o.update(id_cotizacion="11",codigo="839-4-COT26",proveedor="Proveedor ficticio",id_proveedor="rut:123",rut_proveedor_cot="12-3",fuente="privada")
   r=dict(zip(self.s["Resultados"],[""]*10));r.update(codigo="839-4-COT26",id_cotizacion_ganadora="11",validado="No")
   tables={"Ofertas":[self.s["Ofertas"],[o[k] for k in self.s["Ofertas"]]],"Resultados":[self.s["Resultados"],[r[k] for k in self.s["Resultados"]]]}
   m=exportar_tablas(tables,"2026-10",Path(t)/"preview")
   self.assertEqual(m["conteos"],{"ofertas":1,"resultados":1})
   text=(Path(t)/"preview"/"partes"/"ofertas"/"2026-10"/"0001.json").read_text()
   self.assertNotIn("rut_proveedor_cot",text)
   self.assertNotIn("id_proveedor",text)
   self.assertNotIn("fuente",text)
 def test_duplicado(self):
  with tempfile.TemporaryDirectory() as t:
   row=[""]*9;row[0]="42";row[1]="839-4-COT26"
   tables={"Ofertas":[self.s["Ofertas"],row,row],"Resultados":[self.s["Resultados"]]}
   with self.assertRaises(ValueError):exportar_tablas(tables,"2026-10",Path(t)/"output")
if __name__=="__main__":unittest.main()
