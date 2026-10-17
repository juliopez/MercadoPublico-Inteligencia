#!/usr/bin/env python3
"""Validación offline de estructura del detalle V2 y código. No red."""
import importlib.util,json,unittest
from pathlib import Path
source=Path(__file__).with_name("orquestador_v2_detalles_local.py")
spec=importlib.util.spec_from_file_location("detalle_validador_test",source)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
CODE="425-339-COT26"
def response(code=CODE,success="OK",errors=None,quotes=None):
    return json.dumps({"success":success,"errors":errors,"payload":{
        "codigo":code,"institucion":{},"proveedores_cotizando":[] if quotes is None else quotes,
        "productos_solicitados":[]}}).encode()
class TestDetalle(unittest.TestCase):
    def test_detalle_valido(self):
        self.assertEqual(module.validar_detalle(response(),CODE)["payload"]["codigo"],CODE)
    def test_codigo_distinto(self):
        with self.assertRaises(ValueError):module.validar_detalle(response("OTRO-COT26"),CODE)
    def test_error_encapsulado_http200(self):
        with self.assertRaises(ValueError):module.validar_detalle(response(success="ERROR"),CODE)
    def test_errores_reportados(self):
        with self.assertRaises(ValueError):module.validar_detalle(response(errors=[{"message":"fallo"}]),CODE)
    def test_sin_payload(self):
        with self.assertRaises(ValueError):module.validar_detalle(b'{"success":"OK"}',CODE)
    def test_sin_cotizaciones_estructura(self):
        raw=response()
        obj=json.loads(raw)
        del obj["payload"]["proveedores_cotizando"]
        with self.assertRaises(ValueError):module.validar_detalle(json.dumps(obj).encode(),CODE)
if __name__=="__main__":unittest.main(verbosity=2)
