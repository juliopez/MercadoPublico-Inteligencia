// MER v2: carga selectiva por período. No consulta Google Sheets desde el navegador.
const $=id=>document.getElementById(id);
const allowed=['procesos','ofertas','resultados','ordenescompra'];
const state={manifest:null,records:[],page:0,perPage:25,token:0};
function status(message){$('status').textContent=message}
function safePart(path,period,entity){return typeof path==='string'&&new RegExp('^data/partes/'+entity+'/'+period+'/[a-z0-9_-]+\\.json$').test(path)}
function textCell(value){const td=document.createElement('td');td.textContent=String(value??'');return td}
function render(){
 const term=$('buscar').value.trim().toLocaleLowerCase('es');
 const selected=state.records.filter(r=>!term||Object.values(r).some(v=>String(v??'').toLocaleLowerCase('es').includes(term)));
 const pages=Math.ceil(selected.length/state.perPage);state.page=Math.min(state.page,Math.max(0,pages-1));
 const current=selected.slice(state.page*state.perPage,(state.page+1)*state.perPage);
 const fields=current.length?Object.keys(current[0]).slice(0,16):[];
 $('columns').replaceChildren();const tr=document.createElement('tr');
 for(const f of fields){const th=document.createElement('th');th.textContent=f;tr.append(th)}
 if(!fields.length){const th=document.createElement('th');th.textContent='Resultados';tr.append(th)}
 $('columns').append(tr);$('rows').replaceChildren();
 for(const record of current){const row=document.createElement('tr');for(const f of fields)row.append(textCell(record[f]));$('rows').append(row)}
 if(!current.length){const row=document.createElement('tr');row.append(textCell('No hay registros para la consulta.'));$('rows').append(row)}
 $('counter').textContent=selected.length.toLocaleString('es-CL')+' registros encontrados';
 $('page').textContent='Página '+(pages?state.page+1:0)+' de '+pages;
 $('prev').disabled=state.page===0;$('next').disabled=state.page+1>=pages;
}
async function consult(){
 const period=$('periodo').value, entity=$('entidad').value, token=++state.token;
 if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(period)||!allowed.includes(entity))return;
 const info=state.manifest.periodos.find(p=>p.periodo===period);
 const parts=info?.partes?.[entity];if(!Array.isArray(parts)){status('Entidad no publicada para este período.');return}
 $('consultar').disabled=true;state.records=[];state.page=0;render();
 try{
  const all=[];for(const path of parts){
   if(!safePart(path,period,entity))throw Error('Ruta JSON no permitida');
   const response=await fetch('../'+path,{cache:'no-store'});
   if(!response.ok)throw Error('No se pudo leer el fragmento de '+period);
   const rows=await response.json();if(!Array.isArray(rows))throw Error('Formato incorrecto');
   if(token!==state.token)return;
   all.push(...rows);status('Cargando '+all.length.toLocaleString('es-CL')+' registros…');
  }
  if(token!==state.token)return;
  if(Number.isSafeInteger(info?.conteos?.[entity])&&all.length!==info.conteos[entity])throw Error('Conteo no coincide');
  state.records=all;state.page=0;render();status('Consulta cargada: '+period+' · '+entity);
 }catch(e){state.records=[];render();status('No se pudo completar la consulta: '+e.message)}
 finally{if(token===state.token)$('consultar').disabled=false}
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
$('periodo').addEventListener('change',()=>{$('stat-periodo').textContent=$('periodo').value||'—';++state.token;state.records=[];state.page=0;render()});
$('buscar').addEventListener('input',()=>{state.page=0;render()});
$('consultar').addEventListener('click',consult);
$('prev').addEventListener('click',()=>{state.page--;render()});
$('next').addEventListener('click',()=>{state.page++;render()});
init();