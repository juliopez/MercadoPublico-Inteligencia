import datetime as dt
import importlib.util
import pathlib
import unittest
from zoneinfo import ZoneInfo

PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts/ubuntu_disparar_api_actions.py"
SPEC = importlib.util.spec_from_file_location("ubuntu_disparar_api_actions", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
TZ = ZoneInfo("America/Santiago")

def instante(s):
    return dt.datetime.fromisoformat(s).replace(tzinfo=TZ)

def run(id_, created_at, status="completed", conclusion="success"):
    return {"id": id_, "created_at": created_at, "status": status, "conclusion": conclusion}


class DisparadorTest(unittest.TestCase):
    def test_2205_laboral(self):
        self.assertEqual(MOD.jornada(instante("2026-11-04T22:05")), (dt.date(2026, 11, 4), True))
    def test_inicio_retrasado_0430(self):
        self.assertEqual(MOD.jornada(instante("2026-11-05T04:30")), (dt.date(2026, 11, 4), True))
    def test_fuera_ventana(self):
        self.assertFalse(MOD.jornada(instante("2026-11-05T05:30"))[1])
    def test_fin_semana(self):
        self.assertFalse(MOD.jornada(instante("2026-11-07T22:05"))[1])
    def test_viernes_retrasado_sabado(self):
        self.assertEqual(MOD.jornada(instante("2026-11-07T04:10")), (dt.date(2026, 11, 6), True))
    def test_ninguna_anterior_permite(self):
        self.assertEqual(MOD.decidir([], dt.date(2026, 11, 4)), (True, "DISPARO_PENDIENTE"))
    def test_no_duplicar_despacho_preexistente(self):
        x = [run(10,"2026-11-05T01:09:00Z","completed")]
        self.assertFalse(MOD.decidir(x, dt.date(2026, 11, 4))[0])
    def test_no_duplicar_schedule_preexistente(self):
        x = [run(12,"2026-11-05T01:11:00Z","in_progress")]
        self.assertFalse(MOD.decidir(x, dt.date(2026, 11, 4))[0])
    def test_no_duplicar_activa_de_dia_anterior(self):
        x = [run(20,"2026-11-04T04:00:00Z","in_progress")]
        self.assertFalse(MOD.decidir(x, dt.date(2026, 11, 4))[0])
    def test_no_bloquear_por_jornada_anterior_completada(self):
        x = [run(30,"2026-11-04T07:27:05Z","completed")]
        self.assertTrue(MOD.decidir(x, dt.date(2026, 11, 4))[0])
    def test_cambio_de_mes(self):
        self.assertEqual(MOD.jornada(instante("2026-12-01T02:30")), (dt.date(2026, 11, 30), True))

if __name__ == "__main__":
    unittest.main()
