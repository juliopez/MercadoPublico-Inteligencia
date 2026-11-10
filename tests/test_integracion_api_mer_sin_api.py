import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from escribir_api_mer_libro_prueba import operar
from exportar_ofertas_resultados_preview import exportar_tablas
from adaptar_detalle_compra_agil_mer import OFERTAS,RESULTADOS
P=["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"]
class WS:
 def __init__(self,rows,fail_once=False):
  self.rows=[list(r) for r in rows];self.fail_once=fail_once
 def get_all_values(self):return [r[:] for r in self.rows]
 def update(self,*,range_name,values,value_input_option):
  self.rows[int(range_name.split(':')[0][1:])-1]=list(values[0])
 def append_rows(self,rows,*,value_input_option):
  if self.fail_once:
   self.fail_once=False
   raise RuntimeError("Falla de red simulada")
  self.rows.extend([list(r) for r in rows])
class Book:
 def __init__(self,fail=False):
  self.tabs={"Ofertas":WS([list(OFERTAS)]),
   "Resultados":WS([list(RESULTADOS)],fail_once=fail),
   "Proveedores":WS([P,["rut:765117682","765117682","Proveedor de prueba","","OC","RUT_SIN_CONTRASTE"]])}
 def worksheet(self,name):return self.tabs[name]
class Integration(unittest.TestCase):
 def setUp(self):
  self.data={"codigo":"839-4-COT26",
    "ofertas":[{"id_cotizacion":"COT-123","codigo":"839-4-COT26","proveedor":"Proveedor sintético","rut_proveedor_cot":"76.511.768-2","seleccionado":"1","fuente":"SIMULACION"}],
    "resultados":[{"codigo":"839-4-COT26","id_cotizacion_ganadora":"COT-123","validado":"NO: prueba sintética","fuente":"SIMULACION"}]}
 def test_falla_parcial_recuperacion_y_publicacion_aislada(self):
  with tempfile.TemporaryDirectory() as t:
   book=Book(fail=True);lock=Path(t)/"lock"
   with self.assertRaisesRegex(RuntimeError,"ESCRITURA_PARCIAL_POSIBLE"):
    operar(book,self.data,lockpath=lock,respaldo=Path(t)/"primer_respaldo.json")
   self.assertEqual(len(book.tabs["Ofertas"].rows),2)
   self.assertEqual(len(book.tabs["Resultados"].rows),1)
   self.assertTrue((Path(t)/"primer_respaldo.json").exists())
   second=operar(book,self.data,lockpath=lock,respaldo=Path(t)/"segundo_respaldo.json")
   self.assertEqual(second["tablas"]["Ofertas"]["insertados"],0)
   self.assertEqual(second["tablas"]["Resultados"]["insertados"],1)
   third=operar(book,self.data,lockpath=lock,respaldo=Path(t)/"tercer_respaldo.json")
   self.assertEqual(third["tablas"]["Ofertas"]["insertados"],0)
   self.assertEqual(third["tablas"]["Resultados"]["insertados"],0)
   snapshot={"Ofertas":book.tabs["Ofertas"].get_all_values(),"Resultados":book.tabs["Resultados"].get_all_values()}
   public=exportar_tablas(snapshot,"2026-10",Path(t)/"preview")
   self.assertEqual(public["conteos"],{"ofertas":1,"resultados":1})
   for entity in ("ofertas","resultados"):
    file=Path(t)/"preview"/"partes"/entity/"2026-10"/"0001.json"
    rows=json.loads(file.read_text())
    self.assertEqual(len(rows),1)
    self.assertNotIn("rut_proveedor_cot",rows[0])
    self.assertNotIn("id_proveedor",rows[0])
   self.assertEqual(len(list((Path(t)/"preview").rglob("*.json"))),3)
if __name__=="__main__":unittest.main()
