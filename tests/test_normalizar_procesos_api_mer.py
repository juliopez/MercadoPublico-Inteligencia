import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from normalizar_procesos_api_mer import etiqueta,organismo,proceso,completar_proceso
class NormalizadorTest(unittest.TestCase):
 def test_estado_anidado_no_objeto(self):
  self.assertEqual(etiqueta({"id_estado":4,"codigo":"proveedor_seleccionado"}),"proveedor_seleccionado")
 def test_estado_textual_prioridad(self):
  self.assertEqual(etiqueta({"codigo":"cerrada","descripcion":"Cerrada"}),"Cerrada")
 def test_comprador_anidado(self):
  self.assertEqual(organismo({"organismo_comprador":{"razon_social":"Institución A"}}),"Institución A")
 def test_campos_oficiales_anidados(self):
  from datetime import datetime
  p={"institucion":{"organismo_comprador":"Municipalidad X","nombre_region":"Valparaiso"},"presupuesto":{"monto_disponible_clp":120000},"resumen":{"total_ofertas_recibidas":8},"estado":{"glosa":"Proveedor seleccionado"}}
  r=proceso(p,"123-COT26","2026-10-01",datetime(2026,10,28))
  self.assertEqual(r["organismo_comprador"],"Municipalidad X")
  self.assertEqual(r["monto_disponible_clp"],"120000")
  self.assertEqual(r["total_ofertas_recibidas"],"8")
  self.assertEqual(r["estado"],"Proveedor seleccionado")
 def test_no_modifica_datos_verificados(self):
  old={"codigo":"123-COT26","nombre":"Nombre original","estado":"Cerrada","organismo_comprador":"Comprador oficial","fecha_cierre":"2026-10-03"}
  new={"codigo":"123-COT26","nombre":"Nombre API","estado":"Abierta","organismo_comprador":"Comprador API","fecha_cierre":"2026-10-04"}
  self.assertEqual(completar_proceso(old,new),old)
 def test_corrige_estado_objeto_y_completa_vacio(self):
  old={"codigo":"123-COT26","estado":"{'id_estado': 4}","organismo_comprador":""}
  new={"estado":"cerrada","organismo_comprador":"Municipalidad"}
  res=completar_proceso(old,new)
  self.assertEqual(res["estado"],"cerrada")
  self.assertEqual(res["organismo_comprador"],"Municipalidad")
if __name__=="__main__":unittest.main()
