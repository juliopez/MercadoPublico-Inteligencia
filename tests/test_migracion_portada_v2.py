import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / "scripts" / "generar_portada_v2.py"
SPEC = importlib.util.spec_from_file_location("generar_portada_v2", FILE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class MigracionPortadaV2(unittest.TestCase):
    def test_portada_desde_fuente_v2(self):
        original = (ROOT/"frontend-v2/index.html").read_text(encoding="utf-8")
        result = MOD.render(original)
        self.assertIn('<base href="./frontend-v2/">', result)
        self.assertIn('src="./js/app.js"', result)
        self.assertIn("history.replaceState", result)
        self.assertIn("VERSIÓN ESTABLE", result)
        self.assertNotIn("Versión 1 publicada", result)

    def test_una_sola_copia_datos_en_pages(self):
        workflow = (ROOT/".github/workflows/preview-frontend-v2.yml").read_text()
        self.assertIn("cp -a frontend-v2/. _pages/frontend-v2/", workflow)
        self.assertIn("scripts/generar_portada_v2.py", workflow)
        self.assertIn("test ! -f _pages/data/observatorio.json", workflow)
        self.assertIn("location.replace('../'+location.search+location.hash)", workflow)

    def test_v1_archivada_sin_fragmentos_legacy(self):
        self.assertTrue((ROOT/"historico/v1/index.html").is_file())
        self.assertTrue((ROOT/"historico/v1/observatorio.json").is_file())
        self.assertFalse((ROOT/"data/observatorio.json").exists())
        self.assertFalse((ROOT/"data/partes").exists())
        self.assertTrue((ROOT/"frontend-v2/data/catalogo-publico.json").is_file())

    def test_no_se_puede_publicar_portada_duplicada(self):
        with self.assertRaises(ValueError):
            MOD.render('<head><meta charset="utf-8"><base href="./frontend-v2/"></body>')

if __name__ == "__main__":
    unittest.main()
