"""Cargador genérico MER v2 para períodos arbitrarios: simulación, respaldo y append idempotente.

Solo se escribe en la base MER v2 explícitamente autorizada.
"""
import csv,io,json,zipfile,hashlib,time,datetime,collections
from google.colab import auth,files
from google.auth import default
from googleapiclient.discovery import build
import gspread

DESTINO="1lnMVUZ_pn_HkwEvI90yYz5GOMSYzuX-FbcbMR71-oDA"
PRODUCCION="1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4"
CLON_ANTERIOR="1loeK_IM3RXHaR7CqpjUbz-TsNgOKNrV1ejq8aRC6JyE"
assert DESTINO not in {PRODUCCION,CLON_ANTERIOR}
TABLAS={
"Procesos":("codigo",["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre","monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas","motivo_seleccion","url_detalle","fecha_sincronizacion","categoria","subcategoria","modalidad"]),
"Proveedores":("id_proveedor",["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"]),
"Ofertas":("id_cotizacion",["id_cotizacion","codigo","id_proveedor","proveedor","monto_ofertado_clp","fecha_oferta","fuente","seleccionado","rut_proveedor_cot"]),
"OrdenesCompra":("codigo_oc",["codigo_oc","codigo_proceso","id_proveedor","fecha_creacion","fecha_aceptacion","estado","proveedor","monto_total_oc_clp","tipo_oc","cantidad_lineas","total_lineas_neto","rut_sucursal_oc","codigo_proveedor_oc"]),
"VinculosCOT_OC":("id_vinculo",["id_vinculo","codigo_cot","codigo_oc","origen_vinculo","estado_oc_historico","fecha_aceptacion_oc","relacion_confiable"]),
"Resultados":("codigo",["codigo","id_cotizacion_ganadora","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado","monto_oferta_seleccionada_clp","estado_verificacion_oc"])
}
LOTE=300
SUBIDOS=files.upload()
assert len(SUBIDOS)==1,"Sube un único ZIP preparado para MER v2"
NOMBRE=next(iter(SUBIDOS))
BYTES=SUBIDOS[NOMBRE];HUELLA=hashlib.sha256(BYTES).hexdigest()
assert zipfile.is_zipfile(io.BytesIO(BYTES))
with zipfile.ZipFile(io.BytesIO(BYTES)) as z:
 assert set(z.namelist())=={n+".csv" for n in TABLAS}|{"informe.json"},"Estructura del ZIP incompatible"
 MANIFIESTO=json.loads(z.read("informe.json"))
 assert MANIFIESTO.get("esquema")=="MER_V2" and MANIFIESTO.get("validacion_filas")=="OK"
 ANIO=int(MANIFIESTO["anio"]);MES=int(MANIFIESTO["mes"])
 assert 2020<=ANIO<=2100 and 1<=MES<=12
 PERIODO=f"{ANIO}-{MES:02d}"
 assert MANIFIESTO["periodo"]==PERIODO
 print("Paquete validado:",PERIODO,"SHA256:",HUELLA)
 ESPERADOS={n:int(MANIFIESTO[n]) for n in TABLAS}
 assert all(x>=0 for x in ESPERADOS.values())

