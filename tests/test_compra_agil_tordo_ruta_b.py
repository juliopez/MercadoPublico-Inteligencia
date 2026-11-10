"""Pruebas unitarias sin red ni acceso MER."""
import importlib.util, pathlib, unittest, datetime as dt
p=pathlib.Path(__file__).resolve().parents[1]/"scripts"/"compra_agil_tordo_ruta_b.py"
spec=importlib.util.spec_from_file_location("tordo_piloto",p)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class TestTordo(unittest.TestCase):
    def test_utc_a_chile(self):
        self.assertEqual(mod.date("2026-11-10T02:30:00Z"),"2026-11-09")
    def test_fecha_local(self):
        self.assertEqual(mod.date("2026-11-05T10:00:00"),"2026-11-05")
    def test_codigo_invalido(self):
        with self.assertRaises(ValueError):
            mod.row({"codigo_externo":"INVALIDO","fecha_publicacion":"2026-11-05T10:00:00"},"2026-11-10")
    def test_campos_y_modalidad(self):
        x={"codigo_externo":"835727-266-COT26","fecha_publicacion":"2026-11-05T10:00:00","nombre":"Prueba","tipo_convocatoria":"compra_agil"}
        r=mod.row(x,"2026-11-10")
        self.assertEqual(list(r),mod.COLUMNS)
        self.assertEqual(r["modalidad"],"Compra Ágil")
        self.assertEqual(r["codigo"],"835727-266-COT26")
if __name__=="__main__":unittest.main()
