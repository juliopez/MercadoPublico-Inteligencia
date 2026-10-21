// MER v2: carga selectiva por período. No consulta Google Sheets desde el navegador.
const $=id=>document.getElementById(id);
const allowed=['procesos','ofertas','resultados','ordenescompra'];
const state={manifest:null,records:[],page:0,perPage:10,token:0};
function status(message){$('status').textContent=message}
function safePart(path,period,entity){return typeof path==='string'&&new RegExp('^data/partes/'+entity+'/'+period+'/[a-z0-9_-]+\\.json$').test(path)}
function textCell(value){const td=document.createElement('td');td.textContent=String(value??'');return td}
function render(){
 const term=$('buscar').value.trim().toLocaleLowerCase('es');
 const selected=state.records.filter(r=>!term||Object.values(r).some(v=>String(v??'').toLocaleLowerCase('es').includes(term)));
 const pageSize=state.perPage;
 const pages=Math.ceil(selected.length/pageSize);state.page=Math.min(state.page,Math.max(0,pages-1));
 const current=selected.slice(state.page*pageSize,(state.page+1)*pageSize);
 const fields=current.length?Object.keys(current[0]).slice(0,16):[];
 $('columns').replaceChildren();const tr=document.createElement('tr');
 for(const f of fields){const th=document.createElement('th');th.textContent=f;tr.append(th)}
 if(!fields.length){const th=document.createElement('th');th.textContent='Resultados';tr.append(th)}else{const th=document.createElement('th');th.textContent='Acciones';tr.append(th)}
 $('columns').append(tr);$('rows').replaceChildren();
 for(const record of current){const row=document.createElement('tr');for(const f of fields)row.append(textCell(record[f]));const action=document.createElement('td');const button=document.createElement('button');button.textContent='Ver detalle';button.className='detail-button';button.addEventListener('click',()=>showDetail(record));action.append(button);row.append(action);$('rows').append(row)}
 if(!current.length){const row=document.createElement('tr');row.append(textCell('No hay registros para la consulta.'));$('rows').append(row)}
 $('counter').textContent=selected.length.toLocaleString('es-CL')+' registros encontrados';
 $('page').textContent='Bloque '+(state.chunkIndex+1)+'/'+Math.max(state.parts.length,1)+' · Página '+(pages?state.page+1:0)+'/'+pages;
 $('prev').disabled=state.page===0&&state.chunkIndex===0;$('next').disabled=state.page+1>=pages&&state.chunkIndex>=state.parts.length-1;
}
function showDetail(record){
 const area=$('detalle'), body=$('detalle-campos');
 body.replaceChildren();
 for(const [key,value] of Object.entries(record)){
  const dt=document.createElement('dt');dt.textContent=key.replaceAll('_',' ');
  const dd=document.createElement('dd');dd.textContent=String(value??'');
  body.append(dt,dd);
 }
 const external=$('detalle-enlace');
 const raw=String(record.url_detalle??'').trim();
 let url=null;
 try{
  const candidate=new URL(raw);
  if(candidate.protocol==='https:'&&['www.mercadopublico.cl','mercadopublico.cl'].includes(candidate.hostname))url=candidate.href;
 }catch{}
 const code=String(record.codigo??'');
 if(!url&&$('entidad').value==='procesos'&&/^[a-z0-9-]{5,80}$/i.test(code))
  url='https://www.mercadopublico.cl/fichaLicitacion.html?idLicitacion='+encodeURIComponent(code);
 external.hidden=!url;
 if(url)external.href=url;else external.removeAttribute('href');
 $('detalle-titulo').textContent='Detalle del registro · '+$('periodo').value;
 area.hidden=false;area.scrollIntoView({behavior:'smooth',block:'start'});
 const linked=$('detalle-relaciones');
 linked.hidden=$('entidad').value!=='procesos';
 if(!linked.hidden)loadRelated(code,$('periodo').value);
}
function closeDetail(){detailRequest++;$('detalle').hidden=true;$('detalle-campos').replaceChildren();$('detalle-relaciones').hidden=true;}


