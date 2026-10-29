"""Normalización conservadora de campos de Compra Ágil: nunca serializar objetos en celdas."""
def scalar(value):
    if value is None or isinstance(value,(dict,list,tuple)):return ""
    return str(value).strip()
def etiqueta(value):
    if not isinstance(value,dict):return scalar(value)
    for key in ("descripcion","nombre","glosa","codigo","id_estado"):
        val=scalar(value.get(key))
        if val:return val
    return ""
def organismo(payload):
    for key in ("organismo_comprador","comprador","organismo","unidad_compradora"):
        obj=payload.get(key)
        if isinstance(obj,dict):
            for field in ("razon_social","nombre","nombre_organismo","nombre_unidad","descripcion"):
                val=scalar(obj.get(field))
                if val:return val
        elif scalar(obj):return scalar(obj)
    return ""
def proceso(payload,code,fecha,now):
    fechas=payload.get("fechas") or {}
    if not isinstance(fechas,dict):fechas={}
    return {"codigo":code,"nombre":scalar(payload.get("nombre") or payload.get("titulo")),
     "estado":etiqueta(payload.get("estado")),"organismo_comprador":organismo(payload),
     "fecha_publicacion":fecha[:10],"fecha_cierre":scalar(fechas.get("fecha_cierre"))[:10],
     "url_detalle":"https://buscador.mercadopublico.cl/ficha?code="+code,
     "fecha_sincronizacion":now.isoformat(),"categoria":"Compra Ágil","modalidad":"Compra Ágil"}
def completar_proceso(existente,nuevo):
    """Completar solo vacíos y reparar estado serializado; respetar las demás columnas."""
    merged=dict(existente)
    for field in ("nombre","organismo_comprador","fecha_cierre","fecha_publicacion","categoria","modalidad"):
        if not merged.get(field) and nuevo.get(field):merged[field]=nuevo[field]
    old=merged.get("estado","")
    if (not old or old.lstrip().startswith(("{","["))) and nuevo.get("estado"):
        merged["estado"]=nuevo["estado"]
    return merged
