// Consultas transversales usando perfiles públicos mensuales, sin descargar fragmentos.
const ph=id=>document.getElementById(id);
const normalizeActor=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ').trim();
const cache=new Map();let seq=0,timer;
async function fetchPublic(relative){
 let error;
 for(const url of ['./'+relative,'https://raw.githubusercontent.com/juliopez/MercadoPublico-Inteligencia/main/frontend-v2/'+relative]){
  try{const res=await fetch(url,{cache:'no-store'});if(!res.ok)throw Error('HTTP '+res.status);return await res.json()}catch(e){error=e}
 }
 throw error;
}
async function catalog(){
 if(!cache.has('catalog'))cache.set('catalog',await fetchPublic('data/catalogo-publico.json'));
 return cache.get('catalog');
}
const shard=async text=>{
 const bytes=new TextEncoder().encode(text),digest=await crypto.subtle.digest('SHA-256',bytes);
 return new Uint8Array(digest)[0].toString(16).padStart(2,'0');
};
const profile=async(month,entity,name)=>{
 const key=normalizeActor(name),hash=await shard(key),path='data/perfiles/'+month+'/'+entity+'/'+hash+'.json';
 if(!cache.has(path))try{cache.set(path,await fetchPublic(path))}catch(e){if(!String(e).includes('404'))throw e;cache.set(path,{})}
 return cache.get(path)[key]||null;
};
async function suggestions(){
 const id=++seq,term=normalizeActor(ph('participante-nombre').value);
 ph('participante-sugerencias').replaceChildren();
 if(term.length<2)return;
 const type=ph('participante-tipo').value;
 const c=await catalog(),names=new Set(),hash=await shard(term.slice(0,2));
 for(const p of c.periodos){
  const path='data/participacion/'+p.periodo+'/sugerencias/'+type+'/'+hash+'.json';
  try{
   const entries=await fetchPublic(path);
   if(id!==seq)return;
   for(const name of entries)if(name.startsWith(term))names.add(name);
  }catch{}
 }
 for(const name of [...names].slice(0,40)){const opt=document.createElement('option');opt.value=name;ph('participante-sugerencias').append(opt)}
}
async function searchParticipant(){
 const req=++seq,name=ph('participante-nombre').value.trim(),type=ph('participante-tipo').value;
 const entity=type==='proveedor'?'ofertas':'procesos';
 ph('participante-resumen').replaceChildren();ph('participante-evolucion').replaceChildren();ph('participante-enlaces').replaceChildren();
 if(normalizeActor(name).length<2){ph('participante-estado').textContent='Introduce al menos dos caracteres.';return}
 ph('participante-estado').textContent='Consultando índices históricos públicos…';
 try{
  const c=await catalog(),rows=[];
  for(const p of c.periodos){
   if(req!==seq)return;
   const record=await profile(p.periodo,entity,name);
   const actor=normalizeActor(name),group=await shard(actor),path='data/participacion/'+p.periodo+'/'+type+'/'+group+'.json';
   let extra=null;
   try{
    if(!cache.has(path))cache.set(path,await fetchPublic(path));
    extra=cache.get(path)[actor]||null;
   }catch(error){if(!String(error).includes('404'))throw error}
   const outcome=type==='proveedor'?await profile(p.periodo,'resultados',name):null;
   rows.push({period:p.periodo,count:record?.registros||0,monto:record?.monto_total_clp||0,coverage:record?.registros_con_monto||0,extra,outcome:outcome?.registros||0});
  }
  if(req!==seq)return;
  const total=rows.reduce((s,r)=>s+r.count,0),months=rows.filter(r=>r.count).length;
  const active=rows.filter(r=>r.count>0);
  const coverageReady=active.every(r=>r.extra!==null);
  const processMonthCount=active.reduce((sum,r)=>sum+(r.extra?.procesos_distintos||0),0);
  const selectionIndicesReady=type==='proveedor'&&rows.filter(r=>r.outcome>0).every(r=>Array.isArray(r.extra?.codigos_seleccionados));
  const selectedCodes=new Set();
  const selectedAmounts=new Map();
  if(selectionIndicesReady)for(const r of rows){
   for(const code of r.extra?.codigos_seleccionados||[])selectedCodes.add(code);
   for(const [code,amount] of r.extra?.montos_seleccionados_por_codigo||[]){
    if(!selectedAmounts.has(code))selectedAmounts.set(code,amount);
    else if(selectedAmounts.get(code)!==amount)selectedAmounts.set(code,null);
   }
  }
  const selectedValue=[...selectedAmounts.values()].reduce((sum,n)=>sum+(Number.isFinite(n)?n:0),0);
  const knownSelected=Array.from(selectedAmounts.values()).filter(Number.isFinite).length;
  const metrics=[['Registros de '+(type==='proveedor'?'ofertas':'procesos'),total.toLocaleString('es-CL')],['Meses con actividad',String(months)],[type==='proveedor'?'Monto total ofertado informado':'Presupuesto disponible informado',new Intl.NumberFormat('es-CL',{style:'currency',currency:'CLP',maximumFractionDigits:0}).format(rows.reduce((s,r)=>s+r.monto,0))]];
  if(type==='proveedor'){
   metrics.push(['Procesos únicos participados',active.every(r=>Array.isArray(r.extra?.codigos_participados))?new Set(active.flatMap(r=>r.extra.codigos_participados)).size.toLocaleString('es-CL'):'Cobertura incompleta']);
   metrics.push(['Ofertas con monto informado',rows.reduce((sum,r)=>sum+r.coverage,0).toLocaleString('es-CL')+' de '+total.toLocaleString('es-CL')]);
   metrics.push(['Resultados con empresa seleccionada',rows.reduce((sum,r)=>sum+r.outcome,0).toLocaleString('es-CL')]);
   metrics.push(['Procesos distintos con selección registrada',selectionIndicesReady?selectedCodes.size.toLocaleString('es-CL'):'Pendiente de publicar índice']);
   metrics.push(['Suma de ofertas seleccionadas informadas',selectionIndicesReady&&knownSelected?new Intl.NumberFormat('es-CL',{style:'currency',currency:'CLP',maximumFractionDigits:0}).format(selectedValue)+' ('+knownSelected+' procesos con monto)':'Sin cobertura suficiente']);
   // Denominador único transversal, no la suma de procesos distintos de cada mes.
   const participatingCodes=new Set();
   const participationCoverage=active.every(r=>Array.isArray(r.extra?.codigos_participados));
   if(participationCoverage)for(const r of active)for(const code of r.extra.codigos_participados)participatingCodes.add(code);
   const base=participationCoverage?participatingCodes.size:processMonthCount;
   const baseLabel='procesos únicos';
   const selectedWithinBase=selectionIndicesReady?(participationCoverage?[...selectedCodes].filter(code=>participatingCodes.has(code)).length:selectedCodes.size):0;
   if(selectionIndicesReady&&participationCoverage&&base>0){
    const rate=100*selectedWithinBase/base;
    metrics.push(['Tasa de selección registrada',rate.toLocaleString('es-CL',{maximumFractionDigits:1})+' % ('+selectedWithinBase.toLocaleString('es-CL')+' de '+base.toLocaleString('es-CL')+' '+baseLabel+')']);
   }
   const offered=rows.reduce((sum,r)=>sum+r.monto,0);
   if(selectionIndicesReady&&knownSelected&&offered>0)
    metrics.push(['Relación monto seleccionado / ofertado',(100*selectedValue/offered).toLocaleString('es-CL',{maximumFractionDigits:1})+' % · indicador descriptivo']);

   metrics.push(['Procesos ganados verificados','Pendiente de verificar']);
   metrics.push(['Monto adjudicado verificado','Sin datos suficientes']);
  }else{
   metrics.push(['Ofertas recibidas vinculadas',coverageReady?active.reduce((sum,r)=>sum+(r.extra.ofertas_recibidas_vinculadas||0),0).toLocaleString('es-CL'):'En preparación']);
  }
  const groups=type==='proveedor'?[
   {title:'Participación',description:'Volumen de ofertas y procesos publicados.',labels:['Registros de ofertas','Meses con actividad','Procesos únicos participados','Ofertas con monto informado']},
   {title:'Efectividad',description:'Selecciones documentadas; no equivalen a contratos adjudicados.',labels:['Resultados con empresa seleccionada','Procesos distintos con selección registrada','Tasa de selección registrada','Procesos ganados verificados']},
   {title:'Resultados económicos',description:'Distingue importes ofertados, seleccionados y adjudicados.',labels:['Monto total ofertado informado','Suma de ofertas seleccionadas informadas','Relación monto seleccionado / ofertado','Monto adjudicado verificado']}
  ]:[{title:'Actividad del organismo',description:'Información disponible según el nombre publicado.',labels:metrics.map(m=>m[0])}];
  const target=ph('participante-resumen');
  target.classList.add('participant-groups');
  for(const group of groups){
   const entries=metrics.filter(([label])=>group.labels.includes(label));
   if(!entries.length)continue;
   const section=document.createElement('section');section.className='participant-metric-group';
   const heading=document.createElement('h3');heading.textContent=group.title;
   const summary=document.createElement('p');summary.className='participant-group-description';summary.textContent=group.description;
   const grid=document.createElement('div');grid.className='participant-metric-grid';
   for(const [label,val] of entries){
    const card=document.createElement('div');card.className='evolution-metric';
    const caption=document.createElement('small');caption.textContent=label;
    const number=document.createElement('strong');number.textContent=val;
    if(label==='Tasa de selección registrada'||label==='Procesos distintos con selección registrada')card.classList.add('participant-metric-emphasis');
    card.append(caption,number);grid.append(card);
   }
   section.append(heading,summary,grid);target.append(section);
  }
  const max=Math.max(1,...rows.map(r=>r.count));
  for(const row of rows){
   const line=document.createElement('div');line.className='amount-bar';
   const label=document.createElement('span');label.textContent=row.period;
   const track=document.createElement('div');track.className='actor-track';
   const fill=document.createElement('div');fill.className='actor-fill';fill.style.width=(row.count/max*100).toFixed(1)+'%';track.append(fill);
   const number=document.createElement('strong');number.textContent=row.count.toLocaleString('es-CL');
   const action=document.createElement('button');action.type='button';action.className='secondary';action.textContent='Examinar '+row.period;action.disabled=!row.count;
   action.addEventListener('click',()=>{
    ph('periodo').value=row.period;ph('periodo').dispatchEvent(new Event('change'));
    ph('entidad').value=entity;ph('entidad').dispatchEvent(new Event('change'));
    // El buscador indexado admite términos de 3+ caracteres: omitir partículas cortas de organismos.
    const query=type==='organismo'?name.split(/\s+/).filter(word=>normalizeActor(word).replace(/[^a-z0-9]/g,'').length>=3).join(' '):name;
    ph('busqueda-global-texto').value=query;
    ph('busqueda-global-alcance').value='mes';
    ph('global-estado').value='';ph('global-modalidad').value='';
    ph('busqueda-global-boton').click();ph('busqueda-global').scrollIntoView({behavior:'smooth'});
   });
   line.append(label,track,number);ph('participante-evolucion').append(line);
   ph('participante-enlaces').append(action);
  }
  ph('participante-estado').textContent=total?'Encontrados '+total.toLocaleString('es-CL')+' registros en '+months+' meses publicados. '+(type==='proveedor'?'Las selecciones registradas no acreditan adjudicaciones ni pagos. Consulta las ayudas de cada indicador.':'Los organismos se agrupan por nombre publicado, sin homologación.'):'No se encontraron coincidencias exactas del nombre normalizado en los perfiles publicados.';
 }catch(e){if(req===seq)ph('participante-estado').textContent='No fue posible consultar los índices: '+e.message}
}
ph('participante-buscar').addEventListener('click',searchParticipant);
ph('participante-nombre').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(suggestions,250)});
ph('participante-tipo').addEventListener('change',()=>{seq++;ph('participante-sugerencias').replaceChildren();ph('participante-nombre').value=''});
