// Sugerencias opcionales: jamás bloquean la búsqueda global ni consultan Sheets.
const $suggest=id=>document.getElementById(id);
const indexes={texto:'busqueda-global-texto',estado:'global-estado',modalidad:'global-modalidad'};
const stores={texto:'global-sugerencias-texto',estado:'global-sugerencias-estado',modalidad:'global-sugerencias-modalidad'};
const cache=new Map();
let version=0;
const normalize=s=>String(s||'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
function setOptions(kind,options){
 const list=$suggest(stores[kind]);list.replaceChildren();
 for(const word of options.slice(0,30)){const option=document.createElement('option');option.value=word;list.append(option)}
}
async function load(path){
 const urls=['./'+path,'https://raw.githubusercontent.com/juliopez/MercadoPublico-Inteligencia/main/frontend-v2/'+path];
 let last;
 for(const url of urls){
  try{const response=await fetch(url,{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);return await response.json()}catch(e){last=e}
 }
 throw last;
}
async function update(kind){
 const token=++version,period=$suggest('periodo').value,entity=$suggest('entidad').value;
 if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(period))return;
 const path='data/sugerencias/'+period+'/'+entity+'/';
 const raw=$suggest(indexes[kind]).value;
 const term=normalize(raw).trim();
 if(kind==='texto'){
  const words=term.match(/[a-z0-9]+/g)||[];
  const last=words.at(-1)||'';
  if(last.length<2){setOptions(kind,[]);return}
  const group=last.slice(0,2),key=path+group+'.json';
  try{
   if(!cache.has(key))cache.set(key,await load(key));
   if(token!==version)return;
   const matches=cache.get(key).filter(w=>w.startsWith(last));
   const head=raw.slice(0,raw.length-last.length);
   setOptions(kind,matches.map(w=>head+w));
  }catch{if(token===version)$suggest('global-sugerencias-ayuda').textContent='Sugerencias de palabras temporalmente no disponibles; puedes seguir escribiendo.'}
  return;
 }
 const key=path+'facetas.json';
 try{
  if(!cache.has(key))cache.set(key,await load(key));
  if(token!==version)return;
  const values=cache.get(key)[kind]||[];
  setOptions(kind,values.filter(v=>normalize(v).includes(term)));
 }catch{if(token===version)$suggest('global-sugerencias-ayuda').textContent='Sugerencias de filtros temporalmente no disponibles; los filtros manuales siguen funcionando.'}
}
let timer;
for(const [kind,id] of Object.entries(indexes)){
 $suggest(id).addEventListener('input',()=>{
  clearTimeout(timer);timer=setTimeout(()=>update(kind),180);
 });
 $suggest(id).addEventListener('focus',()=>{if(kind!=='texto')update(kind)});
}
for(const id of ['periodo','entidad'])$suggest(id).addEventListener('change',()=>{
 version++;clearTimeout(timer);
 Object.keys(stores).forEach(kind=>setOptions(kind,[]));
 $suggest('global-sugerencias-ayuda').textContent='Sugerencias según el período y la entidad seleccionados.';
});
