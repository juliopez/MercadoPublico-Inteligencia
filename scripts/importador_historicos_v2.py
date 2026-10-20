#!/usr/bin/env python3
"""Importador histórico MER v2: preparación secuencial, solo lectura de ZIP.
No escribe Google Sheets. No consulta API. Python estándar, SQLite y CSV.
Uso: python importador_historicos_v2.py --licitaciones 2026-9.zip --cot COT_2026-09.zip --oc "2026-9 (OC).zip" --out ./preparado_2026_09
"""
import argparse,csv,hashlib,io,json,sqlite3,zipfile,re
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
from pathlib import Path
from collections import Counter

SCHEMA={
"Procesos":["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre","monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas","motivo_seleccion","url_detalle","fecha_sincronizacion","categoria","subcategoria","modalidad"],
"Ofertas":["id_cotizacion","codigo","id_proveedor","proveedor","monto_ofertado_clp","fecha_oferta","fuente","seleccionado","rut_proveedor_cot"],
"Resultados":["codigo","id_cotizacion_ganadora","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado","monto_oferta_seleccionada_clp","estado_verificacion_oc"],
"OrdenesCompra":["codigo_oc","codigo_proceso","id_proveedor","fecha_creacion","fecha_aceptacion","estado","proveedor","monto_total_oc_clp","tipo_oc","cantidad_lineas","total_lineas_neto","rut_sucursal_oc","codigo_proveedor_oc"],
"Proveedores":["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"],
"VinculosCOT_OC":["id_vinculo","codigo_cot","codigo_oc","origen_vinculo","estado_oc_historico","fecha_aceptacion_oc","relacion_confiable"]
}
def val(r,key):return str(r.get(key) or "").strip()
def money(x):
 s=str(x or "").replace("$","").strip().replace(" ","")
 if not s:return ""
 if "," in s and "." not in s:s=s.replace(",",".")
 try:
  d=Decimal(s)
  return str(d.quantize(Decimal("1"),rounding=ROUND_HALF_UP)) if d.is_finite() else ""
 except InvalidOperation:return ""
def rut(x):return re.sub(r"[^0-9K]","",str(x or "").upper())
def h(*parts):return hashlib.sha256("|".join(map(str,parts)).encode()).hexdigest()
def proveedor(rut_raw,nombre,origen):
 rr=rut(rut_raw)
 if rr:return ["rut:"+rr,rr,nombre,"",origen,"RUT_SIN_CONTRASTE"]
 if nombre:return ["sinrut:"+h(origen,nombre.upper())[:24],"",nombre,"",origen,"SIN_RUT"]
 return None
def stream(path):
 with zipfile.ZipFile(path) as z:
  members=[m for m in z.infolist() if m.filename.lower().endswith(".csv") and not m.is_dir()]
  if not members:raise ValueError("ZIP sin CSV: "+str(path))
  for item in members:
   with z.open(item) as raw:
    # Latin-1 accepts all source bytes, and correctly maps ASCII delimiters.
    reader=csv.DictReader(io.TextIOWrapper(raw,encoding="latin-1",newline=""),delimiter=";")
    if not reader.fieldnames or len(reader.fieldnames)<3:raise ValueError("Cabecera incompatible: "+item.filename)
    for row in reader:yield item.filename,row
def init(db):
 for table,cols in SCHEMA.items():
  db.execute('CREATE TABLE "'+table+'" (pk TEXT PRIMARY KEY, fila TEXT NOT NULL)')
 db.execute("CREATE TABLE selección (codigo TEXT, id_oferta TEXT, proveedor TEXT, monto TEXT)")
 db.execute("CREATE INDEX idx_sel ON selección(codigo)")
 db.commit()
def insert(db,table,key,data,replace=False):
 sql='INSERT OR REPLACE' if replace else 'INSERT OR IGNORE'
 db.execute(sql+' INTO "'+table+'" (pk,fila) VALUES (?,?)',(key,json.dumps(data,ensure_ascii=False)))
def addprov(db,p):
 if p:insert(db,"Proveedores",p[0],p)
def process_cot(db,path,counts):
 for member,r in stream(path):
  counts["filas_cot"]+=1
  codigo=val(r,"CodigoCotizacion").upper()
  if not codigo:continue
  proc=[codigo,val(r,"NombreCotizacion"),val(r,"Estado"),"",
   val(r,"FechaPublicacionParaCotizar"),val(r,"FechaCierreParaCotizar"),
   money(r.get("MontoTotalDisponble")),val(r,"RazonSocialUnidaddeCompra"),
   val(r,"Region"),"","","","","","","Compra Ágil"]
  insert(db,"Procesos",codigo,proc)
  nom=val(r,"RazonSocialProveedor");rr=val(r,"RUTProveedor")
  amount=money(r.get("MontoTotal"))
  if nom and rr and amount:
   p=proveedor(rr,nom,"COT");addprov(db,p)
   selected=val(r,"ProveedorSeleccionado")
   ident=h(codigo,rut(rr),amount,val(r,"DetalleCotizacion").casefold(),selected.casefold())
   oferta=[ident,codigo,p[0],nom,amount,"","Histórico Compra Ágil",selected,rr]
   insert(db,"Ofertas",ident,oferta)
   if selected.casefold() in ("si","sí","true","1","seleccionado","yes"):
    db.execute("INSERT INTO selección VALUES (?,?,?,?)",(codigo,ident,nom,amount))
  oc=val(r,"CodigoOC").upper()
  if oc:
   vinc=h(codigo,oc)
   link=[vinc,codigo,oc,str(path.name)+"/"+member,
    val(r,"EstadoOC"),val(r,"FechaAceptacionOCProveedor"),"CODIGO_OC_OFICIAL"]
   insert(db,"VinculosCOT_OC",vinc,link)
  if counts["filas_cot"]%25000==0:db.commit()
 db.commit()
