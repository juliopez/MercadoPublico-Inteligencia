"""Resolver id_proveedor desde Proveedores existente, sin crear identidades ni consultar API."""
import re

def rut_canonico(raw):
    return re.sub(r"[^0-9K]","",str(raw or "").upper())

def resolver_ofertas(ofertas,filas_proveedores):
    header=("id_proveedor","rut_canonico","razon_social_canonica","nombre_fantasia","fuente_principal","estado_identidad")
    if not filas_proveedores or tuple(filas_proveedores[0])!=header:
        raise ValueError("Cabecera Proveedores incompatible")
    ids={}
    for raw in filas_proveedores[1:]:
        record=dict(zip(header,list(raw)+[""]*len(header)))
        rr=rut_canonico(record["rut_canonico"])
        if not rr: continue
        pid=record["id_proveedor"]
        if rr in ids and ids[rr]!=pid: raise ValueError("Identidad canónica ambigua")
        if not pid: raise ValueError("Proveedor sin identificador")
        ids[rr]=pid
    result=[];pending=0
    for offer in ofertas:
        row=dict(offer)
        rut=rut_canonico(row.get("rut_proveedor_cot",""))
        pid=ids.get(rut,"") if rut else ""
        if row.get("id_proveedor") and pid and row["id_proveedor"]!=pid:
            raise ValueError("Identidad API incompatible con MER")
        row["id_proveedor"]=row.get("id_proveedor") or pid
        if not row["id_proveedor"]:pending+=1
        result.append(row)
    return {"ofertas":result,"sin_identidad":pending,"identidad_resuelta":len(result)-pending}
