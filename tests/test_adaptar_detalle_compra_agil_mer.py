import unittest
from adaptar_detalle_compra_agil_mer import adaptar_detalle,OFERTAS,RESULTADOS
class TestAdaptador(unittest.TestCase):
 def setUp(self):
  self.d={"success":True,"payload":{"codigo":"839-4-COT26","motivos":{"motivo_seleccion":"Prueba"},"proveedores_cotizando":[{"id_cotizacion":22,"razon_social":"Ejemplo A","monto_total":12000,"proveedor_seleccionado":True},{"id_cotizacion":23,"razon_social":"Ejemplo B","monto_total":9000,"proveedor_seleccionado":False}]}}
 def test_esquema_y_no_inferencia(self):
  a=adaptar_detalle(self.d)
  self.assertEqual((len(a["ofertas"]),len(a["resultados"])),(2,1))
  self.assertEqual(tuple(a["ofertas"][0]),OFERTAS)
  self.assertEqual(tuple(a["resultados"][0]),RESULTADOS)
  self.assertEqual(a["ofertas"][0]["monto_ofertado_clp"],"")
  self.assertEqual(a["ofertas"][0]["id_proveedor"],"")
  self.assertEqual(a["resultados"][0]["monto_adjudicado_clp"],"")
  self.assertEqual(a["resultados"][0]["id_cotizacion_ganadora"],"22")
 def test_clp_explicito(self):
  self.assertEqual(adaptar_detalle(self.d,clp_verificado=True)["resultados"][0]["monto_oferta_seleccionada_clp"],"12000")
 def test_duplicados(self):
  self.d["payload"]["proveedores_cotizando"][1]["id_cotizacion"]=22
  with self.assertRaises(ValueError): adaptar_detalle(self.d)
 def test_sin_lista(self):
  del self.d["payload"]["proveedores_cotizando"]
  with self.assertRaises(ValueError): adaptar_detalle(self.d)
 def test_seleccion_ambigua(self):
  self.d["payload"]["proveedores_cotizando"][1]["proveedor_seleccionado"]=True
  with self.assertRaises(ValueError): adaptar_detalle(self.d)
 def test_lista_vacia(self):
  self.d["payload"]["proveedores_cotizando"]=[]
  self.assertEqual(adaptar_detalle(self.d)["ofertas"],[])
if __name__=="__main__":unittest.main()
