import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from verificar_metadata_traslado import comprobar
C={"periodos":{"2026-10":{"tipo":"operativo","id":"A"}},"carpetas":{"operativo":"O"}}
D={"id":"A","title":"MER_2026_10_OPERATIVO","parent_ids":["O"],"mime_type":"application/vnd.google-apps.spreadsheet","permissions":[{"type":"user","role":"owner"}]}
class TestMetadata(unittest.TestCase):
 def test_coincidente(self):
  self.assertEqual(comprobar("2026-10",C,D)["estado"],"METADATOS_CONSISTENTES")
 def test_permiso_general_edicion_bloquea(self):
  d=dict(D,permissions=[{"type":"anyone","role":"writer"}])
  self.assertIn("EDICION_GENERAL_NO_RESTRINGIDA",comprobar("2026-10",C,d)["alertas"])
 def test_padre_incorrecto_bloquea(self):
  d=dict(D,parent_ids=["H"])
  self.assertIn("CARPETA_DIVERGENTE",comprobar("2026-10",C,d)["alertas"])
 def test_sin_metadatos_permisos_bloquea(self):
  d=dict(D,permissions=None)
  self.assertIn("PERMISOS_NO_VERIFICABLES",comprobar("2026-10",C,d)["alertas"])
if __name__=="__main__":unittest.main()
