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
  // Ordena las filas del cuadro comparativo por indicador o valor mostrado.
  const headers=[...head.children],labels=headers.map(th=>th.textContent),tbody=byId('comparar-cuerpo');let activeSort=null,direction=1;
  headers.forEach((th,index)=>{
   const text=th.textContent;
   const button=document.createElement('button');button.type='button';button.className='sort-heading';button.textContent=text+' ⇅';
   button.addEventListener('click',()=>{
    direction=activeSort===index?-direction:1;activeSort=index;
    const sorted=[...tbody.children].sort((a,b)=>{
     const v=node=>node.children[index]?.textContent??'';
     const numeric=node=>Number(v(node).replace(/[^0-9,-]/g,'').replaceAll('.','').replace(',','.'));
     const na=numeric(a),nb=numeric(b);
     return direction*(index>0&&Number.isFinite(na)&&Number.isFinite(nb)?na-nb:v(a).localeCompare(v(b),'es',{numeric:true}));
    });
    tbody.replaceChildren(...sorted);
    headers.forEach((other,j)=>{const control=other.firstChild;if(control)control.textContent=labels[j]+(j===index?(direction===1?' ↑':' ↓'):' ⇅')});
   });
   th.replaceChildren(button);
  });
  byId('comparar-estado').textContent='Comparación de '+names.length+' proveedores · '+period+'. Coincidencia por nombre normalizado; variaciones de razón social pueden figurar separadas.';
 }catch(error){
  if(seq===comparisonSeq)byId('comparar-estado').textContent='Error al consultar agregados: '+error.message+'. Intente nuevamente.';
 }finally{
  if(seq===comparisonSeq)byId('comparar-ejecutar').disabled=false;
 }
}
byId('comparar-ejecutar').addEventListener('click',compare);
byId('periodo').addEventListener('change',()=>clear('El período cambió. Ejecute nuevamente la comparación.'));

let suggestionSeq=0;
const suggestionTimers=new Map(),suggestionCache=new Map();
let cachedPeriods=null;
async function suggestionPeriods(){
 if(cachedPeriods)return cachedPeriods;
 const response=await fetch('./data/catalogo-publico.json',{cache:'no-store'});
 if(!response.ok)throw Error('Catálogo HTTP '+response.status);
 const catalog=await response.json();
 const available=[...new Set((catalog.periodos||[]).map(x=>x.periodo).filter(x=>/^20\d{2}-(0[1-9]|1[0-2])$/.test(x)))];
 cachedPeriods=available;
 return available;
}
async function suggestionShard(period,shard){
 const key=period+'/'+shard;
 if(!suggestionCache.has(key)){
  const task=(async()=>{
   const response=await fetch('./data/autocompletar/'+key+'.json',{cache:'no-store'});
   if(response.status===404)return [];
   if(!response.ok)throw Error('Índice '+period+' HTTP '+response.status);
   const entries=await response.json();
   if(!Array.isArray(entries))throw Error('Índice de proveedores inválido');
   return entries;
  })();
  suggestionCache.set(key,task);
  if(suggestionCache.size>35)suggestionCache.delete(suggestionCache.keys().next().value);
  task.catch(()=>{if(suggestionCache.get(key)===task)suggestionCache.delete(key)});
 }
 return suggestionCache.get(key);
}
async function suggest(input){
 const seq=++suggestionSeq,term=canonical(input.value),list=byId('comparar-sugerencias');
 list.replaceChildren();
 if(term.length<2)return;
 const period=byId('periodo').value;
 const prefix=term.slice(0,2);
 const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(prefix));
 const shard=new Uint8Array(digest)[0].toString(16).padStart(2,'0');
 try{
  const periods= /^20\d{2}-(0[1-9]|1[0-2])$/.test(period)?[period]:await suggestionPeriods();
  const results=await Promise.allSettled(periods.map(p=>suggestionShard(p,shard)));
  if(seq!==suggestionSeq||!input.matches(':focus'))return;
  const names=new Map();
  for(const result of results){
   if(result.status!=='fulfilled')continue;
   for(const entry of result.value){
    if(!Array.isArray(entry)||entry.length<2)continue;
    const [key,name]=entry;
    if(typeof key==='string'&&typeof name==='string'&&key.startsWith(term)&&!names.has(key))names.set(key,name);
   }
  }
  for(const name of [...names.values()].sort((a,b)=>a.localeCompare(b,'es',{sensitivity:'base'})).slice(0,40)){
   const option=document.createElement('option');option.value=name;list.append(option);
  }
  const missing=results.filter(x=>x.status==='rejected').length;
  byId('comparar-ayuda').textContent=names.size?
   names.size+' proveedores coincidentes en '+periods.length+' período(s). Selecciona el nombre completo; la comparación se realiza en el período elegido.':
   (missing===periods.length?'No fue posible cargar los índices. Puedes ingresar una razón social manualmente.':'Sin proveedores coincidentes en la cobertura consultada.');
 }catch(error){if(seq===suggestionSeq)byId('comparar-ayuda').textContent='No se pudieron obtener las sugerencias. Puedes ingresar el nombre completo manualmente.'}
}
for(const n of [1,2,3]){
 const input=byId('comparar-nombre-'+n);
 input.addEventListener('input',()=>{
  clearTimeout(suggestionTimers.get(n));
  suggestionTimers.set(n,setTimeout(()=>suggest(input),180));
 });
 input.addEventListener('focus',()=>{if(canonical(input.value).length>=2)suggest(input)});
}
byId('periodo').addEventListener('change',()=>{
 suggestionSeq++;byId('comparar-sugerencias').replaceChildren();
 byId('comparar-ayuda').textContent='Escribe al menos dos letras para ver proveedores de '+(byId('periodo').value||'los períodos publicados')+'.';
});
