"""Pruebas unitarias autocontenidas del índice de búsqueda v2."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/indexar_busqueda_frontend_v2.py"
spec = importlib.util.spec_from_file_location("indexar_busqueda_v2", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class SearchIndexTest(unittest.TestCase):
    def test_index_complete_and_selective(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "data/partes/procesos/2026-06"
            base.mkdir(parents=True)
            rows = [
                {"codigo": "100-1-LE26", "nombre": "Servicio de capacitación", "organismo_comprador": "Universidad Pública"},
                {"codigo": "100-2-COT26", "nombre": "Material de oficina", "organismo_comprador": "Municipalidad"},
            ]
            (base / "0001.json").write_text(json.dumps(rows), encoding="utf-8")
            manifest = {"periodos": [{"periodo":"2026-06","conteos":{"procesos":2},
                        "partes":{"procesos":["data/partes/procesos/2026-06/0001.json"]}}]}
            (root / "data/catalogo-publico.json").write_text(json.dumps(manifest), encoding="utf-8")
            mod.build("2026-06", "procesos", root)
            output = root / "data/busqueda/2026-06/procesos"
            meta = json.loads((output / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["conteo"], 2)
            for prefix in ("ser","cap","uni"):
                self.assertTrue((output / f"{prefix}.json").exists())
                found = json.loads((output / f"{prefix}.json").read_text(encoding="utf-8"))
                self.assertTrue(any(row[1] == 0 for row in found))
            other = json.loads((output / "mat.json").read_text(encoding="utf-8"))
            self.assertTrue(any(row[1] == 1 for row in other))
    def test_detects_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data/partes/procesos/2026-06").mkdir(parents=True)
            (root / "data/partes/procesos/2026-06/0001.json").write_text('[]', encoding="utf-8")
            (root / "data/catalogo-publico.json").write_text(json.dumps({"periodos":[{"periodo":"2026-06","conteos":{"procesos":1},"partes":{"procesos":["data/partes/procesos/2026-06/0001.json"]}}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                mod.build("2026-06","procesos",root)

if __name__ == "__main__":
    unittest.main()
