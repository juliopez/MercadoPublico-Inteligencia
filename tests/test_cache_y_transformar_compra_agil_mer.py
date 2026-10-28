import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from cache_y_transformar_compra_agil_mer import private_json, transform_cached, read_validated

class CacheTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.root=Path(self.tmp.name)
  self.source=self.root/"respuestas"/"839-4-COT26.json"
  self.out=self.root/"transformadas"/"839-4-COT26.json"
  self.payload={"success":True,"payload":{"codigo":"839-4-COT26","proveedores_cotizando":[
   {"id_cotizacion":101,"razon_social":"Empresa ficticia","monto_total":1500,"fecha_creacion":"2026-10-20","proveedor_seleccionado":True}
  ],"motivos":{"motivo_seleccion":"Prueba"}}}
 def tearDown(self): self.tmp.cleanup()
 def test_cache_reutilizable(self):
  private_json(self.source,self.payload)
  a=transform_cached(self.source,"839-4-COT26",self.out)
  self.assertEqual((a["ofertas"],a["resultados"]),(1,1))
  mer=json.loads(self.out.read_text())
  self.assertEqual(mer["ofertas"][0]["monto_ofertado_clp"],"")
  self.assertEqual(mer["resultados"][0]["monto_adjudicado_clp"],"")
  self.assertEqual(self.source.stat().st_mode&0o777,0o600)
  self.assertEqual(self.out.stat().st_mode&0o777,0o600)
 def test_evitar_sobreescritura(self):
  private_json(self.source,self.payload)
  with self.assertRaises(FileExistsError):private_json(self.source,self.payload)
 def test_rechazar_codigo_distinto(self):
  private_json(self.source,self.payload)
  with self.assertRaises(ValueError):read_validated(self.source,"123-2-COT26")
 def test_rechazar_payload_invalido(self):
  private_json(self.source,{"success":False,"payload":{}})
  with self.assertRaises(ValueError):transform_cached(self.source,"839-4-COT26",self.out)
if __name__=="__main__":unittest.main()
