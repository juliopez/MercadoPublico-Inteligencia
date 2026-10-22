// Autocompletado y listas de facetas V2 basados exclusivamente en índices públicos.
// No consulta Google Sheets ni la API ChileCompra.
const $suggest=id=>document.getElementById(id);
const cache=new Map();
const normalize=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
let revision=0,timer;
async function load(path){
 if(!/^data\/(sugerencias|catalogo-publico)[a-z0-9_\/.-]*\.json$/.test(path))throw Error('Ruta de sugerencia no admitida');
 if(cache.has(path))return cache.get(path);
 const p=(async()=>{
  let error;
  for(const url of ['./'+path,'https://raw.githubusercontent.com/juliopez/MercadoPublico-Inteligencia/main/frontend-v2/'+path]){
   try{const r=await fetch(url);if(!r.ok)throw Error('HTTP '+r.status);return await r.json()}catch(e){error=e}
  }
  throw error;
 })();
 cache.set(path,p);
 try{return await p}catch(e){cache.delete(path);throw e}
}
async function periods(){
 const scope=$suggest('busqueda-global-alcance').value;
 if(scope==='mes'){
  const p=$suggest('periodo').value;
  return /^20\d{2}-(0[1-9]|1[0-2])$/.test(p)?[p]:[];
 }
 const catalog=await load('data/catalogo-publico.json');
 return [...new Set((catalog.periodos||[]).map(p=>p.periodo).filter(p=>/^20\d{2}-(0[1-9]|1[0-2])$/.test(p)))];
}
function options(select,values,emptyLabel){
 const selected=select.value;
 select.replaceChildren(new Option(emptyLabel,''));
 for(const value of values){
  if(!value||typeof value!=='string')continue;
  select.add(new Option(value,value));
 }
 if(values.includes(selected))select.value=selected;
}
async function facets(){
 const token=++revision,entity=$suggest('entidad').value;
 const status=$suggest('global-estado'),type=$suggest('global-modalidad');
 const [useStatus,useType]=({procesos:[true,true],ofertas:[true,false],resultados:[false,false],ordenescompra:[true,true]}[entity]||[false,false]);
 status.disabled=!useStatus;type.disabled=!useType;
 options(status,[],'Todos los estados');options(type,[],'Todas las modalidades');
 if(!useStatus&&!useType)return;
 try{
  const months=await periods();
  const results=await Promise.allSettled(months.map(month=>load('data/sugerencias/'+month+'/'+entity+'/facetas.json')));
  if(token!==revision)return;
  const states=new Set(),modes=new Set();
  for(const result of results)if(result.status==='fulfilled'){
   if(useStatus)for(const s of result.value.estado||[])states.add(s);
   // Compatibilidad con índices antiguos que usan nombres 'estado' o 'modalidad'.
   if(useStatus)for(const s of result.value.status||[])states.add(s);
   if(useType)for(const s of result.value.modalidad||[])modes.add(s);
   if(useType)for(const s of result.value.tipo||[])modes.add(s);
  }
  const sorted=set=>[...set].filter(s=>typeof s==='string'&&s.trim()).sort((a,b)=>a.localeCompare(b,'es',{sensitivity:'base'}));
  if(useStatus)options(status,sorted(states),'Todos los estados');
  if(useType)options(type,sorted(modes),'Todas las modalidades');
  if(results.length&&results.every(x=>x.status==='rejected'))$suggest('global-sugerencias-ayuda').textContent='Las listas no están disponibles para esta cobertura. Puedes buscar usando palabras clave.';
 }catch(e){if(token===revision)$suggest('global-sugerencias-ayuda').textContent='No fue posible cargar los filtros. Puedes buscar usando palabras clave.'}
}
async function suggestWords(){
 const token=++revision;
 const raw=$suggest('busqueda-global-texto').value;
 const word=(normalize(raw).match(/[a-z0-9]+/g)||[]).at(-1)||'';
 const list=$suggest('global-sugerencias-texto');list.replaceChildren();
 if(word.length<2)return;
 try{
  const months=await periods(),entity=$suggest('entidad').value;
  const group=word.slice(0,2);
  const results=await Promise.allSettled(months.map(month=>load('data/sugerencias/'+month+'/'+entity+'/'+group+'.json')));
  if(token!==revision)return;
  const values=new Set();
  for(const result of results)if(result.status==='fulfilled'&&Array.isArray(result.value))
   for(const w of result.value)if(typeof w==='string'&&normalize(w).startsWith(word))values.add(w);
  const head=raw.slice(0,raw.length-word.length);
  for(const word of [...values].sort((a,b)=>a.localeCompare(b,'es',{sensitivity:'base'})).slice(0,30)){
   const option=document.createElement('option');option.value=head+word;list.append(option);
  }
 }catch(e){if(token===revision)$suggest('global-sugerencias-ayuda').textContent='Sugerencias temporalmente no disponibles; puedes continuar buscando.'}
}
$suggest('busqueda-global-texto').addEventListener('input',()=>{
 clearTimeout(timer);timer=setTimeout(suggestWords,180);
});
for(const id of ['periodo','entidad','busqueda-global-alcance'])$suggest(id).addEventListener('change',()=>{
 revision++;clearTimeout(timer);$suggest('global-sugerencias-texto').replaceChildren();
 $suggest('global-sugerencias-ayuda').textContent='Escribe al menos 2 letras para obtener sugerencias. Estado y Modalidad se cargan según la cobertura.';
 facets();
});
facets();