// Los índices solo contienen código → archivos públicos. No cargamos el mes completo.
let detailRequest=0;
const indexCache=new Map();
async function readJsonPublic(path){
 const urls=['./'+path,'https://raw.githubusercontent.com/juliopez/MercadoPublico-Inteligencia/main/frontend-v2/'+path];
 let last;
 for(const url of urls){
  try{
   const response=await fetch(url,{cache:'no-store'});
   if(!response.ok)throw Error('HTTP '+response.status);
   return await response.json();
  }catch(error){last=error}
 }
 throw last;
}
function renderLinkedRecords(target,items,kind){
 const container=$(target);container.replaceChildren();
 const description=document.createElement('p');description.className='muted';
 description.textContent=items.length.toLocaleString('es-CL')+' registros relacionados por código de proceso.';
 container.append(description);
 if(!items.length)return;
 const table=document.createElement('table'),head=document.createElement('tr'),body=document.createElement('tbody');
 const fields=kind==='ofertas'?['proveedor','monto_ofertado_clp','seleccionado']:
  kind==='resultados'?['adjudicatario','monto_adjudicado_clp','validado','estado_verificacion_oc']:
  ['codigo_oc','proveedor','monto_total_oc_clp','estado'];
 for(const col of fields){const th=document.createElement('th');th.textContent=col.replaceAll('_',' ');head.append(th)}
 const thead=document.createElement('thead');thead.append(head);table.append(thead,body);
 container.append(table);
 const nav=document.createElement('div');nav.className='pagination';
 const prev=document.createElement('button');prev.textContent='Anterior';
 const pageText=document.createElement('span');
 const next=document.createElement('button');next.textContent='Siguiente';
 nav.append(prev,pageText,next);container.append(nav);
 let page=0;const perPage=10,pages=Math.ceil(items.length/perPage);
 function draw(){
  body.replaceChildren();
  for(const item of items.slice(page*perPage,(page+1)*perPage)){
   const tr=document.createElement('tr');
   for(const field of fields)tr.append(textCell(item[field]));
   body.append(tr);
  }
  prev.disabled=page===0;next.disabled=page===pages-1;
  pageText.textContent='Página '+(page+1)+' de '+pages;
 }
 prev.addEventListener('click',()=>{if(page>0){page--;draw()}});
 next.addEventListener('click',()=>{if(page+1<pages){page++;draw()}});
 draw();
}
async function loadRelated(code,period){
 const seq=++detailRequest;
 for(const target of ['detalle-ofertas','detalle-resultados','detalle-oc'])$(target).replaceChildren();
 $('detalle-relaciones-estado').textContent='Consultando relaciones indexadas…';
 if(!code){$('detalle-relaciones-estado').textContent='Sin código de proceso para relacionar.';return}
 try{
  let index=indexCache.get(period);
  if(!index){
   index=await readJsonPublic('data/indices/'+period+'.json');
   if(index.periodo!==period||!index.entidades)throw Error('Índice incompatible');
   indexCache.set(period,index);
  }
  if(seq!==detailRequest)return;
  let loaded=0;
  for(const [entity,target,key] of [['ofertas','detalle-ofertas','codigo'],['resultados','detalle-resultados','codigo'],['ordenescompra','detalle-oc','codigo_proceso']]){
   const refs=index.entidades?.[entity]?.[code]||[];
   const paths=refs.map(ref=>typeof ref==='number'?index.archivos?.[entity]?.[ref]:ref);
   const records=[];
   for(const path of paths){
    if(!safePart(path,period,entity))throw Error('Ruta vinculada no válida');
    const chunk=await readJsonPublic(path);
    if(!Array.isArray(chunk))throw Error('Fragmento inválido');
    for(const item of chunk)if(String(item[key]||'').trim()===code)records.push(item);
    if(seq!==detailRequest)return;
   }
   renderLinkedRecords(target,records,entity);
   loaded+=records.length;
  }
  if(seq===detailRequest)$('detalle-relaciones-estado').textContent='Relaciones disponibles: '+loaded.toLocaleString('es-CL')+' registros públicos asociados al código '+code+'.';
 }catch(error){
  if(seq===detailRequest)$('detalle-relaciones-estado').textContent='No fue posible consultar las relaciones indexadas: '+error.message+'. La ficha básica sigue disponible.';
 }
}

