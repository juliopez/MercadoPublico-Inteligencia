#!/usr/bin/env python3
"""Ensayo integral API→MER con datos sintéticos, sin llamadas a ChileCompra ni publicación pública.

Modo offline: libro simulado en memoria. Modo conectado: solo copia explícita
fuera del catálogo; utiliza credencial de servicio inyectada por workflow.
"""
import argparse, json, os, pathlib, tempfile, hashlib
from escribir_api_mer_libro_prueba import operar
from exportar_ofertas_resultados_preview import exportar_tablas
from adaptar_detalle_compra_agil_mer import OFERTAS, RESULTADOS
from resolver_proveedores_ofertas_mer import resolver_ofertas

RUT_TEST=""
COD="999999-999-COT26"
COT="TEST-MER-API-20261028"
PROVEEDOR=["id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad"]
class MemorySheet:
    def __init__(self,rows):self.rows=[list(x) for x in rows]
    def get_all_values(self):return [list(x) for x in self.rows]
    def append_rows(self,rows,*,value_input_option):self.rows.extend([list(x) for x in rows])
    def update(self,*,range_name,values,value_input_option):
        self.rows[int(range_name.split(':')[0][1:])-1]=list(values[0])
class MemoryBook:
    def __init__(self):
        self.tabs={"Ofertas":MemorySheet([list(OFERTAS)]),
                   "Resultados":MemorySheet([list(RESULTADOS)]),
                   "Proveedores":MemorySheet([PROVEEDOR])}
    def worksheet(self,n):return self.tabs[n]
def test_data():
    return {"codigo":COD,
      "ofertas":[dict(id_cotizacion=COT,codigo=COD,id_proveedor="",proveedor="PROVEEDOR SINTETICO - ENSAYO",
                      monto_ofertado_clp="",fecha_oferta="2026-10-28",fuente="SIMULACION",
                      seleccionado="1",rut_proveedor_cot="")],
      "resultados":[dict(codigo=COD,id_cotizacion_ganadora=COT,adjudicatario="",
          monto_adjudicado_clp="",fecha_resultado="",motivo_seleccion="",fuente="SIMULACION",
          validado="NO: ENSAYO",monto_oferta_seleccionada_clp="",estado_verificacion_oc="NO VERIFICADA")]}
def validar_destino(test_id,catfile):
    cat=json.loads(pathlib.Path(catfile).read_text())
    all_ids={v["id"] for v in cat["periodos"].values()}
    if test_id in all_ids:raise ValueError("Destino catalogado como MER: BLOQUEADO")
    if not test_id or os.getenv("MER_API_TEST_SHEET_ID","")!=test_id:
        raise ValueError("ID prueba no coincide con allowlist")
def run(book,out):
    data=test_data()
    with tempfile.TemporaryDirectory() as tmp:
        lock=pathlib.Path(tmp)/"mer.lock"
        first=operar(book,data,lockpath=lock,respaldo=pathlib.Path(tmp)/"backup1.json")
        second=operar(book,data,lockpath=lock,respaldo=pathlib.Path(tmp)/"backup2.json")
        if first["tablas"]["Ofertas"]["insertados"] not in (0,1) or first["tablas"]["Resultados"]["insertados"] not in (0,1):
            raise AssertionError("Inserción inesperada")
        if any(second["tablas"][s]["insertados"] or second["tablas"][s]["actualizados"] for s in ("Ofertas","Resultados")):
            raise AssertionError("Idempotencia fallida")
        tabs={name:book.worksheet(name).get_all_values() for name in ("Ofertas","Resultados")}
        for name,index,field in (("Ofertas",0,COT),("Resultados",1,COT)):
            if sum(1 for row in tabs[name][1:] if len(row)>index and row[index]==field)!=1:
                raise AssertionError("Registro sintético no único: "+name)
        preview=exportar_tablas(tabs,"2026-10",out)
        for ent,paths in preview["partes"].items():
            n=0
            for rel in paths:
                p=pathlib.Path(out)/rel.removeprefix("data/")
                records=json.loads(p.read_text())
                n+=len(records)
                if any("rut_proveedor_cot" in r or "id_proveedor" in r or "fuente" in r for r in records):
                    raise AssertionError("Datos internos expuestos")
            if n!=preview["conteos"][ent]:raise AssertionError("Conteos públicos incompatibles")
        return {"estado":"ENSAYO_INTEGRAL_OK","primera":first["tablas"],"segunda":second["tablas"],
                "preview":preview["conteos"],"publicado_pages":False,"consultas_chilecompra":0}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--modo",choices=["offline","conectado"],default="offline")
    p.add_argument("--spreadsheet-prueba-id")
    p.add_argument("--salida",required=True)
    a=p.parse_args()
    out=pathlib.Path(a.salida).resolve()
    root=pathlib.Path(__file__).resolve().parents[1]
    if out==root or root in out.parents:raise SystemExit("Destino debe estar fuera del repositorio")
    if out.exists() and any(out.iterdir()):raise SystemExit("Directorio de salida no vacío")
    if a.modo=="offline":book=MemoryBook()
    else:
        validar_destino(a.spreadsheet_prueba_id,root/"config/catalogo_sheets.json")
        import gspread
        from google.oauth2.service_account import Credentials
        key=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS","")
        if not key or not pathlib.Path(key).is_file():raise SystemExit("Credencial de Sheets no configurada")
        cred=Credentials.from_service_account_file(key,scopes=["https://www.googleapis.com/auth/spreadsheets"])
        book=gspread.authorize(cred).open_by_key(a.spreadsheet_prueba_id)
    print(json.dumps(run(book,out),ensure_ascii=False))
if __name__=="__main__":main()
