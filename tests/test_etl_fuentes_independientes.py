#!/usr/bin/env python3
"""Pruebas aisladas del ETL ZIP operativo; no usa red, credenciales ni Google Sheets."""
import csv
import datetime as dt
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

REPO=Path(__file__).resolve().parents[1]
def cargar(path,nombre):
 spec=importlib.util.spec_from_file_location(nombre,path)
 mod=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(mod)
 return mod

etl=cargar(REPO/"scripts/etl_zip_dos_fuentes.py","etl_aislado")
historicos=cargar(REPO/"scripts/importador_historicos_v2.py","historicos_aislado")

def zip_csv(destino,headers,rows,archivo):
 buffer=io.StringIO(newline="")
 writer=csv.DictWriter(buffer,fieldnames=headers,delimiter=";")
 writer.writeheader()
 writer.writerows(rows)
 with zipfile.ZipFile(destino,"w") as z:
  z.writestr(archivo,buffer.getvalue().encode("latin-1"))

class PruebaFuentesIndependientes(unittest.TestCase):
 def ejecutar(self,lic,oc):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   (root/"config").mkdir()
   mes=dt.datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m")
   catalogo={"periodos":{mes:{"tipo":"operativo","id":"sheet-de-prueba"}}}
   fuentes={"fuentes":{"licitaciones":"https://ejemplo/licitaciones/{yyyy}-{mm}.zip",
                       "ordenes_compra":"https://ejemplo/oc/{yyyy}-{mm}.zip"}}
   (root/"config/catalogo_sheets.json").write_text(json.dumps(catalogo))
   (root/"config/fuentes_descarga_mensual.json").write_text(json.dumps(fuentes))
   def simular_descarga(url,path):
    if "/licitaciones/" in url:
     zip_csv(path,["Codigo","Nombre","CodigoExterno"],lic,"licitaciones.csv")
    else:
     zip_csv(path,["Codigo","NombreProveedor","RutSucursal","FechaCreacion","CodigoLicitacion"],oc,"oc.csv")
    return {"url":url,"sha256":"falso-test","bytes":path.stat().st_size}
   with patch.object(etl,"ROOT",root),patch.object(etl,"importar",return_value=historicos),patch.object(etl,"descargar",side_effect=simular_descarga),patch.object(sys,"argv",["etl","--salida",str(root/"salida")]):
    etl.main()
   return json.loads((root/"salida"/f"etl_zip_operativo_{mes}.json").read_text())

 def test_solo_oc_con_licitaciones_vacias(self):
  rep=self.ejecutar([], [{"Codigo":"1-1-SE26","NombreProveedor":"Empresa Demo","RutSucursal":"12345678-5","FechaCreacion":"2026-11-02"}])
  self.assertEqual(rep["estado"],"PREPARADO_SIN_ESCRITURAS")
  self.assertEqual(rep["preparados"]["OrdenesCompra"],1)
  self.assertEqual(rep["tablas_no_modificadas"],["Procesos"])
  self.assertEqual(rep["cobertura_fuentes"]["licitaciones"],"CSV_SIN_REGISTROS")

 def test_solo_licitaciones_con_oc_vacias(self):
  rep=self.ejecutar([{"Codigo":"L-1","CodigoExterno":"L-1","Nombre":"Prueba"}],[])
  self.assertEqual(rep["preparados"]["Procesos"],1)
  self.assertEqual(rep["tablas_no_modificadas"],["OrdenesCompra"])
  self.assertNotIn("Proveedores",rep["preparados"])

 def test_ambas_fuentes_con_datos(self):
  rep=self.ejecutar([{"Codigo":"L-1","Nombre":"Prueba"}],
     [{"Codigo":"1-1-SE26","NombreProveedor":"Empresa Demo","RutSucursal":"12345678-5"}])
  self.assertEqual(rep["tablas_no_modificadas"],[])
  self.assertEqual(rep["preparados"]["Procesos"],1)
  self.assertEqual(rep["preparados"]["OrdenesCompra"],1)

 def test_ambas_fuentes_vacias_bloqueadas(self):
  with self.assertRaisesRegex(ValueError,"Ambas fuentes"):
   self.ejecutar([],[])

 def test_filas_sin_codigo_no_se_aceptan_como_vacias(self):
  with self.assertRaisesRegex(ValueError,"Licitaciones tiene filas"):
   self.ejecutar([{"Codigo":"","CodigoExterno":"","Nombre":"Prueba"}],
      [{"Codigo":"1-1-SE26","NombreProveedor":"Empresa Demo","RutSucursal":"12345678-5"}])

if __name__=="__main__":
 unittest.main()
