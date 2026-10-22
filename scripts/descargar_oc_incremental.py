#!/usr/bin/env python3
"""Descarga OC del mes, GET condicional y validación ZIP; no descarga históricos."""
import sys,urllib.request,urllib.error,zipfile,os,tempfile,email.utils,datetime
from pathlib import Path
mes,dest=sys.argv[1],Path(sys.argv[2]);dest.parent.mkdir(parents=True,exist_ok=True)
url=f'https://transparenciachc.blob.core.windows.net/oc-da/{mes}.zip'
headers={'User-Agent':'MER-Ubuntu-ETL/2.0'}
if dest.exists(): headers['If-Modified-Since']=email.utils.formatdate(dest.stat().st_mtime,usegmt=True)
req=urllib.request.Request(url,headers=headers)
try:
 with urllib.request.urlopen(req,timeout=180) as response:
  fd,name=tempfile.mkstemp(prefix='.oc_',suffix='.zip',dir=dest.parent)
  try:
   with os.fdopen(fd,'wb') as out:
    while True:
     buf=response.read(1024*1024)
     if not buf:break
     out.write(buf)
   with zipfile.ZipFile(name) as z:
    assert any(n.lower().endswith('.csv') for n in z.namelist())
    assert z.testzip() is None
   os.replace(name,dest)
  finally:
   if os.path.exists(name):os.unlink(name)
except urllib.error.HTTPError as exc:
 if exc.code!=304:raise
 if not dest.exists():raise RuntimeError('Servidor 304 sin cache local')
with zipfile.ZipFile(dest) as z:
 assert any(n.lower().endswith('.csv') for n in z.namelist())
 assert z.testzip() is None
print('OC verificada:',dest,'bytes',dest.stat().st_size)
