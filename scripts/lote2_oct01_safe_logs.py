#!/usr/bin/env python3
"""Lote pequeño OCT 01: una página de listado, máximo dos detalles nuevos; sin escritura."""
import json,os,urllib.parse,urllib.request,time,hashlib
ticket=os.environ["CHILECOMPRA_TICKET"]
known={"3853-565-COT26","5668-58-COT26","607603-61-COT26"}
headers={"ticket":ticket,"Accept":"application/json","User-Agent":"MER-oct-lote2-controlado"}
def get(url):
 req=urllib.request.Request(url,headers=headers)
 with urllib.request.urlopen(req,timeout=40) as response:return json.load(response)
q={"publicado_desde":"2026-10-01T00:00:00","publicado_hasta":"2026-10-01T23:59:59","tamano_pagina":"10","numero_pagina":"1","ordenar_por":"FechaPublicacion"}
data=get("https://api2.mercadopublico.cl/v2/compra-agil?"+urllib.parse.urlencode(q))
p=data.get("payload") or {}
items=p.get("resultados") or p.get("items") or p.get("datos") or []
print("LISTADO_KEYS",json.dumps(list(p) if isinstance(p,dict) else [],ensure_ascii=False))
print("LISTADO_TIPO",type(items).__name__,len(items))
codes=[]
for item in items:
 if not isinstance(item,dict):continue
 code=item.get("codigo") or item.get("codigo_compra_agil") or item.get("codigo_externo")
 if code and code not in known and code not in codes:codes.append(code)
print("CANDIDATOS",json.dumps(codes[:5]))
for code in codes[:2]:
 time.sleep(2)
 detail=get("https://api2.mercadopublico.cl/v2/compra-agil/"+urllib.parse.quote(code))
 payload=detail.get("payload") or {}
 quotes=payload.get("proveedores_cotizando") or []
 fechas=payload.get("fechas") or {}
 sanitized=[{"id":str(x.get("id_cotizacion") or ""),"proveedor":str(x.get("razon_social") or ""),"fecha":str(x.get("fecha_creacion") or ""),"seleccionado":bool(x.get("proveedor_seleccionado"))} for x in quotes]
 print("DETALLE",json.dumps({"codigo":code,"codigo_respuesta":payload.get("codigo"),"fechas":fechas,"cantidad":len(quotes),"ofertas":sanitized},ensure_ascii=False,default=str))
