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
   rows.push({period:p.periodo,count:record?.registros||0,monto:record?.monto_total_clp||0,coverage:record?.registros_con_monto||0,extra});
  }
  if(req!==seq)return;
  const total=rows.reduce((s,r)=>s+r.count,0),months=rows.filter(r=>r.count).length;
  const counted=rows.filter(r=>r.extra!==null);
  const metrics=[['Registros de '+(type==='proveedor'?'ofertas':'procesos'),total.toLocaleString('es-CL')],['Meses con actividad',String(months)],['Montos informados',new Intl.NumberFormat('es-CL',{style:'currency',currency:'CLP',maximumFractionDigits:0}).format(rows.reduce((s,r)=>s+r.monto,0))]];
  if(type==='proveedor'){
   metrics.push(['Participaciones por proceso/mes',counted.length===rows.length?counted.reduce((sum,r)=>sum+(r.extra.procesos_distintos||0),0).toLocaleString('es-CL'):'En preparación']);
  }else{
   metrics.push(['Ofertas recibidas vinculadas',counted.length===rows.length?counted.reduce((sum,r)=>sum+(r.extra.ofertas_recibidas_vinculadas||0),0).toLocaleString('es-CL'):'En preparación']);
  }
  for(const [label,val] of metrics){const card=document.createElement('div');card.className='evolution-metric';const caption=document.createElement('small');caption.textContent=label;const number=document.createElement('strong');number.textContent=val;card.append(caption,number);ph('participante-resumen').append(card)}
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
    ph('busqueda-global-texto').value=name;
    ph('global-estado').value='';ph('global-modalidad').value='';
    ph('busqueda-global-boton').click();ph('busqueda-global').scrollIntoView({behavior:'smooth'});
   });
   line.append(label,track,number);ph('participante-evolucion').append(line);
   ph('participante-enlaces').append(action);
  }
  ph('participante-estado').textContent=total?'Encontrados '+total.toLocaleString('es-CL')+' registros en '+months+' meses publicados. Los conteos de procesos distintos se calculan por mes; un mismo código en meses diferentes podría contarse nuevamente. Las ofertas recibidas se vinculan solo cuando el proceso aparece en el mismo período de la oferta.':'No se encontraron coincidencias exactas del nombre normalizado en los perfiles publicados.';
 }catch(e){if(req===seq)ph('participante-estado').textContent='No fue posible consultar los índices: '+e.message}
}
ph('participante-buscar').addEventListener('click',searchParticipant);
ph('participante-nombre').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(suggestions,250)});
ph('participante-tipo').addEventListener('change',()=>{seq++;ph('participante-sugerencias').replaceChildren();ph('participante-nombre').value=''});
