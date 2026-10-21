import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from evaluar_cierre_mensual import evaluar
T=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")
def datos():
 period="2026-10";sid="sheet1"
 cat={"periodos":{period:{"tipo":"operativo","id":sid}}}
 prep={"periodo":period,"estado":"LISTO_PARA_CONCILIAR","hoja_operativa_origen":sid}
 conc={"periodo":period,"estado":"CONCILIACION_INFORMATIVA_REQUIERE_REVISION","spreadsheet_id":sid,"tablas":{t:{} for t in T}}
 plan={"periodo":period,"estado":"PLAN_DE_CARGA_BLOQUEADO_HASTA_AUDITORIA_Y_APROBACION","spreadsheet_id":sid,"autorizado_para_escribir":False,"autorizado_para_mover":False}
 audit={"periodo":period,"estado":"AUDITORIA_ESTRUCTURAL_SIN_ERRORES_CON_OBSERVACIONES","errores_bloqueantes":{},"observaciones":{},"conteos":{t:1 for t in T}}
 rev={"periodo":period,"estado":"OPERATIVO_SIN_CAMBIOS_DESDE_CONCILIACION","spreadsheet_id":sid,"tablas":{t:{} for t in T}}
 carga={"periodo":period,"estado":"DATOS_CARGADOS_Y_VERIFICADOS_PENDIENTES_DE_AUDITORIA","spreadsheet_id":sid,"respaldo":{"sha256":"abc"},"tablas":{t:{} for t in T}}
 return period,cat,prep,conc,plan,audit,rev,carga
class FinalTest(unittest.TestCase):
 def test_falta_carga_bloquea(self):
  args=list(datos());args[-1]["estado"]="AUSENTE"
  r=evaluar(*args);self.assertEqual(r["estado"],"BLOQUEADO");self.assertFalse(r["traslado_autorizado"])
 def test_todo_verde_no_autoriza_traslado(self):
  r=evaluar(*datos());self.assertEqual(r["estado"],"CANDIDATO_A_APROBACION_SUPERVISADA")
  self.assertFalse(r["traslado_autorizado"]);self.assertFalse(r["cierre_autorizado"])
 def test_observaciones_impiden_aprobacion_directa(self):
  args=list(datos());args[5]["observaciones"]={"oc_proceso_fuera_de_corte":7}
  self.assertEqual(evaluar(*args)["estado"],"BLOQUEADO")
if __name__=="__main__":unittest.main()
