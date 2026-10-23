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
async function participationExtra(period,name){
 const key=canonical(name),digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(key));
 const shard=new Uint8Array(digest)[0].toString(16).padStart(2,'0');
 const response=await fetch('./data/participacion/'+period+'/proveedor/'+shard+'.json',{cache:'no-store'});
 if(response.status===404)return null;
 if(!response.ok)throw Error('Índice de participación HTTP '+response.status);
 const json=await response.json();return json[key]||null;
}
async function compare(){
 const seq=++comparisonSeq;
 const scope=byId('comparar-alcance').value,selectedPeriod=byId('periodo').value;
 const names=[1,2,3].map(i=>byId('comparar-nombre-'+i).value.trim()).filter(Boolean);
 const keys=names.map(canonical);
 if(names.length<2||new Set(keys).size!==names.length||keys.some(k=>k.length<2)){clear('Ingrese dos o tres proveedores distintos con nombre completo.');return}
 if(scope==='mes'&&!/^20\d{2}-(0[1-9]|1[0-2])$/.test(selectedPeriod)){clear('Seleccione un período para la comparación mensual.');return}
 byId('comparar-estado').textContent='Calculando indicadores históricos comparables…';
 byId('comparar-ejecutar').disabled=true;
 try{
  const periods=scope==='mes'?[selectedPeriod]:await suggestionPeriods();
  if(!periods.length)throw Error('Sin períodos publicados');
  const values=await Promise.all(names.map(async name=>{
   const rows=await Promise.all(periods.map(async period=>{
    const [offer,result,oc,extra]=await Promise.all([
     profile(period,'ofertas',name),profile(period,'resultados',name),
     profile(period,'ordenescompra',name),participationExtra(period,name)
    ]);
    return {offer,result,oc,extra};
   }));
   const sum=(field,key)=>rows.reduce((t,row)=>t+(Number(row[field]?.[key])||0),0);
   const offerCount=sum('offer','registros'),months=rows.filter(row=>Number(row.offer?.registros)>0).length;
   const participationReady=rows.filter(row=>Number(row.offer?.registros)>0).every(row=>Array.isArray(row.extra?.codigos_participados));
   const selectedReady=rows.filter(row=>Number(row.result?.registros)>0).every(row=>Array.isArray(row.extra?.codigos_seleccionados));
   const participated=new Set(),selected=new Set(),selectedAmounts=new Map();
   for(const row of rows){
    for(const code of row.extra?.codigos_participados||[])participated.add(code);
    for(const code of row.extra?.codigos_seleccionados||[])selected.add(code);
    for(const [code,amount] of row.extra?.montos_seleccionados_por_codigo||[]){
     if(!selectedAmounts.has(code))selectedAmounts.set(code,amount);
     else if(selectedAmounts.get(code)!==amount)selectedAmounts.set(code,null);
    }
   }
   const selectedWithin=[...selected].filter(code=>participated.has(code)).length;
   const amount=[...selectedAmounts.values()].reduce((t,v)=>t+(Number.isFinite(v)?v:0),0);
   return {offerCount,months,offerAmount:sum('offer','monto_total_clp'),offerCoverage:sum('offer','registros_con_monto'),
    participation:participationReady?participated.size:null,selection:selectedReady?selected.size:null,
    results:sum('result','registros'),rate:participationReady&&selectedReady&&participated.size?100*selectedWithin/participated.size:null,
    selectedAmount:selectedReady&&[...selectedAmounts.values()].some(Number.isFinite)?amount:null,
    ocCount:sum('oc','registros'),ocAmount:sum('oc','monto_total_clp')};
  }));
  if(seq!==comparisonSeq||byId('comparar-alcance').value!==scope||(scope==='mes'&&byId('periodo').value!==selectedPeriod))return;
  const metrics=[
   ['Ofertas registradas',v=>v.offerCount.toLocaleString('es-CL')],
   ['Meses con ofertas',v=>String(v.months)],
   ['Procesos únicos participados',v=>v.participation===null?'Cobertura incompleta':v.participation.toLocaleString('es-CL')],
   ['Ofertas con monto informado',v=>v.offerCoverage.toLocaleString('es-CL')],
   ['Monto total ofertado informado',v=>formatMoney(v.offerAmount)],
   ['Resultados con empresa seleccionada',v=>v.results.toLocaleString('es-CL')],
   ['Procesos únicos con selección registrada',v=>v.selection===null?'Pendiente de índice':v.selection.toLocaleString('es-CL')],
   ['Tasa de selección registrada',v=>v.rate===null?'No calculable':v.rate.toLocaleString('es-CL',{maximumFractionDigits:1})+' %'],
   ['Suma de ofertas seleccionadas informadas',v=>v.selectedAmount===null?'Sin cobertura suficiente':formatMoney(v.selectedAmount)],
   ['Órdenes de compra registradas',v=>v.ocCount.toLocaleString('es-CL')],
   ['Monto informado en órdenes de compra',v=>formatMoney(v.ocAmount)],
   ['Adjudicaciones contractuales verificadas',()=> 'Sin verificación suficiente']
  ];
  const head=document.createElement('tr');head.append(cell('Indicador'));
  for(const name of names){const th=document.createElement('th');th.textContent=name;head.append(th)}
  const body=document.createDocumentFragment();
  for(const [label,format] of metrics){
   const row=document.createElement('tr');row.append(cell(label));
   for(const v of values)row.append(cell(format(v)));
   body.append(row);
  }
  byId('comparar-cabecera').replaceChildren(head);byId('comparar-cuerpo').replaceChildren(body);
  // Ordenamiento ascendente/descendente conservado en la tabla comparativa.
  const tbody=byId('comparar-cuerpo'),headers=[...head.children];let activeSort=null,direction=1;
  headers.forEach((th,index)=>{
   const label=th.textContent,button=document.createElement('button');button.type='button';button.className='sort-heading';button.textContent=label+' ⇅';
   button.addEventListener('click',()=>{
    direction=activeSort===index?-direction:1;activeSort=index;
    const numeric=value=>Number(value.replace(/[^0-9,.-]/g,'').replaceAll('.','').replace(',','.'));
    const rows=[...tbody.children].sort((aa,bb)=>{
     const aaText=aa.children[index]?.textContent||'',bbText=bb.children[index]?.textContent||'';
     const x=numeric(aaText),y=numeric(bbText);
     return direction*(index>0&&aaText&&!/^(Sin|No |Pendiente)/.test(aaText)&&bbText&&!/^(Sin|No |Pendiente)/.test(bbText)&&Number.isFinite(x)&&Number.isFinite(y)?x-y:aaText.localeCompare(bbText,'es',{numeric:true}));
    });
    tbody.replaceChildren(...rows);
    headers.forEach((h,i)=>h.firstChild.textContent=h.dataset.label+(activeSort===i?(direction===1?' ↑':' ↓'):' ⇅'));
   });
   th.dataset.label=label;th.replaceChildren(button);
  });
  byId('comparar-estado').textContent='Comparación de '+names.length+' proveedores · '+(scope==='mes'?selectedPeriod:'todos los períodos ('+periods.length+' meses)')+'. Tasa basada en códigos únicos; selección registrada no equivale a adjudicación contractual. Los nombres no sustituyen el RUT.';
 }catch(error){
  if(seq===comparisonSeq)byId('comparar-estado').textContent='No fue posible completar la comparación: '+error.message;
 }finally{if(seq===comparisonSeq)byId('comparar-ejecutar').disabled=false}
}
byId('comparar-ejecutar').addEventListener('click',compare);
byId('periodo').addEventListener('change',()=>{if(byId('comparar-alcance').value==='mes')clear('El período cambió. Ejecute nuevamente la comparación.');});
byId('comparar-alcance').addEventListener('change',()=>clear('Alcance cambiado. Ejecute nuevamente la comparación.'));

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
  const periods=byId('comparar-alcance').value==='mes'&&/^20\d{2}-(0[1-9]|1[0-2])$/.test(period)?[period]:await suggestionPeriods();
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
