"""Planificador puro de upsert API → MER (sin escribir Sheets).

Entrada: filas MER actuales (incluyen cabecera) + objeto transformado.
Salida: inserciones, actualizaciones y conflictos, siempre por nombre de columna.
"""
from adaptar_detalle_compra_agil_mer import OFERTAS, RESULTADOS

def planificar(tabla, existentes, nuevas):
    columnas=OFERTAS if tabla=="Ofertas" else RESULTADOS if tabla=="Resultados" else None
    if columnas is None: raise ValueError("Tabla no soportada")
    if not existentes or tuple(existentes[0])!=columnas: raise ValueError("Cabecera MER incompatible")
    clave=("codigo","id_cotizacion") if tabla=="Ofertas" else ("codigo","id_cotizacion_ganadora")
    def k(d):return tuple(str(d.get(c,"")).strip() for c in clave)
    original={}
    for i,r in enumerate(existentes[1:],2):
        d=dict(zip(columnas,list(r)+[""]*(len(columnas)-len(r))))
        key=k(d)
        if not all(key) or key in original: raise ValueError("Clave MER vacía o duplicada")
        original[key]=(i,d)
    seen=set(); plan={"insertar":[],"actualizar":[],"sin_cambios":0,"conflictos":[]}
    for item in nuevas:
        d={c:str(item.get(c,"") or "") for c in columnas}
        key=k(d)
        if not all(key) or key in seen:raise ValueError("Clave API vacía o duplicada")
        seen.add(key)
        if key not in original:
            plan["insertar"].append(d)
            continue
        num,old=original[key]
        merged=dict(old)
        # El enriquecimiento API nunca borra ni cambia datos verificados o establecidos.
        for c in columnas:
            val=d[c]
            if not val:continue
            if not old[c]:merged[c]=val
            elif val!=old[c] and c not in ("fuente",):
                plan["conflictos"].append({"clave":key,"columna":c})
        if merged!=old:plan["actualizar"].append({"fila":num,"valores":merged})
        else:plan["sin_cambios"]+=1
    return plan
