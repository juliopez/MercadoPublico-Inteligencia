#!/usr/bin/env python3
"""Cargador MER v2: motor real preparado, ESCRITURAS DESHABILITADAS.

Separa verificación y operación de escritura. La función interna cargar_con_respaldo
solo podrá invocarse tras una futura aprobación técnica y prueba supervisada.
La CLI no ofrece --aplicar: nunca modifica Google Sheets.
"""
import argparse,datetime as dt,importlib.util,json,os,sqlite3,sys
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
TABLAS=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")

def importar(nombre,ruta):
 spec=importlib.util.spec_from_file_location(nombre,ROOT/"scripts"/ruta)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 return mod

def evaluar_diferencias(registros,existentes):
 """Conservador: propone solo insertar claves nuevas; no actualizar ni borrar."""
 nuevos=modificados=iguales=0
 for pk,row in registros:
  if pk not in existentes:nuevos+=1
  elif existentes[pk][1]==row:iguales+=1
  else:modificados+=1
 return {"nuevos":nuevos,"modificados_bloqueados":modificados,"iguales":iguales}

def cargar_con_respaldo(book,db,schemas,periodo,readback,aplicar,backup,registrar):
 """Motor desacoplado para pruebas con dobles; jamás llamarlo en la CLI actual.

 Invariantes: seis tablas, respaldo ANTES de escribir, nuevas PK únicamente,
 verificación posterior de cada tabla, bitácora. No archiva ni cierra el mes.
 """
 if set(schemas)!=set(TABLAS):raise ValueError("Contrato de seis tablas MER incompleto")
 resultado={"periodo":periodo,"tablas":{},"cierre_autorizado":False,"traslado_autorizado":False}
 estado={}
 for tab in TABLAS:
  ws=book.worksheet(tab)
  estado[tab]=readback(ws,schemas[tab])
 # Prever crecimiento de grilla: límite de 10 millones de celdas por spreadsheet.
 expected_add=0
 for tab in TABLAS:
  cols=schemas[tab]; origen=list(db.execute('SELECT pk,fila FROM "'+tab+'"'))
  rows=[]
  for pk,raw in origen:
   row=[str(v or "") for v in json.loads(raw)]
   if len(row)!=len(cols) or row[0]!=pk:raise ValueError("Origen inválido "+tab)
   rows.append((pk,row))
  diferencia=evaluar_diferencias(rows,estado[tab])
  resultado["tablas"][tab]=diferencia
  expected_add+=diferencia["nuevos"]*len(cols)
  if diferencia["modificados_bloqueados"]:
   raise ValueError("Modificados requieren política y aprobación: "+tab)
 grid=sum(w.row_count*w.col_count for w in book.worksheets())
 if grid+expected_add>10_000_000:raise ValueError("Límite de celdas proyectado excedido")
 # El backup debe ser verificable y registrar manifest de las seis tablas.
 copia=backup(book,schemas,periodo)
 if not copia.get("sha256") or not copia.get("archivo"):
  raise ValueError("Respaldo incompleto")
 resultado["respaldo"]=copia
 registrar("RESPALDO_VERIFICADO",resultado)
 try:
  _ejecutar_tablas(book,db,schemas,readback,aplicar,registrar,resultado)
 except BaseException as exc:
  resultado["estado"]="CARGA_INCOMPLETA_BLOQUEADA"
  resultado["error"]=repr(exc)
  registrar("CARGA_INTERRUMPIDA",resultado)
  raise
 return resultado

def _ejecutar_tablas(book,db,schemas,readback,aplicar,registrar,resultado):
 # Cada etapa vuelve a consultar el destino: reinicio tras fallos no duplica PK.
 for tab in TABLAS:
  ws=book.worksheet(tab)
  current=readback(ws,schemas[tab])
  rows=[]
  for pk,raw in db.execute('SELECT pk,fila FROM "'+tab+'" ORDER BY pk'):
   row=[str(v or "") for v in json.loads(raw)]
   if pk in current and current[pk][1]!=row:
    raise ValueError("Destino divergente durante la carga: "+tab+" "+pk)
   rows.append((pk,row))
  resultado["tablas"][tab]["aplicado"]=aplicar(ws,schemas[tab],rows,current)
  actual=readback(ws,schemas[tab])
  for pk,row in rows:
   if pk not in actual or actual[pk][1]!=row:
    raise ValueError("Verificación post-carga falló: "+tab+" "+pk)
  registrar("TABLA_VERIFICADA:"+tab,resultado)
 resultado["estado"]="DATOS_CARGADOS_Y_VERIFICADOS_PENDIENTES_DE_AUDITORIA"
 registrar("CARGA_VERIFICADA",resultado)


def cargar_con_adaptadores_etl(book,db,schemas,periodo,registrar,confirmacion=None):
 """Adaptador real del motor al ETL diario; solo llamable desde orquestador autorizado.

 ¡No autoriza por sí mismo la escritura! El llamador debe asegurar flock,
 informe de cierre validado, credenciales, aprobación externa y lectura coherente.
 El adaptador mantiene política segura de SOLO ALTAS; toda divergencia bloquea.
 """
 if confirmacion!="CIERRE_SUPERVISADO_AUTORIZADO":
  raise PermissionError("Sin autorización supervisada del cierre")
 etl=importar("etl_operativo_cierre","etl_zip_dos_fuentes.py")
 return cargar_con_respaldo(
  book=book,db=db,schemas=schemas,periodo=periodo,
  readback=etl.worksheet_rows,
  aplicar=etl.aplicar_tabla,
  backup=etl.respaldo_local,
  registrar=registrar,
 )

def main():
 p=argparse.ArgumentParser(description="Preflight del cargador: sin escrituras ni autorización de cierre")
 p.add_argument("--paquete",type=Path,required=True)
 p.add_argument("--plan",type=Path,required=True)
 p.add_argument("--salida",type=Path)
 a=p.parse_args()
 plan=json.loads(a.plan.read_text(encoding="utf8"))
 if plan.get("autorizado_para_escribir") is not False:
  p.error("Plan inesperadamente autoriza escritura: se bloquea")
 if plan.get("estado")!="PLAN_DE_CARGA_BLOQUEADO_HASTA_AUDITORIA_Y_APROBACION":
  p.error("Plan sin estado de seguridad esperado")
 informe=json.loads((a.paquete/"informe.json").read_text(encoding="utf8"))
 if informe.get("periodo")!=plan.get("periodo") or informe.get("validacion_filas")!="OK":
  p.error("Paquete no corresponde al plan")
 for t in TABLAS:
  if t not in informe or t not in plan.get("acciones_candidatas",{}):
   p.error("Falta entidad "+t)
 resumen={"estado":"PREPARADO_SIN_ESCRITURAS","periodo":plan["periodo"],
  "fecha_chile":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),
  "reglas":"Solo altas; cualquier modificación preexistente bloquea el motor",
  "modificados_detectados":sum(plan["acciones_candidatas"][t]["actualizar_candidatos_sujetos_a_revision"] for t in TABLAS),
  "capacidad_de_escritura_en_CLI":False,"cierre_autorizado":False,
  "pendiente":"Validación con dobles de Google Sheets, política de modificados, autorización supervisada y recuperación"}
 salida=a.salida or a.paquete.parent/"preflight_cargador.json"
 salida.parent.mkdir(parents=True,exist_ok=True)
 salida.write_text(json.dumps(resumen,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("CARGADOR PREPARADO SIN ESCRITURAS:",salida)
if __name__=="__main__":main()