// Lectura por bloque: cada parte tiene hasta 1000 filas; no descargar 400+ partes al abrir.
const chunkSize=1000;
state.parts=[];state.chunkIndex=0;state.cache=new Map();
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function getPart(path){
 if(!safePart(path,$('periodo').value,$('entidad').value))throw Error('Ruta de fragmento no válida');
 const urls=['./'+path,'https://raw.githubusercontent.com/juliopez/MercadoPublico-Inteligencia/main/frontend-v2/'+path];
 let error;
 for(const url of urls){
  for(let attempt=0;attempt<2;attempt++){
   try{
    const response=await fetch(url,{cache:'no-store'});
    if(!response.ok)throw Error('HTTP '+response.status);
    const rows=await response.json();
    if(!Array.isArray(rows))throw Error('Formato de fragmento incorrecto');
    return rows;
   }catch(e){error=e;if(attempt===0)await pause(450)}
  }
 }
 throw Error('No se pudo leer el fragmento '+path+': '+error.message);
}
async function loadChunk(index){
 const token=state.token,parts=state.parts;
 if(index<0||index>=parts.length)return;
 $('prev').disabled=true;$('next').disabled=true;
 status('Cargando bloque '+(index+1)+' de '+parts.length+'…');
 try{
  const rows=state.cache.has(index)?state.cache.get(index):await getPart(parts[index]);
  if(token!==state.token)return;
  state.cache.set(index,rows);
  // Cache acotada a los bloques cercanos.
  while(state.cache.size>3)state.cache.delete(state.cache.keys().next().value);
  state.chunkIndex=index;state.records=rows;state.page=0;render();
  $('stat-registros').textContent=Number(state.total).toLocaleString('es-CL');
  status('Bloque '+(index+1)+' de '+parts.length+' cargado. Búsqueda limitada al bloque visible; '+Number(state.total).toLocaleString('es-CL')+' registros publicados en este período.');
 }catch(e){if(token===state.token){state.records=[];render();status('Error al cargar: '+e.message)}}
}
async function consult(){
 const period=$('periodo').value,entity=$('entidad').value;
 if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(period)||!allowed.includes(entity))return;
 const info=state.manifest.periodos.find(p=>p.periodo===period);
 const parts=info?.partes?.[entity];
 if(!Array.isArray(parts)){status('Entidad no publicada para este período.');return}
 ++state.token;state.cache.clear();state.parts=parts;state.total=info.conteos?.[entity]??0;state.records=[];state.page=0;closeDetail();render();
 $('stat-registros').textContent=Number(state.total).toLocaleString('es-CL');
 $('consultar').disabled=false;
 if(!parts.length){status('La entidad está publicada, pero no registra filas en este período.');return}
 await loadChunk(0);
}

async function init(){
 try{
  const response=await fetch('./data/catalogo-publico.json',{cache:'no-store'});
  if(!response.ok)throw Error('Catálogo público v2 no disponible');
  const payload=await response.json();
  if(!Array.isArray(payload.periodos))throw Error('Catálogo incompatible');
  state.manifest=payload;
  for(const item of payload.periodos){
   if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(item.periodo))continue;
   const option=document.createElement('option');option.value=item.periodo;option.textContent=item.periodo+' · '+(item.tipo==='historico'?'Histórico':'Operativo');$('periodo').append(option)
  }
  $('stat-fecha').textContent=payload.fecha_publicacion||'Pendiente';
  $('consultar').disabled=payload.periodos.length===0;
  status(payload.periodos.length?'Seleccione un período y una entidad.':'Frontend v2 preparado. Aún no se han publicado extractos MER v2; la versión 1 sigue disponible.');
 }catch(e){status('Catálogo v2 todavía no publicado: '+e.message)}
}
$('periodo').addEventListener('change',()=>{$('stat-periodo').textContent=$('periodo').value||'—';++state.token;state.records=[];state.parts=[];state.chunkIndex=0;state.cache.clear();state.page=0;closeDetail();render()});
$('detalle-cerrar').addEventListener('click',closeDetail);
$('buscar').addEventListener('input',()=>{state.page=0;render()});
$('consultar').addEventListener('click',consult);
$('entidad').addEventListener('change',()=>{++state.token;state.records=[];state.parts=[];state.chunkIndex=0;state.cache.clear();state.page=0;closeDetail();render()});
$('prev').addEventListener('click',()=>{if(state.page===0&&state.chunkIndex>0)loadChunk(state.chunkIndex-1);else{state.page--;render()}});
$('next').addEventListener('click',()=>{const count=state.records.filter(r=>!$('buscar').value.trim()||Object.values(r).some(v=>String(v??'').toLocaleLowerCase('es').includes($('buscar').value.trim().toLocaleLowerCase('es')))).length;if((state.page+1)*state.perPage>=count&&state.chunkIndex<state.parts.length-1)loadChunk(state.chunkIndex+1);else{state.page++;render()}});
init();