def process_oc(db,path,counts):
 for member,r in stream(path):
  counts["filas_oc"]+=1
  oc=val(r,"Codigo").upper()
  if not oc:continue
  nom=val(r,"NombreProveedor")
  p=proveedor(val(r,"RutSucursal"),nom,"OC");addprov(db,p)
  ident=val(r,"CodigoLicitacion").upper()
  ocdata=[oc,ident,p[0] if p else "",val(r,"FechaCreacion"),
   val(r,"FechaAceptacion"),val(r,"Estado"),nom,
   money(r.get("MontoTotalOC_PesosChilenos")),val(r,"Tipo"),
   "","",val(r,"RutSucursal"),val(r,"CodigoProveedor")]
  insert(db,"OrdenesCompra",oc,ocdata)
  if counts["filas_oc"]%25000==0:db.commit()
 db.commit()
def process_licitaciones(db,path,counts):
 for member,r in stream(path):
  counts["filas_licitaciones"]+=1
  code=(val(r,"CodigoExterno") or val(r,"Codigo")).upper()
  if not code:continue
  # El campo CodigoExterno se prefiere al identificador interno histórico.
  data=[code,val(r,"Nombre"),val(r,"Estado"),val(r,"Convocatoria"),
   val(r,"FechaPublicacion"),val(r,"FechaCierre"),
   money(r.get("MontoDisponible")),val(r,"NombreOrganismo"),val(r,"Region"),
   val(r,"TotalOfertasRecibidas"),val(r,"MotivoSeleccion"),val(r,"Link"),
   "","","","Licitación"]
  insert(db,"Procesos",code,data)
  if counts["filas_licitaciones"]%25000==0:db.commit()
 db.commit()
def finish(db,counts,out):
 # Una sola oferta seleccionada técnica por proceso; múltiples marcas iguales se deduplican.
 cursor=db.execute("SELECT codigo,COUNT(DISTINCT id_oferta),MIN(id_oferta),MIN(proveedor),MIN(monto) FROM selección GROUP BY codigo")
 for codigo,n,ident,prov,monto in cursor:
  if n!=1:
   counts["selecciones_ambiguas"]+=1
   continue
  data=[codigo,ident,prov,"","","Histórico Compra Ágil",
   "Pendiente: selección histórica, no adjudicación verificada",
   monto,"OC no verificada"]
  insert(db,"Resultados",codigo,data)
 db.commit()
 out.mkdir(parents=True,exist_ok=True)
 for table,cols in SCHEMA.items():
  path=out/(table+".csv")
  with path.open("w",encoding="utf-8-sig",newline="") as f:
   writer=csv.writer(f);writer.writerow(cols)
   for (raw,) in db.execute('SELECT fila FROM "'+table+'" ORDER BY pk'):
    writer.writerow(json.loads(raw))
  counts[table]=db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
 proc={k for (k,) in db.execute('SELECT pk FROM Procesos')}
 for t,col in (("Ofertas",1),("Resultados",0),("VinculosCOT_OC",1)):
  counts[t+"_sin_proceso"]=sum(json.loads(raw)[col] not in proc for (raw,) in db.execute('SELECT fila FROM "'+t+'"'))
 counts["regla_cobertura"]="Las OC fuera de corte no se consideran errores."
 counts["estado"]="PREPARADO_SOLO_LECTURA_SIN_CARGA_SHEETS"
 (out/"informe.json").write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(counts,ensure_ascii=False,indent=2))
def main():
 pa=argparse.ArgumentParser()
 for k in ("licitaciones","cot","oc"):pa.add_argument("--"+k,required=True,type=Path)
 pa.add_argument("--out",required=True,type=Path)
 a=pa.parse_args()
 for x in (a.licitaciones,a.cot,a.oc):
  if not x.is_file():pa.error("Archivo no encontrado: "+str(x))
 a.out.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(a.out/"preparado.sqlite")
 init(db);counts=Counter()
 process_licitaciones(db,a.licitaciones,counts)
 process_cot(db,a.cot,counts)
 process_oc(db,a.oc,counts)
 finish(db,counts,a.out);db.close()
if __name__=="__main__":main()
