"""Carga controlada MER v2 desde ZIP preparado. SOLO ejecuta en Colab con autorización explícita."""
import csv,io,zipfile,json,collections,datetime,time,hashlib
from google.colab import files,auth
from google.auth import default
from googleapiclient.discovery import build
import gspread

DESTINO="1lnMVUZ_pn_HkwEvI90yYz5GOMSYzuX-FbcbMR71-oDA"
PRODUCCION="1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4"
CLON_ANTERIOR="1loeK_IM3RXHaR7CqpjUbz-TsNgOKNrV1ejq8aRC6JyE"
TABLAS={
"Procesos":("codigo",["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre","monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas","motivo_seleccion","url_detalle","fecha_sincronizacion","categoria","subcategoria","modalidad"]),
"Proveedores":("id_proveedor",["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"]),
"Ofertas":("id_cotizacion",["id_cotizacion","codigo","id_proveedor","proveedor","monto_ofertado_clp","fecha_oferta","fuente","seleccionado","rut_proveedor_cot"]),
"OrdenesCompra":("codigo_oc",["codigo_oc","codigo_proceso","id_proveedor","fecha_creacion","fecha_aceptacion","estado","proveedor","monto_total_oc_clp","tipo_oc","cantidad_lineas","total_lineas_neto","rut_sucursal_oc","codigo_proveedor_oc"]),
"VinculosCOT_OC":("id_vinculo",["id_vinculo","codigo_cot","codigo_oc","origen_vinculo","estado_oc_historico","fecha_aceptacion_oc","relacion_confiable"]),
"Resultados":("codigo",["codigo","id_cotizacion_ganadora","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado","monto_oferta_seleccionada_clp","estado_verificacion_oc"])
}
ESPERADOS={"Procesos":79376,"Proveedores":30280,"Ofertas":398018,"OrdenesCompra":147966,"VinculosCOT_OC":50041,"Resultados":48637}
FRACCION_LOTE=600
print("Sube exclusivamente preparado_mercado_publico_mer_v2.zip, versión corregida.")
uploads=files.upload()
assert len(uploads)==1,"Debe recibirse exactamente un ZIP."
nombre=next(iter(uploads))
raw=uploads[nombre]
assert zipfile.is_zipfile(io.BytesIO(raw))
zip_digest=hashlib.sha256(raw).hexdigest()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert set(z.namelist())=={t+".csv" for t in TABLAS}|{"informe.json"},"Contenido ZIP inesperado"
 informe=json.loads(z.read("informe.json"))
 assert informe.get("validacion_filas")=="OK"
 for name,total in ESPERADOS.items():assert informe.get(name)==total,f"Total de {name} inesperado."
 print("Paquete:",nombre,"SHA256:",zip_digest)
 print("Cantidades declaradas:",ESPERADOS)