auth.authenticate_user()
creds,_=default(scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
gc=gspread.authorize(creds)
drive=build("drive","v3",credentials=creds)
libro=gc.open_by_key(DESTINO)
for name,(_,cab) in TABLAS.items():
 assert libro.worksheet(name).row_values(1)==cab,"Cabeceras distintas en "+name

# Ninguna escritura antes de una autorización separada.
def origen(name):
 pk,cols=TABLAS[name]
 with zipfile.ZipFile(io.BytesIO(BYTES)) as z:
  with z.open(name+".csv") as f:
   reader=csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig",newline=""))
   assert reader.fieldnames==cols
   for r in reader:
    assert None not in r and None not in r.values(),"CSV de ancho incorrecto: "+name
    key=r[pk].strip()
    assert key,"PK vacía: "+name
    yield key,[r[c] for c in cols]
def destino_claves(name):
 ws=libro.worksheet(name)
 keys=[s.strip() for s in ws.col_values(1)[1:] if s.strip()]
 assert len(keys)==len(set(keys)),"PK repetida actualmente en hoja "+name
 return keys
ESTADO={}
for name in TABLAS:
 actual=set(destino_claves(name))
 vistos=set();nuevos=0;solapados=0
 for key,row in origen(name):
  if key in vistos:raise ValueError("Duplicado en paquete "+name+": "+key)
  vistos.add(key)
  if key in actual:solapados+=1
  else:nuevos+=1
 assert len(vistos)==ESPERADOS[name],f"Cantidad incorrecta en {name}"
 ESTADO[name]={"paquete":len(vistos),"existentes":len(actual),"ya_registrados":solapados,"nuevos":nuevos}
 print(name,ESTADO[name])
# Google Sheets tiene un límite por archivo: comprobar capacidad antes de reservar filas.
MAX_CELDAS=10_000_000
def proyectar_celdas():
 actual=0;futuro=0
 for name,(_,cab) in TABLAS.items():
  ws=libro.worksheet(name)
  actual+=ws.row_count*ws.col_count
  filas=max(ws.row_count,ESTADO[name]["existentes"]+ESTADO[name]["nuevos"]+1)
  futuro+=filas*len(cab)
 return actual,futuro
CELDAS_ACTUALES,CELDAS_PROYECTADAS=proyectar_celdas()
print("Capacidad Sheets actual:",CELDAS_ACTUALES,"celdas; proyección de carga:",CELDAS_PROYECTADAS,"de",MAX_CELDAS)
CAPACIDAD_SUFICIENTE=CELDAS_PROYECTADAS<=MAX_CELDAS
if not CAPACIDAD_SUFICIENTE:
 print("BLOQUEO POR CAPACIDAD: se requiere particionar por períodos o migrar a una base de mayor capacidad; sin escrituras.")
print("SIMULACIÓN OK, sin escrituras. Período:",PERIODO)
print("ATENCIÓN: las PK coincidentes se conservan, sin sobrescribirlas; se documentan como solapamientos.")

# La siguiente fase se activa únicamente desde una celda separada en Colab.
def ejecutar(confirmacion):
 frase=f"AUTORIZO CARGA MER V2 {PERIODO} EN BASE NUEVA"
 assert confirmacion==frase,"Autorización incorrecta; no se escribe"
 assert CAPACIDAD_SUFICIENTE,"Capacidad Sheets insuficiente. No se permite escribir."
 assert libro.id==DESTINO
 respaldo=drive.files().copy(fileId=DESTINO,
   body={"name":"Respaldo MER v2 antes de "+PERIODO+" "+datetime.datetime.now().isoformat()},
   fields="id,webViewLink").execute()
 print("RESPALDO:",respaldo.get("webViewLink",respaldo["id"]))
 final={}
 for name,(pk,cols) in TABLAS.items():
  ws=libro.worksheet(name)
  assert ws.row_values(1)==cols
  keys=destino_claves(name)
  existentes=set(keys)
  # Reintentar no vuelve a insertar registros ya confirmados.
  pendientes=[]
  vistos=set()
  for key,row in origen(name):
   assert key not in vistos
   vistos.add(key)
   if key not in existentes:pendientes.append((key,row))
  assert len(vistos)==ESPERADOS[name]
  print(name,"pendientes",len(pendientes))
  posicion=len(keys)+2
  if pendientes:
   requerido=posicion+len(pendientes)-1
   if ws.row_count<requerido or ws.col_count!=len(cols):
    ws.resize(rows=max(requerido,ws.row_count),cols=len(cols))
  escritos=0
  fincol=gspread.utils.rowcol_to_a1(1,len(cols)).rstrip("1")
  for i in range(0,len(pendientes),LOTE):
   bloque=pendientes[i:i+LOTE]
   inicio=posicion+i;fin=inicio+len(bloque)-1
   rango=f"A{inicio}:{fincol}{fin}"
   valores=[r for k,r in bloque]
   for intento in range(5):
    try:
     # Leer PK antes de escribir evita repetir lotes confirmados si una petición falló después de escribir.
     pk_actual=ws.get(f"A{inicio}:A{fin}")
     pk_actual=[r[0] if r else "" for r in pk_actual]
     if pk_actual!=[k for k,r in bloque]:
      assert all(not x for x in pk_actual),"Hay otro escritor o un lote parcial: detener para reanudar de forma segura"
      ws.update(range_name=rango,values=valores,value_input_option="RAW")
     ver=ws.get(rango,value_render_option="FORMATTED_VALUE")
     normal=[(list(r)+[""]*len(cols))[:len(cols)] for r in ver]
     assert normal==valores,"El lote escrito difiere de la fuente"
     break
    except Exception as e:
     if intento==4:raise
     time.sleep(min(40,2**intento*3))
   escritos+=len(bloque)
   if escritos%6000<LOTE or i+len(bloque)==len(pendientes):
    print(name,"insertados/verificados",escritos,"de",len(pendientes))
  finalkeys=destino_claves(name)
  assert len(finalkeys)==len(keys)+len(pendientes),f"Conteo final incorrecto {name}"
  assert set(k for k,r in pendientes).issubset(set(finalkeys))
  final[name]={"antes":len(keys),"insertados":len(pendientes),"despues":len(finalkeys),"solapados_sin_cambios":len(vistos)-len(pendientes)}
 print("CARGA MER V2 FINALIZADA",PERIODO,json.dumps(final,ensure_ascii=False))
 print("Respaldo ID:",respaldo["id"],"Huella:",HUELLA)
 return final
