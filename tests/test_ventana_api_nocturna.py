import datetime as dt
import importlib.util
import pathlib
import unittest
from zoneinfo import ZoneInfo

P = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "ventana_api_nocturna.py"
spec = importlib.util.spec_from_file_location("ventana_api_nocturna", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
CL = ZoneInfo("America/Santiago")

class VentanaNocturna(unittest.TestCase):
    def check(self, fecha, habilitada, objetivo, razon):
        ok, dia, motivo = mod.evaluar(dt.datetime.fromisoformat(fecha).replace(tzinfo=CL))
        self.assertEqual((ok, str(dia), motivo), (habilitada, objetivo, razon))

    def test_inicio_martes_22(self):
        self.check("2026-11-03T22:05:00", True, "2026-11-03", "AUTORIZADA")
    def test_retraso_martes_23(self):
        self.check("2026-11-03T23:45:00", True, "2026-11-03", "AUTORIZADA")
    def test_retraso_miercoles_02(self):
        self.check("2026-11-04T02:30:00", True, "2026-11-03", "AUTORIZADA")
    def test_retraso_miercoles_04(self):
        self.check("2026-11-04T04:45:00", True, "2026-11-03", "AUTORIZADA")
    def test_fuera_de_ventana_05(self):
        self.check("2026-11-04T05:00:00", False, "2026-11-03", "FUERA_VENTANA")
    def test_no_corresponde_lunes_de_madrugada(self):
        self.check("2026-11-02T02:30:00", False, "2026-11-01", "JORNADA_FIN_SEMANA")
    def test_retraso_viernes_a_sabado(self):
        self.check("2026-11-07T02:30:00", True, "2026-11-06", "AUTORIZADA")
    def test_sabado_noche_no_corresponde(self):
        self.check("2026-11-07T22:05:00", False, "2026-11-07", "JORNADA_FIN_SEMANA")
    def test_dia_uno_mes_siguiente(self):
        self.check("2026-12-01T02:30:00", True, "2026-11-30", "AUTORIZADA")

if __name__ == "__main__":
    unittest.main()
