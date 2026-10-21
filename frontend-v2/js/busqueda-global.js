// Búsqueda global V2: verifica las palabras completas sobre fragmentos selectivos.
const el=id=>document.getElementById(id);
const fields={
 procesos:[['codigo','Código'],['nombre','Proceso'],['organismo_comprador','Organismo'],['estado','Estado']],
 ofertas:[['codigo','Proceso'],['proveedor','Proveedor'],['monto_ofertado_clp','Monto CLP']],
 resultados:[['codigo','Proceso'],['adjudicatario','Proveedor informado'],['validado','Verificación']],
 ordenescompra:[['codigo_oc','Orden de compra'],['codigo_proceso','Proceso'],['proveedor','Proveedor']]
};
const searchable={procesos:['codigo','nombre','organismo_comprador'],ofertas:['codigo','proveedor'],resultados:['codigo','adjudicatario'],ordenescompra:['codigo_oc','codigo_proceso','proveedor']};
const norm=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const terms=s=>norm(s).match(/[a-z0-9]+/g)||[];
function matches(record,query,entity){
 const words=new Set(searchable[entity].flatMap(key=>terms(record[key])));
 return query.every(term=>words.has(term));
}
let seq=0,session=null;
function message(text){el('busqueda-global-estado').textContent=text}
function clear(text){
 seq++;session=null;
 el('busqueda-global-columnas').replaceChildren();
 el('busqueda-global-filas').replaceChildren();
 el('busqueda-global-pagina').textContent='Sin resultados';
 el('busqueda-global-anterior').disabled=true;el('busqueda-global-siguiente').disabled=true;
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
function valid(s,t){return seq===s&&session===t&&el('periodo').value===t.period&&el('entidad').value===t.entity}
async function collect(s,t,target){
 // Explorar solo los fragmentos requeridos para las páginas solicitadas.
 while(valid(s,t)&&t.found.length<target&&t.cursor<t.refs.length){
  const part=t.refs[t.cursor][0];
  if(!Number.isInteger(part)||part<0||part>=t.parts.length)throw Error('Fragmento indexado inválido');
  const group=[];
  while(t.cursor<t.refs.length&&t.refs[t.cursor][0]===part)group.push(t.refs[t.cursor++]);
  if(!/^data\/partes\/[a-z]+\/20\d{2}-\d{2}\/[a-z0-9_-]+\.json$/.test(t.parts[part]))throw Error('Ruta de datos inválida');
  const rows=await read(t.parts[part]);
  if(!valid(s,t))return;
  if(!Array.isArray(rows))throw Error('Fragmento inválido');
  for(const [,pos] of group){
   if(!Number.isInteger(pos)||pos<0||pos>=rows.length)throw Error('Referencia inválida');
   if(matches(rows[pos],t.tokens,t.entity))t.found.push({part,pos,record:rows[pos]});
  }
 }
}
async function draw(s,t){
 if(!valid(s,t))return;
 const limit=(t.page+1)*10+1;
 message('Comprobando coincidencias exactas en fragmentos públicos…');
 el('busqueda-global-anterior').disabled=true;el('busqueda-global-siguiente').disabled=true;
 try{
  await collect(s,t,limit);
  if(!valid(s,t))return;
  const visible=t.found.slice(t.page*10,(t.page+1)*10);
  const head=document.createElement('tr');
  for(const [,label] of fields[t.entity]){const th=document.createElement('th');th.textContent=label;head.append(th)}
  const action=document.createElement('th');action.textContent='Acción';head.append(action);
  const frag=document.createDocumentFragment();
  for(const item of visible){
   const tr=document.createElement('tr');
   for(const [key] of fields[t.entity]){const td=document.createElement('td');td.textContent=String(item.record[key]??'')||'No informado';tr.append(td)}
   const td=document.createElement('td'),btn=document.createElement('button');
   btn.textContent='Ver detalle';
   btn.addEventListener('click',()=>window.openIndexedRecord?.(item.part,item.pos,t.period,t.entity));
   td.append(btn);tr.append(td);frag.append(tr);
  }
  if(!visible.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=fields[t.entity].length+1;td.textContent='No se encontraron coincidencias exactas.';tr.append(td);frag.append(tr)}
  el('busqueda-global-columnas').replaceChildren(head);
  el('busqueda-global-filas').replaceChildren(frag);
  const completed=t.cursor>=t.refs.length;
  el('busqueda-global-pagina').textContent='Página '+(visible.length?t.page+1:0)+(completed?' de '+Math.max(1,Math.ceil(t.found.length/10)):' · más resultados por comprobar');
  el('busqueda-global-anterior').disabled=t.page===0;
  el('busqueda-global-siguiente').disabled=t.found.length<limit&&completed;
  message((completed?t.found.length.toLocaleString('es-CL')+' coincidencias exactas':t.found.length.toLocaleString('es-CL')+' coincidencias exactas verificadas hasta ahora')+' · '+t.period+' · '+t.entity+'.');
 }catch(e){if(valid(s,t))message('No se pudo completar la búsqueda: '+e.message)}
}
async function search(){
 const now=++seq,period=el('periodo').value,entity=el('entidad').value;
 session=null;
 const query=[...new Set(terms(el('busqueda-global-texto').value))];
 if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(period)||!fields[entity]){clear('Seleccione un período y una entidad.');return}
 if(!query.length||query.some(t=>t.length<3)){clear('Escriba palabras de al menos 3 caracteres.');return}
 message('Consultando índice de '+period+'…');
 try{
  const meta=await read('data/busqueda/'+period+'/'+entity+'/meta.json');
  if(now!==seq)return;
  if(meta.version!==3||meta.periodo!==period||meta.entidad!==entity)throw Error('Índice incompatible');
  const response=await fetch('./data/catalogo-publico.json');
  if(!response.ok)throw Error('No se pudo consultar el catálogo');
  const catalogue=await response.json();
  const parts=catalogue.periodos?.find(p=>p.periodo===period)?.partes?.[entity];
  if(!Array.isArray(parts)||parts.length!==meta.fragmentos)throw Error('Índice desactualizado');
  const grouped=new Map();
  for(const key of [...new Set(query.map(t=>t.slice(0,2)))]){
   try{grouped.set(key,await read('data/busqueda/'+period+'/'+entity+'/'+key+'.json'))}
   catch(e){if(String(e.message).includes('404'))grouped.set(key,{});else throw e}
   if(now!==seq)return;
  }
  const lists=query.map(token=>grouped.get(token.slice(0,2))?.[token.slice(0,3)]||[]);
  lists.sort((a,b)=>a.length-b.length);
  const others=lists.slice(1).map(list=>new Set(list.map(v=>v.join(':'))));
  const refs=(lists[0]||[]).filter(ref=>others.every(set=>set.has(ref.join(':'))));
  refs.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  const t={period,entity,parts,tokens:query,refs,cursor:0,found:[],page:0};
  session=t;
  await draw(now,t);
 }catch(e){if(now===seq)clear('No fue posible consultar el índice: '+e.message+'. La consulta por bloques sigue disponible.')}
}
el('busqueda-global-boton').addEventListener('click',search);
el('busqueda-global-texto').addEventListener('keydown',e=>{if(e.key==='Enter')search()});
el('busqueda-global-anterior').addEventListener('click',()=>{if(session&&session.page>0){session.page--;draw(seq,session)}});
el('busqueda-global-siguiente').addEventListener('click',()=>{if(session){session.page++;draw(seq,session)}});
for(const id of ['periodo','entidad'])el(id).addEventListener('change',()=>clear('Seleccione Buscar en el período para iniciar una consulta.'));
