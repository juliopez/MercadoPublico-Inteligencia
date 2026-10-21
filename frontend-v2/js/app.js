// MER v2: carga selectiva por período. No consulta Google Sheets desde el navegador.
const $=id=>document.getElementById(id);
const allowed=['procesos','ofertas','resultados','ordenescompra'];
const state={manifest:null,records:[],page:0,perPage:10,token:0,sort:{key:null,direction:1}};
function status(message){$('status').textContent=message}
function safePart(path,period,entity){return typeof path==='string'&&new RegExp('^data/partes/'+entity+'/'+period+'/[a-z0-9_-]+\\.json$').test(path)}
function textCell(value){const td=document.createElement('td');td.textContent=String(value??'');return td}
const tableColumns={
 procesos:[['codigo','Código'],['nombre','Nombre del proceso'],['modalidad','Modalidad'],['organismo_comprador','Organismo comprador'],['estado','Estado'],['fecha_publicacion','Publicación'],['fecha_cierre','Cierre'],['monto_disponible_clp','Monto disponible']],
 ofertas:[['codigo','Proceso'],['proveedor','Proveedor'],['monto_ofertado_clp','Monto ofertado'],['seleccionado','Oferta seleccionada'],['fecha_oferta','Fecha de oferta']],
 resultados:[['codigo','Proceso'],['adjudicatario','Proveedor informado'],['monto_adjudicado_clp','Monto adjudicado'],['monto_oferta_seleccionada_clp','Oferta seleccionada']],
 ordenescompra:[['codigo_oc','Orden de compra'],['codigo_proceso','Proceso asociado'],['proveedor','Proveedor'],['estado','Estado'],['monto_total_oc_clp','Monto total'],['fecha_creacion','Creación']]
};
function formatTableValue(record,key){
 const value=record[key];
 if(value===null||value===undefined||String(value).trim()==='')return 'No informado';
 if(moneyField(key)){
  const raw=String(value).trim().replace(/\\./g,'').replace(',','.');
  const amount=Number(raw);
  return Number.isFinite(amount)?'$'+Math.round(amount).toLocaleString('es-CL'):String(value);
 }
 return String(value);
}
// Presentación pública común. Los valores originales de los JSON no cambian.
function moneyField(key){return /(^monto|_monto|_clp$|precio|valor_total)/i.test(key)}
function moneyCLP(value){
 if(value==null||String(value).trim()==='')return 'No informado';
 const n=Number(String(value).trim().replaceAll('.','').replace(',','.'));
 return Number.isFinite(n)?new Intl.NumberFormat('es-CL',{style:'currency',currency:'CLP',maximumFractionDigits:0}).format(n):String(value);
}
function codeField(key){return ['codigo','codigo_proceso','codigo_oc','codigoexterno','codigo_externo'].includes(key.toLowerCase())}
let previousContext=null;
function openCode(code,key){
 if(!/^[a-z0-9-]{4,100}$/i.test(String(code??'')))return;
 const current=$('entidad').value;
 const target=key==='codigo_oc'?'ordenescompra':'procesos';
 previousContext={period:$('periodo').value,entity:$('entidad').value,block:state.chunkIndex,search:$('buscar').value,global:$('busqueda-global-texto').value,status:$('global-estado').value,type:$('global-modalidad').value};
 $('volver-contexto').hidden=false;
 $('entidad').value=target;$('entidad').dispatchEvent(new Event('change'));
 $('buscar').value='';
 $('busqueda-global-texto').value=String(code);
 $('global-estado').value='';$('global-modalidad').value='';
 $('busqueda-global-boton').click();
 $('busqueda-global').scrollIntoView({behavior:'smooth',block:'start'});
}
function displayedCell(record,key){
 const td=textCell(moneyField(key)?moneyCLP(record[key]):record[key]??'No informado');
 if(codeField(key)&&record[key]){
  const button=document.createElement('button');button.type='button';button.className='code-link';
  button.textContent=String(record[key]);button.title='Buscar este código en el Observatorio';
  button.addEventListener('click',()=>openCode(record[key],key));
  td.replaceChildren(button);
 }
 return td;
}
$('volver-contexto').addEventListener('click',async ()=>{
 const old=previousContext;if(!old)return;
 previousContext=null;$('volver-contexto').hidden=true;
 if($('periodo').value!==old.period){$('periodo').value=old.period;$('periodo').dispatchEvent(new Event('change'))}
 $('entidad').value=old.entity;$('entidad').dispatchEvent(new Event('change'));
 $('buscar').value=old.search;
 $('busqueda-global-texto').value=old.global;
 $('global-estado').value=old.status;$('global-modalidad').value=old.type;
 await consult();
 if(old.block>0&&old.block<state.parts.length)await loadChunk(old.block);
 $('consulta').scrollIntoView({behavior:'smooth',block:'start'});
});
window.MPV2={moneyCLP,moneyField,codeField,openCode};
function localFilterFields(){
 const e=$('entidad').value;
 return {state:e==='procesos'||e==='ordenescompra'?'estado':e==='ofertas'?'seleccionado':'validado',type:e==='procesos'?'modalidad':e==='ordenescompra'?'tipo_oc':null};
}
function refreshLocalFilters(){
 const fields=localFilterFields();
 for(const [id,key] of [['filtro-estado',fields.state],['filtro-modalidad',fields.type]]){
  const select=$(id),old=select.value;
  select.replaceChildren(new Option(id==='filtro-estado'?'Todos':'Todas',''));
  if(key){for(const v of [...new Set(state.records.map(r=>String(r[key]??'').trim()).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'es')))select.add(new Option(v,v))}
  select.disabled=!key;
  select.value=[...select.options].some(o=>o.value===old)?old:'';
 }
}
function filteredBlock(){
 const term=$('buscar').value.trim().toLocaleLowerCase('es');
 const fields=localFilterFields(),statusValue=$('filtro-estado').value,typeValue=$('filtro-modalidad').value;
 return state.records.filter(r=>(!term||Object.values(r).some(v=>String(v??'').toLocaleLowerCase('es').includes(term)))&&(!statusValue||String(r[fields.state]??'')===statusValue)&&(!typeValue||(fields.type&&String(r[fields.type]??'')===typeValue)));
}
function compareRows(a,b,key){
 const x=a[key],y=b[key];
 if(x==null||x==='')return y==null||y===''?0:1;
 if(y==null||y==='')return -1;
 if(key.endsWith('_clp'))return Number(String(x).replaceAll('.','').replace(',','.'))-Number(String(y).replaceAll('.','').replace(',','.'));
 return String(x).localeCompare(String(y),'es',{numeric:true,sensitivity:'base'});
}
function ordered(rows){if(!state.sort.key)return rows;return [...rows].sort((a,b)=>state.sort.direction*compareRows(a,b,state.sort.key))}
function sortLocal(key){state.sort.direction=state.sort.key===key?-state.sort.direction:1;state.sort.key=key;state.page=0;render()}
function render(){
 const selected=ordered(filteredBlock());
 const pages=Math.ceil(selected.length/state.perPage);
 state.page=Math.min(state.page,Math.max(0,pages-1));
 const current=selected.slice(state.page*state.perPage,(state.page+1)*state.perPage);
 const entity=$('entidad').value;
 const fields=tableColumns[entity]||[];
 $('resultados').classList.toggle('process-table',entity==='procesos');
 $('columns').replaceChildren();
 const header=document.createElement('tr');
 for(const [key,label] of fields){const th=document.createElement('th');const button=document.createElement('button');button.type='button';button.className='sort-heading';button.textContent=label+(state.sort.key===key?(state.sort.direction===1?' ↑':' ↓'):' ⇅');button.addEventListener('click',()=>sortLocal(key));th.append(button);header.append(th)}
 const actions=document.createElement('th');actions.textContent='Acciones';header.append(actions);$('columns').append(header);
 $('rows').replaceChildren();
 for(const record of current){
  const row=document.createElement('tr');
  for(const [key] of fields){
   const td=displayedCell(record,key);
   if(key==='codigo'||key==='codigo_oc'||key==='codigo_proceso')td.classList.add('process-code');
   if(key==='nombre')td.classList.add('process-name');
   if(key==='estado'){const pill=document.createElement('span');pill.className='state-pill';pill.textContent=td.textContent;td.replaceChildren(pill)}
   if(key.endsWith('_clp'))td.classList.add('amount-cell');
   row.append(td);
  }
  const action=document.createElement('td');const button=document.createElement('button');button.textContent='Ver detalle';button.className='detail-button';button.addEventListener('click',()=>showDetail(record));action.append(button);
  const actorKey=entity==='procesos'?'organismo_comprador':entity==='resultados'?'adjudicatario':'proveedor';
  if(record[actorKey]&&String(record[actorKey]).trim()){
   const profile=document.createElement('button');profile.type='button';profile.className='secondary profile-button';
   profile.textContent=entity==='procesos'?'Perfil organismo':'Perfil proveedor';
   profile.addEventListener('click',()=>showContextProfile(actorKey,String(record[actorKey])));
   action.append(' ',profile);
  }
  const favorite=document.createElement('button');favorite.type='button';favorite.className='secondary';
  favorite.textContent=favorites.some(x=>x.key===favoriteKey(entity,$('periodo').value,record))?'★ Guardado':'☆ Favorito';
  favorite.addEventListener('click',()=>toggleFavorite(record));action.append(' ',favorite);
  row.append(action);$('rows').append(row);
 }
 if(!current.length){const row=document.createElement('tr');const cell=textCell('No hay registros para la consulta.');cell.colSpan=fields.length+1;row.append(cell);$('rows').append(row)}
 $('counter').textContent=selected.length.toLocaleString('es-CL')+' registros encontrados en el bloque';
 $('page').textContent='Bloque '+(state.chunkIndex+1)+'/'+Math.max(state.parts.length,1)+' · Página '+(pages?state.page+1:0)+'/'+pages;
 $('prev').disabled=state.page===0&&state.chunkIndex===0;$('next').disabled=state.page+1>=pages&&state.chunkIndex>=state.parts.length-1;
}
let profileRequest=0;
function closeContextProfile(){
 profileRequest++;
 $('perfil-contextual').hidden=true;
 $('perfil-resumen').replaceChildren();
 $('perfil-columnas').replaceChildren();
 $('perfil-filas').replaceChildren();
}
async function showContextProfile(field,name){
 const seq=++profileRequest;
 const period=$('periodo').value,entity=$('entidad').value;
 const rows=state.records.filter(record=>String(record[field]??'').trim()===name);
 const link=$('perfil-ver-global');
 link.replaceChildren();
 const targets=field==='organismo_comprador'?[['procesos','Ver procesos del organismo']]:[['ofertas','Ver ofertas'],['resultados','Ver resultados informados'],['ordenescompra','Ver órdenes de compra']];
 for(const [target,label] of targets){
  const button=document.createElement('button');button.type='button';button.className='secondary';button.textContent=label;
  button.addEventListener('click',()=>{
   const words=(name.normalize('NFD').replace(/\p{M}/gu,'').match(/[a-z0-9]+/gi)||[]).filter(w=>w.length>=3);
   if(!words.length){status('No existen palabras de 3 caracteres suficientes para esta búsqueda.');return}
   $('entidad').value=target;$('entidad').dispatchEvent(new Event('change'));
   $('busqueda-global-texto').value=words.join(' ');
   $('global-estado').value='';$('global-modalidad').value='';
   $('busqueda-global-boton').click();
   $('busqueda-global').scrollIntoView({behavior:'smooth',block:'start'});
  });
  link.append(button);
 }

 const area=$('perfil-contextual'),header=$('perfil-resumen');
 $('perfil-titulo').textContent=(field==='organismo_comprador'?'Organismo comprador':'Proveedor')+' · '+name;
 header.replaceChildren();
 const p=document.createElement('p');
 p.textContent=rows.length.toLocaleString('es-CL')+' registro(s) de '+name+' encontrados en el bloque '+(state.chunkIndex+1)+' de '+state.parts.length+' del período '+period+'. Estos datos no representan el total del período.';
 header.append(p);
 const relevant=tableColumns[entity]?.slice(0,5)||[];
 const head=document.createElement('tr');
 let profileSort={key:null,direction:1};
 const tableBody=$('perfil-filas');
 function paintProfile(){
  head.replaceChildren();
  for(const [key,label] of relevant){
   const th=document.createElement('th'),button=document.createElement('button');button.type='button';button.className='sort-heading';
   button.textContent=label+(profileSort.key===key?(profileSort.direction===1?' ↑':' ↓'):' ⇅');
   button.addEventListener('click',()=>{profileSort.direction=profileSort.key===key?-profileSort.direction:1;profileSort.key=key;paintProfile()});
   th.append(button);head.append(th);
  }
  const body=document.createDocumentFragment();
  const sorted=profileSort.key?[...rows].sort((a,b)=>profileSort.direction*compareRows(a,b,profileSort.key)):rows;
  for(const record of sorted.slice(0,25)){
   const tr=document.createElement('tr');for(const [key] of relevant)tr.append(displayedCell(record,key));body.append(tr);
  }
  tableBody.replaceChildren(body);
 }
 $('perfil-columnas').replaceChildren(head);
 paintProfile();
 if(rows.length>25){const more=document.createElement('p');more.className='muted';more.textContent='Se muestran los primeros 25 registros del bloque.';header.append(more)}
 area.hidden=false;area.scrollIntoView({behavior:'smooth',block:'start'});
 const extra=document.createElement('p');extra.className='muted';
 extra.textContent='Consultando resumen del período…';header.prepend(extra);
 try{
  const normalized=name.normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().trim().replace(/\s+/g,' ');
  const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(normalized));
  const shard=Array.from(new Uint8Array(digest)).slice(0,1).map(v=>v.toString(16).padStart(2,'0')).join('');
  const location='data/perfiles/'+period+'/'+entity+'/'+shard+'.json';
  const summary=await readJsonPublic(location);
  if(seq!==profileRequest||$('periodo').value!==period||$('entidad').value!==entity)return;
  const item=summary[normalized];
  if(!item){extra.textContent='Sin resumen agregado publicado para este actor.';return}
  const total=Number(item.registros||0).toLocaleString('es-CL');
  const available=Number(item.registros_con_monto||0).toLocaleString('es-CL');
  const money=Number(item.monto_total_clp||0).toLocaleString('es-CL');
  extra.textContent='Resumen del período completo: '+total+' registros identificados; '+available+' con monto informado; suma de montos: $'+money+'. Son registros de '+entity+', no operaciones únicas ni adjudicaciones verificadas.';
 }catch(e){if(seq===profileRequest)extra.textContent='Resumen mensual aún no publicado. Se muestra únicamente el bloque consultado.'}
}
const FAVORITES_KEY='observatorio-favoritos-v2';
let favorites=[];
try{const saved=JSON.parse(localStorage.getItem(FAVORITES_KEY)||'[]');if(Array.isArray(saved))favorites=saved.slice(0,200)}catch{}
function favoriteKey(entity,period,record){return JSON.stringify([entity,period,record])}
function renderFavorites(){
 const box=$('favoritos-lista');box.replaceChildren();
 $('favoritos-estado').textContent=favorites.length+' favoritos guardados en este navegador.';
 for(const item of favorites){
  const line=document.createElement('div');line.className='favorite-item';
  const label=document.createElement('span');label.textContent=item.period+' · '+item.entity+' · '+item.label;
  const button=document.createElement('button');button.type='button';button.className='secondary';button.textContent='Eliminar';
  button.addEventListener('click',()=>{favorites=favorites.filter(x=>x.key!==item.key);persistFavorites();render();renderFavorites()});
  line.append(label,button);box.append(line);
 }
}
function persistFavorites(){try{localStorage.setItem(FAVORITES_KEY,JSON.stringify(favorites))}catch{$('favoritos-estado').textContent='No se pudo guardar en el navegador.'}}
function toggleFavorite(record){
 const entity=$('entidad').value,period=$('periodo').value,key=favoriteKey(entity,period,record);
 if(favorites.some(x=>x.key===key))favorites=favorites.filter(x=>x.key!==key);
 else{
  if(favorites.length>=200){status('Límite de 200 favoritos en este navegador.');return}
  favorites.push({key,entity,period,label:String(record.codigo_oc??record.codigo??record.nombre??'Registro'),record});
 }
 persistFavorites();renderFavorites();render();
}
function exportBlockCSV(){
 const rows=filteredBlock(),entity=$('entidad').value,period=$('periodo').value;
 if(!rows.length){status('No hay registros filtrados para exportar.');return}
 const keys=tableColumns[entity].map(([key])=>key);
 const escape=value=>'"'+String(value??'').replaceAll('"','""').replace(/^[=+@\-\t\r]/,x=>"'"+x)+'"';
 const csv='\uFEFF'+[keys.join(';'),...rows.map(row=>keys.map(k=>escape(row[k])).join(';'))].join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 const link=document.createElement('a');link.href=url;link.download='observatorio-v2-'+entity+'-'+period+'-bloque-'+(state.chunkIndex+1)+'.csv';
 document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
 status('CSV exportado: '+rows.length+' registros filtrados del bloque '+(state.chunkIndex+1)+'.');
}
function showDetail(record){
 const area=$('detalle'), body=$('detalle-campos');
 const summary=$('detalle-resumen');summary.replaceChildren();
 const entity=$('entidad').value;
 const priority={procesos:['codigo','nombre','organismo_comprador','estado','monto_disponible_clp'],
 ofertas:['codigo','proveedor','seleccionado','monto_ofertado_clp'],
 resultados:['codigo','adjudicatario','monto_adjudicado_clp'],
 ordenescompra:['codigo_oc','codigo_proceso','proveedor','estado','monto_total_oc_clp']}[entity]||[];
 for(const key of priority){
  const val=record[key];if(val===undefined||val===null||String(val).trim()==='')continue;
  const item=document.createElement('div');item.className='detail-highlight';
  const title=document.createElement('small');title.textContent=key.replaceAll('_',' ');
  const value=document.createElement('strong');
  if(codeField(key))value.append(displayedCell(record,key).firstChild);
  else value.textContent=moneyField(key)?moneyCLP(val):String(val);
  item.append(title,value);summary.append(item);
 }
 $('detalle-secundario').open=false;
 body.replaceChildren();
 for(const [key,value] of Object.entries(record)){
  if($('entidad').value==='resultados'&&['validado','estado_verificacion_oc'].includes(key))continue;
  const dt=document.createElement('dt');dt.textContent=key.replaceAll('_',' ');
  const dd=document.createElement('dd');
  const isOC=$('entidad').value==='ordenescompra';
  if(isOC&&key==='codigo_proceso'&&/^[a-z0-9-]{5,80}$/i.test(String(value??''))){
   const code=String(value).trim();
   const b=document.createElement('button');b.type='button';b.className='secondary detail-process-link';b.textContent='Ver proceso '+code+' en el Observatorio';
   b.addEventListener('click',()=>{
    $('entidad').value='procesos';$('entidad').dispatchEvent(new Event('change'));
    $('busqueda-global-texto').value=code;
    $('global-estado').value='';$('global-modalidad').value='';
    $('busqueda-global-boton').click();
    $('busqueda-global').scrollIntoView({behavior:'smooth',block:'start'});
   });
   dd.append(b);
   // La ruta de fichaLicitacion solo es apropiada para códigos de licitación,
   // no para toda Compra Ágil ni para cualquier OC.
   if(/-([A-Z]{2}\d{0,2})$/i.test(code)&&!/-COT\d+$/i.test(code)){
    const a=document.createElement('a');a.href='https://www.mercadopublico.cl/fichaLicitacion.html?idLicitacion='+encodeURIComponent(code);
    a.target='_blank';a.rel='noopener noreferrer';a.textContent='Abrir ficha de licitación';a.className='detail-official-link';
    dd.append(' ',a);
   }
  }else if(codeField(key)&&value)dd.append(displayedCell(record,key).firstChild);else dd.textContent=moneyField(key)?moneyCLP(value):formatTableValue(record,key);
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
function closeDetail(){detailRequest++;$('detalle-resumen').replaceChildren();$('detalle').hidden=true;$('detalle-campos').replaceChildren();$('detalle-relaciones').hidden=true;}


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
  kind==='resultados'?['adjudicatario','monto_adjudicado_clp','monto_oferta_seleccionada_clp']:
  ['codigo_oc','proveedor','monto_total_oc_clp','estado'];
 let relatedSort={key:null,direction:1};
 for(const col of fields){const th=document.createElement('th');const button=document.createElement('button');button.type='button';button.className='sort-heading';button.textContent=col.replaceAll('_',' ')+' ⇅';button.addEventListener('click',()=>{relatedSort.direction=relatedSort.key===col?-relatedSort.direction:1;relatedSort.key=col;page=0;draw()});th.append(button);head.append(th)}
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
  const orderedItems=relatedSort.key?[...items].sort((a,b)=>relatedSort.direction*compareRows(a,b,relatedSort.key)):items;
  for(const item of orderedItems.slice(page*perPage,(page+1)*perPage)){
   const tr=document.createElement('tr');
   for(const field of fields)tr.append(displayedCell(item,field));
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
  state.chunkIndex=index;state.records=rows;state.page=0;closeContextProfile();refreshLocalFilters();render();
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
 ++state.token;state.cache.clear();state.parts=parts;state.total=info.conteos?.[entity]??0;state.records=[];state.page=0;refreshLocalFilters();closeDetail();closeContextProfile();render();
 $('stat-registros').textContent=Number(state.total).toLocaleString('es-CL');
 $('consultar').disabled=false;
 if(!parts.length){status('La entidad está publicada, pero no registra filas en este período.');return}
 await loadChunk(0);
}

function renderMonthlyEvolution(){
 const container=$('evolucion-barras');container.replaceChildren();
 if(!state.manifest)return;
 const entity=$('entidad').value;
 const items=state.manifest.periodos.map(p=>({period:p.periodo,n:Number(p.conteos?.[entity]||0)}));
 const max=Math.max(1,...items.map(p=>p.n));
 const summary=$('evolucion-resumen');summary.replaceChildren();
 const total=items.reduce((a,b)=>a+b.n,0);
 const complete=items.filter(x=>x.period<'2026-10');
 const average=complete.length?Math.round(complete.reduce((a,b)=>a+b.n,0)/complete.length):0;
 const latestComplete=complete.at(-1),before=complete.at(-2);
 const change=latestComplete&&before&&before.n?((latestComplete.n/before.n-1)*100).toFixed(1)+' %':'—';
 for(const [label,value] of [['Registros publicados',total.toLocaleString('es-CL')],['Promedio mensual jun–sep',average.toLocaleString('es-CL')],['Variación último mes completo',change],['Mes más reciente',items.at(-1)?.period||'—']]){
  const box=document.createElement('div');box.className='evolution-metric';
  const small=document.createElement('small');small.textContent=label;
  const strong=document.createElement('strong');strong.textContent=value;box.append(small,strong);summary.append(box);
 }
 for(const item of items){
  const row=document.createElement('div');row.className='evolution-row';
  const label=document.createElement('span');label.textContent=item.period;
  const track=document.createElement('div');track.className='evolution-track';
  const bar=document.createElement('div');bar.className='evolution-fill';bar.style.width=(item.n/max*100).toFixed(1)+'%';
  track.append(bar);
  const count=document.createElement('strong');count.textContent=item.n.toLocaleString('es-CL');
  const delta=document.createElement('span');const previous=items[items.indexOf(item)-1];delta.textContent=previous?.n?((item.n/previous.n-1)*100).toFixed(1)+' %':'—';row.append(label,track,count,delta);container.append(row);
 }
}
async function init(){
 try{
  const response=await fetch('./data/catalogo-publico.json',{cache:'no-store'});
  if(!response.ok)throw Error('Catálogo público v2 no disponible');
  const payload=await response.json();
  if(!Array.isArray(payload.periodos))throw Error('Catálogo incompatible');
  state.manifest=payload;
  renderMonthlyEvolution();
  for(const item of payload.periodos){
   if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(item.periodo))continue;
   const option=document.createElement('option');option.value=item.periodo;option.textContent=item.periodo+' · '+(item.tipo==='historico'?'Histórico':'Operativo');$('periodo').append(option)
  }
  const date=new Date(payload.fecha_publicacion);$('stat-fecha').textContent=Number.isNaN(date.getTime())?(payload.fecha_publicacion||'Pendiente'):new Intl.DateTimeFormat('es-CL',{timeZone:'America/Santiago',dateStyle:'long',timeStyle:'short'}).format(date)+' (Chile)';
  $('consultar').disabled=payload.periodos.length===0;
  status(payload.periodos.length?'Seleccione un período y una entidad.':'Frontend v2 preparado. Aún no se han publicado extractos MER v2; la versión 1 sigue disponible.');
 }catch(e){status('Catálogo v2 todavía no publicado: '+e.message)}
}
$('periodo').addEventListener('change',()=>{$('stat-periodo').textContent=$('periodo').value||'—';++state.token;state.records=[];state.parts=[];state.chunkIndex=0;state.cache.clear();state.page=0;refreshLocalFilters();closeDetail();render()});
$('detalle-cerrar').addEventListener('click',closeDetail);
$('exportar-csv').addEventListener('click',exportBlockCSV);
renderFavorites();
$('perfil-cerrar').addEventListener('click',closeContextProfile);
$('buscar').addEventListener('input',()=>{state.page=0;render()});
for(const id of ['filtro-estado','filtro-modalidad'])$(id).addEventListener('change',()=>{state.page=0;render()});
$('limpiar-filtros').addEventListener('click',()=>{$('buscar').value='';$('filtro-estado').value='';$('filtro-modalidad').value='';state.page=0;render()});
$('consultar').addEventListener('click',consult);
$('entidad').addEventListener('change',()=>{renderMonthlyEvolution();++state.token;state.records=[];state.parts=[];state.chunkIndex=0;state.cache.clear();state.page=0;closeDetail();closeContextProfile();render()});
$('prev').addEventListener('click',()=>{if(state.page===0&&state.chunkIndex>0)loadChunk(state.chunkIndex-1);else{state.page--;render()}});
$('next').addEventListener('click',()=>{const count=filteredBlock().length;if((state.page+1)*state.perPage>=count&&state.chunkIndex<state.parts.length-1)loadChunk(state.chunkIndex+1);else{state.page++;render()}});
// API mínima para abrir resultados indexados sin duplicar el lector de fragmentos.
window.openIndexedRecord=async function(part,row,period,entity){
 if($('periodo').value!==period||$('entidad').value!==entity){
  status('El período o la entidad cambiaron. Ejecute nuevamente la búsqueda.');
  return;
 }
 if(!Number.isInteger(part)||part<0||!Number.isInteger(row)||row<0)return;
 if(!state.parts.length)await consult();
 if(part>=state.parts.length)return;
 const token=state.token;
 await loadChunk(part);
 if(token===state.token&&state.chunkIndex===part&&state.records[row])showDetail(state.records[row]);
};
init();
