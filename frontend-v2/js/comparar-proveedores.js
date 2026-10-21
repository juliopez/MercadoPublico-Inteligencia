// Comparación basada exclusivamente en agregados públicos por mes y entidad.
const byId=id=>document.getElementById(id);
let comparisonSeq=0;
const kinds=[['ofertas','Ofertas'],['resultados','Resultados informados'],['ordenescompra','Órdenes de compra']];
function canonical(value){return String(value||'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().trim().replace(/\s+/g,' ')}
async function profile(period,kind,name){
 const key=canonical(name);
 const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(key));
 const group=new Uint8Array(digest)[0].toString(16).padStart(2,'0');
 const path='data/perfiles/'+period+'/'+kind+'/'+group+'.json';
 const response=await fetch('./'+path,{cache:'no-store'});
 if(response.status===404)return null;
 if(!response.ok)throw Error('HTTP '+response.status+' al leer '+kind);
 const records=await response.json();
 return records[key]||null;
}
function cell(value){const td=document.createElement('td');td.textContent=String(value);return td}
function formatMoney(n){return '$'+Math.round(Number(n)||0).toLocaleString('es-CL')}
function clear(message){
 comparisonSeq++;
 byId('comparar-cabecera').replaceChildren();byId('comparar-cuerpo').replaceChildren();
 byId('comparar-estado').textContent=message;
}
async function compare(){
 const seq=++comparisonSeq,period=byId('periodo').value;
 const names=[1,2,3].map(i=>byId('comparar-nombre-'+i).value.trim()).filter(Boolean);
 const keys=names.map(canonical);
 if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(period)){clear('Seleccione primero un período.');return}
 if(names.length<2||names.length>3||keys.some(k=>!k)||new Set(keys).size!==keys.length){clear('Ingrese dos o tres proveedores distintos.');return}
 byId('comparar-estado').textContent='Consultando agregados mensuales…';
 byId('comparar-ejecutar').disabled=true;
 try{
  const values=await Promise.all(names.map(async n=>Promise.all(kinds.map(async ([kind])=>profile(period,kind,n)))));
  if(seq!==comparisonSeq||byId('periodo').value!==period)return;
  const head=document.createElement('tr');head.append(cell('Indicador'));
  for(const name of names){const th=document.createElement('th');th.textContent=name;head.append(th)}
  const body=document.createDocumentFragment();
  for(let i=0;i<kinds.length;i++){
   for(const [metric,title,format] of [
    ['registros',kinds[i][1]+' · registros',v=>Number(v||0).toLocaleString('es-CL')],
    ['registros_con_monto',kinds[i][1]+' · con monto informado',v=>Number(v||0).toLocaleString('es-CL')],
    ['monto_total_clp',kinds[i][1]+' · suma de montos',formatMoney]
   ]){
    const row=document.createElement('tr');row.append(cell(title));
    for(const arr of values)row.append(cell(arr[i]?format(arr[i][metric]):'Sin registros identificados'));
    body.append(row);
   }
  }
  byId('comparar-cabecera').replaceChildren(head);byId('comparar-cuerpo').replaceChildren(body);
  byId('comparar-estado').textContent='Comparación de '+names.length+' proveedores · '+period+'. Coincidencia por nombre normalizado; variaciones de razón social pueden figurar separadas.';
 }catch(error){
  if(seq===comparisonSeq)byId('comparar-estado').textContent='Error al consultar agregados: '+error.message+'. Intente nuevamente.';
 }finally{
  if(seq===comparisonSeq)byId('comparar-ejecutar').disabled=false;
 }
}
byId('comparar-ejecutar').addEventListener('click',compare);
byId('periodo').addEventListener('change',()=>clear('El período cambió. Ejecute nuevamente la comparación.'));

let suggestionSeq=0, suggestionTimer;
const suggestionCache=new Map();
async function suggest(input){
 const seq=++suggestionSeq,period=byId('periodo').value;
 const term=canonical(input.value);
 const list=byId('comparar-sugerencias');
 list.replaceChildren();
 if(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(period)||term.length<2)return;
 const prefix=term.slice(0,2);
 const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(prefix));
 const shard=new Uint8Array(digest)[0].toString(16).padStart(2,'0');
 const cacheKey=period+'/'+shard;
 try{
  let entries=suggestionCache.get(cacheKey);
  if(!entries){
   const response=await fetch('./data/autocompletar/'+cacheKey+'.json');
   if(response.status===404){byId('comparar-ayuda').textContent='Las sugerencias no están publicadas para este período. Puedes escribir el nombre manualmente.';return}
   if(!response.ok)throw Error('HTTP '+response.status);
   entries=await response.json();
   if(!Array.isArray(entries))throw Error('Formato inválido');
   suggestionCache.set(cacheKey,entries);
   if(suggestionCache.size>12)suggestionCache.delete(suggestionCache.keys().next().value);
  }
  if(seq!==suggestionSeq||byId('periodo').value!==period)return;
  const matching=entries.filter(([key])=>key.startsWith(term)).slice(0,40);
  for(const [,name] of matching){const option=document.createElement('option');option.value=name;list.append(option)}
  byId('comparar-ayuda').textContent=matching.length+' sugerencias de proveedores para el texto ingresado. Selecciona una razón social completa.';
 }catch(error){if(seq===suggestionSeq)byId('comparar-ayuda').textContent='No fue posible consultar sugerencias. Puedes ingresar el nombre manualmente.'}
}
for(const n of [1,2,3]){
 byId('comparar-nombre-'+n).addEventListener('input',event=>{
  clearTimeout(suggestionTimer);
  suggestionTimer=setTimeout(()=>suggest(event.target),200);
 });
}
byId('periodo').addEventListener('change',()=>{
 suggestionSeq++;byId('comparar-sugerencias').replaceChildren();
 byId('comparar-ayuda').textContent='Escribe al menos dos letras iniciales para ver proveedores del nuevo período.';
});
