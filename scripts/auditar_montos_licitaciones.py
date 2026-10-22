#!/usr/bin/env python3
"""Auditoría solo lectura del ZIP mensual de licitaciones; no escribe Sheets ni fragmentos."""
import csv,io,json,sys,urllib.request,zipfile,tempfile,pathlib,collections
url=sys.argv[1] if len(sys.argv)>1 else 'https://transparenciachc.blob.core.windows.net/lic-da/2026-10.zip'
with tempfile.TemporaryDirectory(prefix='mer_audit_montos_') as d:
 p=pathlib.Path(d)/'source.zip'
 req=urllib.request.Request(url,headers={'User-Agent':'MER-v2-Auditoria/1.0'})
 with urllib.request.urlopen(req,timeout=180) as stream,p.open('wb') as file:
  import shutil;shutil.copyfileobj(stream,file)
 report=[]
 with zipfile.ZipFile(p) as z:
  for obj in z.infolist():
   if not obj.filename.lower().endswith('.csv'):continue
   with z.open(obj) as stream:
    reader=csv.DictReader(io.TextIOWrapper(stream,encoding='latin-1',newline=''),delimiter=';')
    fields=reader.fieldnames or []
    candidates=[name for name in fields if any(x in name.casefold() for x in ('monto','moneda','estimad','presup','valor'))]
    counters=collections.Counter();examples={}
    n=0
    for row in reader:
     n+=1
     for field in candidates:
      val=(row.get(field) or '').strip()
      if val:
       counters[field]+=1
       if field not in examples:examples[field]=val[:32]
    report.append({'archivo':obj.filename,'registros':n,'cabeceras_monetarias':candidates,'campos_con_datos':dict(counters),'ejemplos_anonimos':examples,'columna_usada_por_importador':'MontoDisponible','existe': 'MontoDisponible' in fields})
 print(json.dumps(report,ensure_ascii=False,indent=2))
