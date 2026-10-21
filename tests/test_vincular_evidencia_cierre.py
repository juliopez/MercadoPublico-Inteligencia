#!/usr/bin/env python3
"""Prueba sin red de evidencia vinculada y detección de alteraciones."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from vincular_evidencia_cierre import verificar,TABLES
class EvidenciaTest(unittest.TestCase):
 def test_consistencia_y_bloqueo(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);prep=root/"preparados";prep.mkdir()
   for t in TABLES:(prep/(t+".csv")).write_text("codigo\n")
   (prep/"preparado.sqlite").write_bytes(b"contenido-prueba")
   def write(name,obj):
    path=root/name;path.write_text(json.dumps(obj));return path
   r={"periodo":"2026-10","validacion_filas":"OK",**{t:2 for t in TABLES}}
   (prep/"informe.json").write_text(json.dumps(r))
   conc=write("conciliacion.json",{"periodo":"2026-10","estado":"CONCILIACION_INFORMATIVA_REQUIERE_REVISION","spreadsheet_id":"id1","tablas":{t:{"filas_historico":2,"nuevos":1,"modificados":1,"solo_operativo":0} for t in TABLES}})
   plan=write("plan.json",{"periodo":"2026-10","estado":"PLAN_DE_CARGA_BLOQUEADO_HASTA_AUDITORIA_Y_APROBACION","spreadsheet_id":"id1","autorizado_para_escribir":False,"autorizado_para_mover":False,"acciones_candidatas":{t:{"insertar_candidatos":1,"actualizar_candidatos_sujetos_a_revision":1,"solo_operativo_sin_borrado":0} for t in TABLES}})
   state=write("estado.json",{"periodo":"2026-10","estado":"LISTO_PARA_CONCILIAR","hoja_operativa_origen":"id1"})
   catalog=write("catalog.json",{"periodos":{"2026-10":{"tipo":"operativo","id":"id1"}}})
   out=verificar("2026-10",prep,conc,plan,catalog,state)
   self.assertFalse(out["escritura_autorizada"])
   self.assertEqual(len(out["archivos"]),12)
   changed=json.loads(plan.read_text());changed["acciones_candidatas"]["Procesos"]["insertar_candidatos"]=99
   plan.write_text(json.dumps(changed))
   with self.assertRaises(ValueError):verificar("2026-10",prep,conc,plan,catalog,state)
if __name__=="__main__":unittest.main()
