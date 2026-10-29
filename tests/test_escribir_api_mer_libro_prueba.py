import tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from escribir_api_mer_libro_prueba import operar
from adaptar_detalle_compra_agil_mer import OFERTAS,RESULTADOS
P=["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"]
class WS:
 def __init__(self,rows):self.rows=[list(r) for r in rows]
 def get_all_values(self):return [list(r) for r in self.rows]
 def update(self,*,range_name,values,value_input_option):self.rows[int(range_name.split(":")[0][1:])-1]=list(values[0])
 def append_rows(self,rows,*,value_input_option):self.rows.extend(list(r) for r in rows)
class Book:
 def __init__(self):
  self.tabs={"Ofertas":WS([list(OFERTAS)]),"Resultados":WS([list(RESULTADOS)]),
             "Proveedores":WS([P,["rut:765117682","765117682","Test","","OC","RUT_SIN_CONTRASTE"]])}
 def worksheet(self,n):return self.tabs[n]
class WriterTests(unittest.TestCase):
 def test_escritura_verificada_idempotente(self):
  b=Book()
  trans={"codigo":"839-4-COT26","ofertas":[{"codigo":"839-4-COT26","id_cotizacion":"7","rut_proveedor_cot":"76.511.768-2"}],
         "resultados":[{"codigo":"839-4-COT26","id_cotizacion_ganadora":"7","validado":"No"}]}
  with tempfile.TemporaryDirectory() as d:
   first=operar(b,trans,lockpath=Path(d)/"lock",respaldo=Path(d)/"b1.json")
   second=operar(b,trans,lockpath=Path(d)/"lock",respaldo=Path(d)/"b2.json")
   self.assertEqual(first["tablas"]["Ofertas"]["insertados"],1)
   self.assertEqual(second["tablas"]["Ofertas"]["insertados"],0)
   self.assertEqual(second["tablas"]["Resultados"]["insertados"],0)
   self.assertEqual(b.tabs["Ofertas"].rows[1][2],"rut:765117682")
 def test_conflicto_sin_escritura(self):
  b=Book()
  row=[""]*len(OFERTAS);row[0]="7";row[1]="839-4-COT26";row[3]="Proveedor original"
  b.tabs["Ofertas"].rows.append(row)
  trans={"ofertas":[{"codigo":"839-4-COT26","id_cotizacion":"7","proveedor":"Otro proveedor"}],"resultados":[]}
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):operar(b,trans,lockpath=Path(d)/"lock",respaldo=Path(d)/"b.json")
   self.assertEqual(b.tabs["Ofertas"].rows[1][3],"Proveedor original")
   self.assertFalse((Path(d)/"b.json").exists())
if __name__=="__main__":unittest.main()