auth.authenticate_user()
credentials,_=default(scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
gc=gspread.authorize(credentials)
drive=build("drive","v3",credentials=credentials)
book=gc.open_by_key(DESTINO)
assert DESTINO not in (PRODUCCION,CLON_ANTERIOR)
for name,(_,header) in TABLAS.items():
 assert book.worksheet(name).row_values(1)==header,f"Cabecera incompatible en {name}"
print("Estructura de destino validada.")

# Una tabla a la vez en memoria: lectura del ZIP preparado, no ZIP históricos.
def preparar(nombre):
 pk,enc=TABLAS[nombre]
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  with z.open(nombre+".csv") as f:
   rd=csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig",newline=""))
   assert rd.fieldnames==enc
   rows=[];ids=set()
   for r in rd:
    assert None not in r and len(r)==len(enc),"Fila de longitud incorrecta: "+nombre
    clave=(r.get(pk) or "").strip()
    assert clave and clave not in ids,"PK vacía/repetida en "+nombre
    ids.add(clave);rows.append([r[k] for k in enc])
 assert len(rows)==ESPERADOS[nombre]
 return rows

# Releer únicamente la PK y comprobar que la carga previa es un prefijo estricto
# del CSV aprobado; no se permite insertar encima de contenidos ajenos o alterados.
def verificar_destino(ws,rows):
 existentes=ws.col_values(1)[1:]
 esperadas=[r[0] for r in rows]
 assert existentes==esperadas[:len(existentes)],f"Claves de {ws.title} no siguen prefijo aprobado"
 return len(existentes)

for nombre in TABLAS:
 ws=book.worksheet(nombre)
 # Lectura inicial corta y conteos del ZIP; todavía no se escriben datos.
 existentes=ws.col_values(1)[1:]
 assert len(existentes)<=ESPERADOS[nombre]
 print(f"{nombre}: destino actual {len(existentes)}; objetivo {ESPERADOS[nombre]}")
print("SIMULACIÓN REALIZADA: todavía no se escribió ninguna fila.")
print("Para escribir, ejecuta la última celda con la frase de autorización.")

# SEGUNDA ETAPA: escritura. La autorización queda siempre vacía por defecto.
AUTORIZACION=""  # escribir: AUTORIZO CARGA MER V2 SEPTIEMBRE EN BASE NUEVA
if AUTORIZACION!="AUTORIZO CARGA MER V2 SEPTIEMBRE EN BASE NUEVA":
 print("FIN DE SIMULACIÓN. Para cargar, fija AUTORIZACION en la celda de ejecución del notebook.")
else:
 assert book.id==DESTINO
 # Backup completo previo: no se permiten otras escrituras concurrentes.
 respaldo=drive.files().copy(fileId=DESTINO,body={"name":"Respaldo MER v2 antes de septiembre "+datetime.datetime.now().isoformat()},fields="id,webViewLink").execute()
 print("RESPALDO:",respaldo.get("webViewLink",respaldo["id"]))
 reporte_final={}
 for nombre,(clave,cab) in TABLAS.items():
  ws=book.worksheet(nombre)
  registros=preparar(nombre)
  pre=verificar_destino(ws,registros)
  total=len(registros)
  # Minimizar columnas reservadas para no alcanzar límite de 10M celdas.
  if ws.row_count<total+1 or ws.col_count!=len(cab):
   ws.resize(rows=max(total+1,ws.row_count),cols=len(cab))
  escritos=0
  for offset in range(pre,total,FRACCION_LOTE):
   bloque=registros[offset:offset+FRACCION_LOTE]
   inicio=offset+2;termino=inicio+len(bloque)-1
   fin_col=gspread.utils.rowcol_to_a1(1,len(cab)).rstrip("1")
   rango=f"A{inicio}:{fin_col}{termino}"
   # Tras un fallo/reintento ambiguo, comprobar el bloque antes de reescribir.
   for intento in range(6):
    try:
     # Sheets omite celdas vacías al final de cada fila en las respuestas.
     def normalizar_respuesta(valores):
      return [(list(fila)+[""]*len(cab))[:len(cab)] for fila in valores]
     actual=normalizar_respuesta(ws.get(rango,value_render_option="UNFORMATTED_VALUE"))
     if actual!=bloque:
      ws.update(range_name=rango,values=bloque,value_input_option="RAW")
     actual=normalizar_respuesta(ws.get(rango,value_render_option="UNFORMATTED_VALUE"))
     assert actual==bloque,f"No se pudo verificar rango {rango}"
     break
    except Exception as e:
     if intento==5:raise
     espera=min(60,2**intento*3)
     print("Reintento",nombre,rango,"en",espera,"seg:",str(e)[:100])
     time.sleep(espera)
   escritos+=len(bloque)
   if escritos%6000<FRACCION_LOTE or offset+len(bloque)==total:
    print(nombre,"verificados",offset+len(bloque),"/",total)
  # Verificación total de PK, incluye carga preexistente reanudada.
  actual_pk=ws.col_values(1)[1:]
  assert actual_pk==[fila[0] for fila in registros],f"Fallo verificación PK final {nombre}"
  reporte_final[nombre]={"antes":pre,"nuevos":escritos,"final":len(actual_pk)}
  del registros
 print("CARGA TERMINADA, resumen:",json.dumps(reporte_final,ensure_ascii=False))
 print("Respaldo:",respaldo["id"],"SHA256 paquete:",zip_digest)
