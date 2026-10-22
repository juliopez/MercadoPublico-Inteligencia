// Búsqueda global V2: verifica las palabras completas sobre fragmentos selectivos.
const el=id=>document.getElementById(id);
const fields={
 procesos:[['codigo','Código'],['nombre','Proceso'],['organismo_comprador','Organismo'],['estado','Estado']],
 ofertas:[['codigo','Proceso'],['proveedor','Proveedor'],['monto_ofertado_clp','Monto CLP']],
 resultados:[['codigo','Proceso'],['adjudicatario','Proveedor informado'],['monto_adjudicado_clp','Monto informado']],
 ordenescompra:[['codigo_oc','Orden de compra'],['codigo_proceso','Proceso'],['proveedor','Proveedor']]
};
const searchable={procesos:['codigo','nombre','organismo_comprador'],ofertas:['codigo','proveedor'],resultados:['codigo','adjudicatario'],ordenescompra:['codigo_oc','codigo_proceso','proveedor']};
const norm=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const terms=s=>norm(s).match(/[a-z0-9]+/g)||[];
const facetFields={procesos:['estado','modalidad'],ofertas:['seleccionado',null],resultados:['validado',null],ordenescompra:['estado','tipo_oc']};
function matches(record,query,entity,filters={}){
 const words=new Set(searchable[entity].flatMap(key=>terms(record[key])));
 if(!query.every(term=>words.has(term)))return false;
 const [statusField,typeField]=facetFields[entity];
 return (!filters.status||norm(record[statusField]).includes(filters.status))&&
        (!filters.type||norm(record[typeField]).includes(filters.type));
}
function controls(){
 const entity=el('entidad').value;
 const keys=facetFields[entity]||[null,null];
 el('global-estado').disabled=!keys[0];el('global-modalidad').disabled=!keys[1];
 if(!keys[1])el('global-modalidad').value='';
 const names={procesos:['Estado de licitación','Modalidad del proceso'],ofertas:['Selección informada','No corresponde'],resultados:['No corresponde: verificación interna','No corresponde'],ordenescompra:['Estado de orden','Tipo de OC']}[entity];
 if(entity==='resultados')el('global-estado').disabled=true;
 el('global-estado').placeholder=names[0];
 el('global-modalidad').placeholder=names[1];
}
let seq=0,session=null;
let globalSort={key:null,direction:1};
function message(text){el('busqueda-global-estado').textContent=text}
function clear(text){
 seq++;session=null;
 el('busqueda-global-columnas').replaceChildren();
 el('busqueda-global-filas').replaceChildren();
 el('busqueda-global-pagina').textContent='Sin resultados';
 el('busqueda-global-anterior').disabled=true;el('busqueda-global-siguiente').disabled=true;
 el('global-csv').disabled=true;
 el('global-analitica').textContent='Indicadores de consulta: sin ejecutar.';
 el('busqueda-global-progreso').hidden=true;
 message(text);
}
async function read(path){
 if(!/^data\/(busqueda|partes)\/[a-z0-9_\/-]+\.json$/.test(path))throw Error('Ruta no permitida');
 let last;
 for(const url of ['./'+path,'https://raw.githubusercontent.com/juliopez/MercadoPublico-Inteligencia/main/frontend-v2/'+path]){
  try{const response=await fetch(url);if(!response.ok)throw Error('HTTP '+response.status);return await response.json()}catch(e){last=e}
 }
 throw last;
}
function valid(s,t){return seq===s&&session===t&&(t.multi||el('periodo').value===t.period)&&el('entidad').value===t.entity}
async function collect(s,t,target){
 // Explorar solo los fragmentos requeridos para las páginas solicitadas.
 while(valid(s,t)&&t.found.length<target&&t.cursor<t.refs.length){
  const month=t.multi?t.refs[t.cursor][0]:t.period;
  const part=t.multi?t.refs[t.cursor][1]:t.refs[t.cursor][0];
  if(!Number.isInteger(part)||part<0||part>=t.parts[month].length)throw Error('Fragmento indexado inválido');
  const group=[];
  while(t.cursor<t.refs.length&&(t.multi?t.refs[t.cursor][0]===month&&t.refs[t.cursor][1]===part:t.refs[t.cursor][0]===part))group.push(t.refs[t.cursor++]);
  if(!/^data\/partes\/[a-z]+\/20\d{2}-\d{2}\/[a-z0-9_-]+\.json$/.test(t.parts[month][part]))throw Error('Ruta de datos inválida');
  const rows=await read(t.parts[month][part]);
  if(!valid(s,t))return;
  if(!Array.isArray(rows))throw Error('Fragmento inválido');
  const progress=el('busqueda-global-progreso');progress.hidden=false;progress.value=t.refs.length?Math.round(t.cursor/t.refs.length*100):100;
  for(const ref of group){
   const pos=ref[ref.length-1];
   if(!Number.isInteger(pos)||pos<0||pos>=rows.length)throw Error('Referencia inválida');
   if(matches(rows[pos],t.tokens,t.entity,t.filters))t.found.push({part,pos,month,record:rows[pos]});
  }
 }
}
async function draw(s,t){
 if(!valid(s,t))return;
 const limit=(t.page+1)*10+1;
 message('Comprobando registros del período…');
 const progress=el('busqueda-global-progreso');progress.hidden=false;progress.value=t.refs.length?Math.round(t.cursor/t.refs.length*100):100;
 el('busqueda-global-anterior').disabled=true;el('busqueda-global-siguiente').disabled=true;
 try{
  await collect(s,t,limit);
  if(!valid(s,t))return;
  const progress=el('busqueda-global-progreso');progress.hidden=false;progress.value=t.refs.length?Math.round(t.cursor/t.refs.length*100):100;
  const ordering=globalSort.key?[...t.found].sort((a,b)=>globalSort.direction*String(a.record[globalSort.key]??'').localeCompare(String(b.record[globalSort.key]??''),'es',{numeric:true})):t.found;
  const visible=ordering.slice(t.page*10,(t.page+1)*10);
  const head=document.createElement('tr');
  if(t.multi){const th=document.createElement('th');th.textContent='Período';head.append(th)}
  for(const [key,label] of fields[t.entity]){const th=document.createElement('th');const b=document.createElement('button');b.className='sort-heading';b.type='button';b.textContent=label+(globalSort.key===key?(globalSort.direction===1?' ↑':' ↓'):' ⇅');b.addEventListener('click',()=>{globalSort.direction=globalSort.key===key?-globalSort.direction:1;globalSort.key=key;t.page=0;draw(seq,t)});th.append(b);head.append(th)}
  const action=document.createElement('th');action.textContent='Acción';head.append(action);
  const frag=document.createDocumentFragment();
  for(const item of visible){
   const tr=document.createElement('tr');
   if(t.multi){const td=document.createElement('td');td.textContent=item.month;tr.append(td)}
   for(const [key] of fields[t.entity]){const value=item.record[key];const td=document.createElement('td');td.textContent=window.MPV2?.moneyField(key)?window.MPV2.moneyCLP(value):String(value??'')||'No informado';if(window.MPV2?.codeField(key)&&value){const link=document.createElement('button');link.className='code-link';link.textContent=String(value);link.addEventListener('click',()=>window.MPV2.openCode(value,key));td.replaceChildren(link)}tr.append(td)}
   const td=document.createElement('td'),btn=document.createElement('button');
   btn.textContent='Ver detalle';
   btn.addEventListener('click',()=>window.openIndexedRecord?.(item.part,item.pos,item.month,t.entity));
   td.append(btn);tr.append(td);frag.append(tr);
  }
  if(!visible.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=fields[t.entity].length+1+(t.multi?1:0);td.textContent='No se encontraron coincidencias exactas.';tr.append(td);frag.append(tr)}
  el('busqueda-global-columnas').replaceChildren(head);
  el('busqueda-global-filas').replaceChildren(frag);
  const completed=t.cursor>=t.refs.length;
  el('busqueda-global-pagina').textContent='Página '+(visible.length?t.page+1:0)+(completed?' de '+Math.max(1,Math.ceil(t.found.length/10)):' · más resultados por comprobar');
  el('busqueda-global-anterior').disabled=t.page===0;
  el('busqueda-global-siguiente').disabled=t.found.length<limit&&completed;
  const verified=t.found;
  const amountField={procesos:'monto_disponible_clp',ofertas:'monto_ofertado_clp',resultados:'monto_adjudicado_clp',ordenescompra:'monto_total_oc_clp'}[t.entity];
  const numbers=verified.map(x=>String(x.record[amountField]??'').replaceAll('.','').replace(',','.')).filter(Boolean).map(Number).filter(Number.isFinite);
   el('global-analitica').textContent=(completed?'Total verificado del período: ':'Avance de verificación: ')+verified.length.toLocaleString('es-CL')+' registros · '+numbers.length.toLocaleString('es-CL')+' con monto · suma informada $'+Math.round(numbers.reduce((a,b)=>a+b,0)).toLocaleString('es-CL')+'. Los montos son descriptivos.';
   el('global-csv').disabled=verified.length===0;
   message((completed?t.found.length.toLocaleString('es-CL')+' coincidencias exactas':t.found.length.toLocaleString('es-CL')+' coincidencias exactas verificadas hasta ahora')+' · '+(t.multi?'todos los períodos':t.period)+' · '+t.entity+'.');
 }catch(e){if(valid(s,t))message('No se pudo completar la búsqueda: '+e.message)}
}
async function search(){
 const now=++seq,period=el('periodo').value,entity=el('entidad').value,multi=el('busqueda-global-alcance').value==='todos';
 el('busqueda-global-progreso').hidden=false;el('busqueda-global-progreso').value=0;
 session=null;
 const raw=el('busqueda-global-texto').value.trim();
 const query=[...new Set(terms(raw))];
 const codeQuery=/^[a-z0-9]+(?:-[a-z0-9]+)+$/i.test(raw);
 const indexedTokens=query.filter(t=>t.length>=3);
 if((!multi&&!/^20\d{2}-(0[1-9]|1[0-2])$/.test(period))||!fields[entity]){clear('Seleccione un período y una entidad.');return}
 if(!indexedTokens.length||(!codeQuery&&query.some(t=>t.length<3))){clear('Introduce palabras de al menos 3 caracteres o un código completo.');return}
 message(multi?'Consultando índices de todos los períodos publicados…':'Consultando índice de '+period+'…');
 try{
  const response=await fetch('./data/catalogo-publico.json');
  if(!response.ok)throw Error('No se pudo consultar el catálogo');
  const catalogue=await response.json();
  const months=multi?catalogue.periodos.map(p=>p.periodo):[period];
  const refs=[],parts={};
  for(const month of months){
   if(now!==seq)return;
   let meta;
   try{meta=await read('data/busqueda/'+month+'/'+entity+'/meta.json')}
   catch(e){if(multi&&String(e).includes('404'))continue;throw e}
   if(meta.version!==3||meta.periodo!==month||meta.entidad!==entity)throw Error('Índice incompatible: '+month);
   const paths=catalogue.periodos?.find(p=>p.periodo===month)?.partes?.[entity];
   if(!Array.isArray(paths)||paths.length!==meta.fragmentos)throw Error('Índice desactualizado: '+month);
   parts[month]=paths;
   const grouped=new Map();
   for(const key of [...new Set(indexedTokens.map(t=>t.slice(0,2)))]){
    try{grouped.set(key,await read('data/busqueda/'+month+'/'+entity+'/'+key+'.json'))}
    catch(e){if(String(e.message).includes('404'))grouped.set(key,{});else throw e}
    if(now!==seq)return;
   }
   const lists=indexedTokens.map(token=>grouped.get(token.slice(0,2))?.[token.slice(0,3)]||[]);
   lists.sort((a,b)=>a.length-b.length);
   const others=lists.slice(1).map(list=>new Set(list.map(v=>v.join(':'))));
   for(const ref of (lists[0]||[]))if(others.every(set=>set.has(ref.join(':'))))refs.push(multi?[month,...ref]:ref);
  }
  refs.sort((a,b)=>multi?(a[0].localeCompare(b[0])||a[1]-b[1]||a[2]-b[2]):(a[0]-b[0]||a[1]-b[1]));
  globalSort={key:null,direction:1};
  const t={period,entity,multi,parts,tokens:query,filters:{status:norm(el('global-estado').value.trim()),type:norm(el('global-modalidad').value.trim())},refs,cursor:0,found:[],page:0};
  session=t;
  await draw(now,t);
 }catch(e){if(now===seq)clear('No fue posible consultar el índice: '+e.message+'. La consulta por bloques sigue disponible.')}
}
el('busqueda-global-boton').addEventListener('click',search);
el('busqueda-global-texto').addEventListener('keydown',e=>{if(e.key==='Enter')search()});
el('busqueda-global-anterior').addEventListener('click',()=>{if(session&&session.page>0){session.page--;draw(seq,session)}});
el('busqueda-global-siguiente').addEventListener('click',()=>{if(session){session.page++;draw(seq,session)}});
for(const id of ['periodo','entidad'])el(id).addEventListener('change',()=>{if(id==='entidad'||el('busqueda-global-alcance').value!=='todos')clear('Seleccione Buscar para iniciar una consulta.')});
el('busqueda-global-alcance').addEventListener('change',()=>clear('Seleccione Buscar para iniciar una consulta.'));
async function exportGlobal(){
 const t=session,s=seq;
 if(!t)return;
 const button=el('global-csv');button.disabled=true;
 try{
  const limit=20001;
  message('Completando verificación de coincidencias para la exportación CSV…');
  await collect(s,t,limit);
  if(!valid(s,t))return;
  if(t.found.length>20000||t.cursor<t.refs.length){
   message('La consulta excede 20.000 coincidencias o aún requiere demasiados registros. Refina las palabras clave antes de exportar para evitar un CSV incompleto.');
   return;
  }
  const cols=[...(t.multi?['periodo']:[]),...fields[t.entity].map(([key])=>key)];
  const safe=x=>'"'+String(x??'').replaceAll('"','""').replace(/^[=+@\-\t\r]/,m=>"'"+m)+'"';
  const all=globalSort.key?[...t.found].sort((a,b)=>globalSort.direction*String(a.record[globalSort.key]??'').localeCompare(String(b.record[globalSort.key]??''),'es',{numeric:true})):t.found;
  const csv='\uFEFF'+[cols.join(';'),...all.map(x=>cols.map(key=>safe(key==='periodo'?x.month:x.record[key])).join(';'))].join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download='busqueda-global-'+t.entity+'-'+t.period+'.csv';
  document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  message('CSV completo exportado: '+t.found.length.toLocaleString('es-CL')+' registros verificados de '+t.period+'.');
 }catch(e){if(valid(s,t))message('No fue posible exportar: '+e.message)}
 finally{if(valid(s,t))button.disabled=t.found.length===0}
}
el('global-csv').addEventListener('click',exportGlobal);
for(const id of ['global-estado','global-modalidad'])el(id).addEventListener('change',()=>clear('Filtros modificados. Ejecute nuevamente la búsqueda global.'));
el('entidad').addEventListener('change',controls);
controls();
