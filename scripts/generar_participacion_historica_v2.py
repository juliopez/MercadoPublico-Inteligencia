#!/usr/bin/env python3
"""Indicadores de participación por actor y mes, enlazando códigos reales."""
import argparse, collections, hashlib, json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"frontend-v2"
def norm(v):
 s=unicodedata.normalize('NFD',str(v or '').casefold())
 return re.sub(r'\s+',' ',''.join(c for c in s if unicodedata.category(c)!='Mn')).strip()
def records(root,part_paths):
 for rel in part_paths:
  for row in json.loads((root/rel).read_text(encoding='utf8')):
   yield row
def build(period,root=ROOT):
 if not re.fullmatch(r'20\d{2}-(0[1-9]|1[0-2])',period):raise ValueError('Período inválido')
 cat=json.loads((root/'data/catalogo-publico.json').read_text(encoding='utf8'))
 info=next(x for x in cat['periodos'] if x['periodo']==period)
 org_by_code={}
 org_counts=collections.Counter()
 for record in records(root,info['partes']['procesos']):
  code=str(record.get('codigo') or '').strip()
  name=norm(record.get('organismo_comprador'))
  if code and name:org_by_code[code]=name;org_counts[name]+=1
 offer_counts=collections.Counter();provider_codes=collections.defaultdict(set)
 org_received=collections.Counter();org_offer_codes=collections.defaultdict(set)
 unmatched=0
 for offer in records(root,info['partes']['ofertas']):
  code=str(offer.get('codigo') or '').strip()
  provider=norm(offer.get('proveedor'))
  if provider:
   offer_counts[provider]+=1
   if code:provider_codes[provider].add(code)
  org=org_by_code.get(code)
  if org:
   org_received[org]+=1
   org_offer_codes[org].add(code)
  else:unmatched+=1
 out=root/'data/participacion'/period
 for entity,keys in [('proveedor',offer_counts.keys()),('organismo',org_counts.keys())]:
  shards=collections.defaultdict(dict)
  for name in keys:
   if entity=='proveedor':
    value={'ofertas':offer_counts[name],'procesos_distintos':len(provider_codes[name])}
   else:
    value={'procesos_publicados':org_counts[name],'ofertas_recibidas_vinculadas':org_received[name],'procesos_con_ofertas_vinculadas':len(org_offer_codes[name])}
   shard=hashlib.sha256(name.encode('utf8')).hexdigest()[:2]
   shards[shard][name]=value
  # Sugerencias de nombres reales por prefijo normalizado; archivos acotados.
  names=collections.defaultdict(list)
  for actor in keys:
   if len(actor)<2:continue
   prefix=hashlib.sha256(actor[:2].encode('utf8')).hexdigest()[:2]
   names[prefix].append(actor)
  suggestions=out/'sugerencias'/entity;suggestions.mkdir(parents=True,exist_ok=True)
  for group,values in names.items():
   (suggestions/(group+'.json')).write_text(json.dumps(sorted(values)[:500],ensure_ascii=False,separators=(',',':')),encoding='utf8')
  dest=out/entity;dest.mkdir(parents=True,exist_ok=True)
  for shard,items in shards.items():
   (dest/(shard+'.json')).write_text(json.dumps(items,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 meta={'version':1,'periodo':period,'procesos_publicados':sum(org_counts.values()),'ofertas':sum(offer_counts.values()),'ofertas_sin_proceso_en_el_mismo_mes':unmatched,'metodo':'Vinculación exacta por código de proceso dentro de cada período; no identifica procesos de otros meses'}
 (out/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
 print('PARTICIPACION_OK',period,meta)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--periodo',required=True);args=p.parse_args();build(args.periodo)
