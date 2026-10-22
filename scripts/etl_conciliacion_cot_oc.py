#!/usr/bin/env python3
"""Conciliación incremental y conservadora COT--OC para MER v2.

Requiere el repositorio MercadoPublico-Inteligencia como cwd y su .venv.
SIMULACIÓN por defecto. Escritura real únicamente con --aplicar.
No altera Procesos, OC, ni filas originales; inserta en VinculosCOT_OC.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

CHILE = ZoneInfo('America/Santiago')
COT_RE = re.compile(r'(?<![A-Z0-9])\d{1,7}-\d{1,9}-COT\d{2,4}(?![A-Z0-9])', re.I)
OC_RE = re.compile(r'(?<![A-Z0-9])\d{1,7}-\d{1,9}-(?:SE|CM|AG|OC|CC|LP|LE|LQ|LR|TD|B2B)\d{2,4}(?![A-Z0-9])', re.I)
DESC_FIELDS = ['Descripcion/Obervaciones', 'Descripcion', 'Descripción', 'Observaciones', 'Obervaciones',
               'DescripcionOC', 'DescripcionOrdenCompra', 'Observacion']
SCHEMA = ['id_vinculo','codigo_cot','codigo_oc','origen_vinculo',
          'estado_oc_historico','fecha_aceptacion_oc','relacion_confiable']


def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def rows_zip(path):
    with zipfile.ZipFile(path) as z:
        bad=z.testzip()
        if bad: raise ValueError(f'ZIP corrupto {path}: {bad}')
        files=[n for n in z.namelist() if n.lower().endswith('.csv')]
        if not files: raise ValueError(f'ZIP sin CSV: {path}')
        for name in files:
            with z.open(name) as stream:
                # Contrato de históricos oficiales: separador ; y codificación latin-1.
                reader=csv.DictReader(io.TextIOWrapper(stream,encoding='latin-1',newline=''),delimiter=';')
                if not reader.fieldnames or len(reader.fieldnames)<3:
                    raise ValueError(f'Cabecera CSV incompatible: {name}')
                for row in reader: yield name, row


def clean(v):
    v=str(v or '').strip()
    return '' if v.upper() in {'NA','N/A','NULL','NAN','NONE'} else v


def key(cot,oc): return hashlib.sha256((cot+'|'+oc).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cot',type=Path,help='ZIP oficial COT del período (opcional)')
    p.add_argument('--oc',required=True,type=Path,help='ZIP oficial OC del período')
    p.add_argument('--periodo',required=True,help='AAAA-MM')
    p.add_argument('--aplicar',action='store_true',help='Permite insertar SOLO vínculos verificables')
    p.add_argument('--salida',type=Path,default=Path('salida_operativa'))
    args=p.parse_args()
    if not re.fullmatch(r'20\d\d-(0[1-9]|1[0-2])',args.periodo): p.error('Período inválido')
    if not args.oc.is_file() or (args.cot and not args.cot.is_file()): p.error('ZIP inexistente')
    args.salida.mkdir(parents=True,exist_ok=True)
    sources={kind:{'ruta':str(path.resolve()),'sha256':sha_file(path)} for kind,path in [('oc',args.oc),('cot',args.cot)] if path}
    target=args.salida/f'conciliacion_cot_oc_{args.periodo}.json'
    found={}; ambiguous=[]; stats=Counter()
    # Máxima certeza: vínculo oficial directamente codificado en COT.
    if args.cot:
        for member,r in rows_zip(args.cot):
            stats['cot_filas']+=1
            cot=clean(r.get('CodigoCotizacion')).upper()
            oc=clean(r.get('CodigoOC')).upper()
            if not cot or not oc: continue
            if not COT_RE.fullmatch(cot):
                stats['cot_codigos_no_estandar']+=1
                continue
            k=key(cot,oc)
            found[k]=[k,cot,oc,f'COT:{args.periodo}/{member}:CodigoOC',
                      clean(r.get('EstadoOC')),clean(r.get('FechaAceptacionOCProveedor')),
                      'CODIGO_OC_OFICIAL']
            stats['cot_pares']+=1
    # Fuente documental: campo de texto original OC; NO inferir por proveedor ni montos.
    for member,r in rows_zip(args.oc):
        stats['oc_filas']+=1
        oc=clean(r.get('Codigo')).upper()
        if not oc: continue
        texts=[(field,clean(r.get(field))) for field in DESC_FIELDS if clean(r.get(field))]
        matches=set()
        for field,value in texts:
            for m in COT_RE.findall(value): matches.add((m.upper(),field))
        codes={c for c,_ in matches}
        if len(codes)>1:
            ambiguous.append({'codigo_oc':oc,'motivo':'multiples COT citadas','cantidad':len(codes),
                              'archivo':member})
            continue
        if len(codes)==1:
            cot=next(iter(codes))
            field=next(f for c,f in matches if c==cot)
            k=key(cot,oc)
            if k not in found:
                found[k]=[k,cot,oc,f'OC:{args.periodo}/{member}:{field}',
                          clean(r.get('Estado')),clean(r.get('FechaAceptacion')),
                          'REFERENCIA_DOCUMENTAL_OC']
                stats['oc_pares_documentales']+=1
    report={'periodo':args.periodo,'ejecucion_chile':dt.datetime.now(CHILE).isoformat(),
            'fuentes':sources,'estadisticas':dict(stats),'pares_validos':len(found),
            'ambiguos':len(ambiguous),'modo':'APLICAR' if args.aplicar else 'SIMULACION',
            'estado':'PREPARADO_SIN_ESCRITURAS'}
    # La simulación genera una lista auditable en archivo local privado (no publicar en Pages).
    private=Path.home()/'.local/share/mercadopublico/conciliacion'
    private.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(private,0o700)
    audit=private/f'conciliacion_{args.periodo}_{dt.datetime.now(CHILE):%Y%m%d_%H%M%S}.json'
    audit.write_text(json.dumps({'pares':list(found.values()),'ambiguos':ambiguous},ensure_ascii=False),encoding='utf8')
    os.chmod(audit,0o600)
    report['auditoria_local']=str(audit)
    # Contraste multi-período: nunca exige ZIP COT del mes en curso.
    # Para todas las pruebas, consultar MER en modo solo lectura.
    import gspread
    from google.oauth2.service_account import Credentials
    root=Path(__file__).resolve().parents[1]
    catalogue=json.loads((root/'config/catalogo_sheets.json').read_text(encoding='utf8'))
    info=catalogue['periodos'].get(args.periodo)
    if not info or info.get('tipo')!='operativo' or not info.get('id'):
        raise SystemExit('BLOQUEADO: destino MER operativo no catalogado')
    if args.periodo!=dt.datetime.now(CHILE).strftime('%Y-%m'):
        raise SystemExit('BLOQUEADO: conciliación solamente en período vigente')
    secret=os.environ.get('GOOGLE_APPLICATION_CREDENTIALS','')
    if not secret or not Path(secret).is_file():
        raise SystemExit('BLOQUEADO: credenciales locales no encontradas')
    scopes=['https://www.googleapis.com/auth/spreadsheets'] if args.aplicar else ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds=Credentials.from_service_account_file(secret,scopes=scopes)
    client=gspread.authorize(creds)
    # Reutilizar claves previamente catalogadas, nunca reimportar históricos.
    cot_codes={}; existing_pairs=set(); read_books={}
    def book_for(period,metadata):
        id_=metadata['id']
        if id_ not in read_books:read_books[id_]=client.open_by_key(id_)
        return read_books[id_]
    for period,metadata in sorted(catalogue['periodos'].items()):
        if period>args.periodo or metadata.get('tipo') not in ('historico','histórico','operativo') or not metadata.get('id'):
            continue
        # No consultar meses futuros ni un operativo antiguo: históricos aprobados únicamente.
        if period!=args.periodo and metadata.get('tipo') not in ('historico','histórico'):
            continue
        book=book_for(period,metadata)
        proc=book.worksheet('Procesos').col_values(1)[1:]
        for code in proc:
            code=clean(code).upper()
            if COT_RE.fullmatch(code):cot_codes.setdefault(code,set()).add(period)
        links=book.worksheet('VinculosCOT_OC').get_all_values()
        if not links or links[0]!=SCHEMA:
            raise RuntimeError('Esquema incompatible en VinculosCOT_OC de '+period)
        for row in links[1:]:
            if row and len(row)>2 and row[1] and row[2]:
                existing_pairs.add((row[1].strip().upper(),row[2].strip().upper()))
        report.setdefault('consultados',{})[period]={
            'procesos':len(proc),'vinculos':len(links)-1}
    approved=[]; missing=[]; already=[]
    for row in found.values():
        pair=(row[1],row[2])
        if pair in existing_pairs:already.append(row);continue
        if row[1] not in cot_codes:missing.append(row);continue
        approved.append(row)
    report.update({'candidatos_documentales':len(found),
      'ya_existentes_multimes':len(already),
      'cot_ausente_en_mer':len(missing),
      'nuevos_con_cot_verificada':len(approved),
      'ambiguos_sin_aplicar':len(ambiguous),
      'estado':'SIMULACION_CON_CONTRASTE_MULTIMES'})
    report['detalle_local'] = str(audit)
    # El resultado es un conteo de pares con COT registrada, no una certificación
    # automática de adjudicación. Los casos ambiguos quedan excluidos.
    if args.aplicar:
        import fcntl,importlib.util
        lockpath=root/'logs/.mer_escritura_compartida.lock'
        lockpath.parent.mkdir(exist_ok=True,parents=True)
        with lockpath.open('a+') as handle:
            try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise RuntimeError('MER ocupado: ejecución abortada')
            # Relectura bajo el candado: puede haber escrituras desde la simulación.
            dest=book_for(args.periodo,info)
            ws=dest.worksheet('VinculosCOT_OC')
            old=ws.get_all_values()
            if not old or old[0]!=SCHEMA:raise RuntimeError('Cabeceras incompatibles')
            existing_dest={r[0] for r in old[1:] if r}
            to_add=[r for r in approved if r[0] not in existing_dest]
            report['nuevos_a_insertar']=len(to_add)
            if to_add:
                sp=importlib.util.spec_from_file_location('base',root/'scripts/etl_zip_dos_fuentes.py')
                base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
                sp2=importlib.util.spec_from_file_location('schema',root/'scripts/importador_historicos_v2.py')
                schema=importlib.util.module_from_spec(sp2);sp2.loader.exec_module(schema)
                report['respaldo_local']=base.respaldo_local(dest,schema.SCHEMA,args.periodo)
                for i in range(0,len(to_add),200):
                    batch=to_add[i:i+200]
                    present=set(ws.col_values(1)[1:])
                    pending=[r for r in batch if r[0] not in present]
                    if pending:ws.append_rows(pending,value_input_option='RAW',insert_data_option='INSERT_ROWS')
            verified={r[0]:r for r in ws.get_all_values()[1:] if r}
            if any(verified.get(r[0])!=r for r in to_add):
                raise RuntimeError('Verificación posterior fallida; revisar escritura parcial')
            report['nuevos_confirmados']=len(to_add)
            report['estado']='CONCILIACION_VERIFICADA'
            fcntl.flock(handle,fcntl.LOCK_UN)
    # El reporte público carece de contenido de textos y credenciales.
    tmp=target.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    os.replace(tmp,target)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
