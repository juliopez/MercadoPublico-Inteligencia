#!/usr/bin/env python3
"""Escritor API-MER para un libro de PRUEBA explícito, nunca para el catálogo operativo.

No consulta ChileCompra. Aplica una transformación cacheada a Ofertas y Resultados,
con backup local, lock exclusivo y verificación de lectura posterior.
"""
import argparse,fcntl,hashlib,json,os,pathlib,tempfile
from planificar_upsert_api_mer import planificar
from resolver_proveedores_ofertas_mer import resolver_ofertas
from adaptar_detalle_compra_agil_mer import OFERTAS,RESULTADOS

TABS=("Ofertas","Resultados","Proveedores")
def leer(ws):return ws.get_all_values()
def operar(book,transformacion,*,lockpath,respaldo):
    if not isinstance(transformacion,dict) or not isinstance(transformacion.get("ofertas"),list) or not isinstance(transformacion.get("resultados"),list):
        raise ValueError("Transformación incompatible")
    path=pathlib.Path(lockpath)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a+") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        sheets={n:book.worksheet(n) for n in TABS}
        snap={n:leer(sheets[n]) for n in TABS}
        datos=resolver_ofertas(transformacion["ofertas"],snap["Proveedores"])["ofertas"]
        plans={n:planificar(n,snap[n],items) for n,items in
               (("Ofertas",datos),("Resultados",transformacion["resultados"]))}
        if any(p["conflictos"] for p in plans.values()):
            raise ValueError("Conflictos detectados: escritura cancelada")
        dst=pathlib.Path(respaldo)
        if dst.exists() or dst.is_symlink():raise FileExistsError("Respaldo ya existe")
        dst.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(dst,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(snap,f,ensure_ascii=False)
            f.flush();os.fsync(f.fileno())
        before_sha=hashlib.sha256(dst.read_bytes()).hexdigest()
        try:
            return _escribir_y_verificar(sheets,plans,datos,transformacion,before_sha)
        except Exception as exc:
            raise RuntimeError("ESCRITURA_PARCIAL_POSIBLE: conservar respaldo y revisar libro de prueba") from exc

def _escribir_y_verificar(sheets,plans,datos,transformacion,before_sha):
    counts={}
    for name,columns in (("Ofertas",OFERTAS),("Resultados",RESULTADOS)):
        plan=plans[name];ws=sheets[name]
        changes=sorted(plan["actualizar"],key=lambda x:x["fila"])
        for update in changes:
            n=update["fila"]
            ws.update(range_name=f"A{n}:{chr(64+len(columns))}{n}",
                      values=[[update["valores"][k] for k in columns]],value_input_option="RAW")
        rows=[[row[k] for k in columns] for row in plan["insertar"]]
        if rows:ws.append_rows(rows,value_input_option="RAW")
        actual=leer(ws)
        # Replanificar: no debe quedar ninguna escritura pendiente ni conflictos.
        new=datos if name=="Ofertas" else transformacion["resultados"]
        check=planificar(name,actual,new)
        if check["insertar"] or check["actualizar"] or check["conflictos"]:
            raise RuntimeError("Verificación posterior fallida para "+name)
        counts[name]={"insertados":len(rows),"actualizados":len(changes),"total_filas":len(actual)-1}
    return {"estado":"APLICADO_VERIFICADO","respaldo_sha256":before_sha,"tablas":counts}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--transformacion",required=True)
    ap.add_argument("--spreadsheet-prueba-id",required=True)
    ap.add_argument("--operativo-id",required=True)
    ap.add_argument("--respaldo",required=True)
    ap.add_argument("--lock",required=True)
    ap.add_argument("--aplicar-en-prueba",action="store_true")
    a=ap.parse_args()
    if not a.aplicar_en_prueba:raise SystemExit("MODO_SIMULACION: sin escrituras; requiere --aplicar-en-prueba")
    if os.environ.get("MER_API_TEST_SHEET_ID","")!=a.spreadsheet_prueba_id:\n        raise SystemExit("BLOQUEADO: requiere libro autorizado por MER_API_TEST_SHEET_ID")\n    if a.spreadsheet_prueba_id==a.operativo_id:raise SystemExit("BLOQUEADO: destino es MER operativo")
    # Defensa adicional: todos los ids de MER en catálogo prohibidos.
    root=pathlib.Path(__file__).resolve().parents[1]
    cat=json.loads((root/"config/catalogo_sheets.json").read_text())
    ids={x["id"] for x in cat["periodos"].values()}
    if a.spreadsheet_prueba_id in ids:raise SystemExit("BLOQUEADO: destino pertenece al catálogo MER")
    import gspread
    from google.oauth2.service_account import Credentials
    key=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS","")
    if not key or not pathlib.Path(key).is_file():raise SystemExit("Falta credencial local")
    credentials=Credentials.from_service_account_file(key,scopes=["https://www.googleapis.com/auth/spreadsheets"])
    book=gspread.authorize(credentials).open_by_key(a.spreadsheet_prueba_id)
    trans=json.loads(pathlib.Path(a.transformacion).read_text())
    if not isinstance(trans,dict) or not isinstance(trans.get("ofertas"),list) or not isinstance(trans.get("resultados"),list):
        raise SystemExit("Transformación inválida")
    print(json.dumps(operar(book,trans,lockpath=a.lock,respaldo=a.respaldo),ensure_ascii=False))
if __name__=="__main__":main()
