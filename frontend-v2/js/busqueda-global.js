// Búsqueda global V2 independiente: no sustituye ni modifica la carga por bloques de app.js.
const el=id=>document.getElementById(id);
let request=0, references=[], page=0, context=null;
const columns={
 procesos:[['codigo','Código'],['nombre','Proceso'],['organismo_comprador','Organismo'],['estado','Estado']],
 ofertas:[['codigo','Proceso'],['proveedor','Proveedor'],['monto_ofertado_clp','Monto CLP']],
 resultados:[['codigo','Proceso'],['adjudicatario','Proveedor informado'],['validado','Verificación']],
 ordenescompra:[['codigo_oc','Orden de compra'],['codigo_proceso','Proceso'],['proveedor','Proveedor']]
};
function normalize(s){return String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
async function read(path){
 if(!/^data\/(busqueda|partes)\/[a-z0-9_\/-]+\.json$/.test(path))throw Error('Ruta no permitida');
 let last;
 for(const url of ['./'+path,'https://raw.githubusercontent.com/juliopez/MercadoPublico-Inteligencia/main/frontend-v2/'+path]){
  try{const response=await fetch(url);if(!response.ok)throw Error('HTTP '+response.status);return await response.json()}catch(e){last=e}
 }
 throw last;
}
function reset(message){
 request++;references=[];page=0;context=null;
 el('busqueda-global-filas').replaceChildren();el('busqueda-global-columnas').replaceChildren();
 el('busqueda-global-anterior').disabled=true;el('busqueda-global-siguiente').disabled=true;
 el('busqueda-global-pagina').textContent='Sin resultados';
 el('busqueda-global-estado').textContent=message;
}
async function paint(seq){
 if(!context||seq!==request)return;
 const {period,entity,parts}=context;
 const start=page*10,refs=references.slice(start,start+10);
 el('busqueda-global-estado').textContent='Cargando resultados indexados…';
 try{
  const chunks=new Map();
  for(const [part] of refs){
   if(!Number.isInteger(part)||part<0||part>=parts.length)throw Error('Referencia de fragmento inválida');
   if(!chunks.has(part)){
    const rows=await read(parts[part]);
    if(!Array.isArray(rows))throw Error('Fragmento no válido');
    chunks.set(part,rows);
   }
  }
  if(seq!==request||el('periodo').value!==period||el('entidad').value!==entity)return;
  const head=document.createElement('tr'),body=document.createDocumentFragment();
  const fields=columns[entity];
  for(const [,label] of fields){const th=document.createElement('th');th.textContent=label;head.append(th)}
  const action=document.createElement('th');action.textContent='Acción';head.append(action);
  for(const [part,index] of refs){
   const rowData=chunks.get(part)?.[index];if(!rowData)throw Error('Fila referenciada ausente');
   const tr=document.createElement('tr');
   for(const [key] of fields){const td=document.createElement('td');td.textContent=String(rowData[key]??'')||'No informado';tr.append(td)}
   const td=document.createElement('td'),button=document.createElement('button');
   button.textContent='Ver registro en bloque';
   button.addEventListener('click',()=>{
    // Navega a la consulta original sin sustituir su modelo de carga.
    reset('Abra el detalle del registro desde el bloque indicado.');
    el('buscar').value=String(rowData.codigo??rowData.codigo_oc??'');
    el('filtro-estado').value='';el('filtro-modalidad').value='';
    document.getElementById('resultados').scrollIntoView({behavior:'smooth'});
    el('busqueda-global-estado').textContent='Referencia: bloque '+(part+1)+'. Pulse Consultar y navegue a ese bloque para ver la ficha.';
   });
   td.append(button);tr.append(td);body.append(tr);
  }
  el('busqueda-global-columnas').replaceChildren(head);
  el('busqueda-global-filas').replaceChildren(body);
  el('busqueda-global-pagina').textContent='Página '+(page+1)+' de '+Math.ceil(references.length/10);
  el('busqueda-global-anterior').disabled=page===0;
  el('busqueda-global-siguiente').disabled=start+10>=references.length;
  el('busqueda-global-estado').textContent=references.length.toLocaleString('es-CL')+' coincidencias indexadas · '+period+' · '+entity+'.';
 }catch(error){if(seq===request)el('busqueda-global-estado').textContent='Error al leer resultados: '+error.message}
}
async function search(){
 const seq=++request;references=[];page=0;context=null;
 const period=el('periodo').value,entity=el('entidad').value;
 const query=normalize(el('busqueda-global-texto').value).trim();
 const tokens=[...new Set(query.match(/[a-z0-9]+/g)||[])];
 if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(period)||!columns[entity]){reset('Seleccione un período y una entidad.');return}
 if(!tokens.length||tokens.some(t=>t.length<3)){reset('Escriba palabras de al menos 3 caracteres.');return}
 const info=Array.isArray(window.__unused)?null:null; // No depende del estado interno de app.js.
 el('busqueda-global-estado').textContent='Consultando índice público…';
 try{
  const catalogue=await read('data/busqueda/'+period+'/'+entity+'/meta.json');
  if(seq!==request)return;
  if(catalogue.version!==3||catalogue.periodo!==period||catalogue.entidad!==entity)throw Error('Índice incompatible');
  const source=await (await fetch('./data/catalogo-publico.json')).json();
  const parts=source.periodos?.find(x=>x.periodo===period)?.partes?.[entity];
  if(!Array.isArray(parts)||parts.length!==catalogue.fragmentos)throw Error('Índice desactualizado');
  const keys=[...new Set(tokens.map(t=>t.slice(0,2)))];
  const groups=new Map();
  for(const key of keys){groups.set(key,await read('data/busqueda/'+period+'/'+entity+'/'+key+'.json'));if(seq!==request)return}
  const lists=tokens.map(token=>groups.get(token.slice(0,2))?.[token.slice(0,3)]||[]);
  lists.sort((a,b)=>a.length-b.length);
  if(!lists.length||!lists[0].length){references=[]}else{
   const sets=lists.slice(1).map(a=>new Set(a.map(r=>r.join(':'))));
   references=lists[0].filter(r=>sets.every(set=>set.has(r.join(':'))));
  }
  // Seguridad del cliente: no descargar más de 10 filas de resultados por página.
  context={period,entity,parts};page=0;
  if(!references.length){el('busqueda-global-filas').replaceChildren();el('busqueda-global-columnas').replaceChildren();el('busqueda-global-pagina').textContent='Sin resultados';el('busqueda-global-estado').textContent='Sin coincidencias en el índice del período.';return}
  await paint(seq);
 }catch(error){if(seq===request)reset('Índice no disponible o consulta fallida: '+error.message+'. La búsqueda por bloque sigue disponible.')}
}
el('busqueda-global-boton').addEventListener('click',search);
el('busqueda-global-texto').addEventListener('keydown',e=>{if(e.key==='Enter')search()});
el('busqueda-global-anterior').addEventListener('click',()=>{if(page>0){page--;paint(request)}});
el('busqueda-global-siguiente').addEventListener('click',()=>{if((page+1)*10<references.length){page++;paint(request)}});
for(const id of ['periodo','entidad'])el(id).addEventListener('change',()=>reset('Seleccione Buscar en el período para ejecutar una nueva consulta.'));
