// Filtro temático: verifica todas las referencias del índice antes de calcular agregados.
// No modifica datos, índices, procesos ni contratos de publicación.
const F=id=>document.getElementById(id);
const fields={procesos:['codigo','nombre','organismo_comprador'],ofertas:['codigo','proveedor'],resultados:['codigo','adjudicatario'],ordenescompra:['codigo_oc','codigo_proceso','proveedor']};
const actors={procesos:'organismo_comprador',ofertas:'proveedor',resultados:'adjudicatario',ordenescompra:'proveedor'};
const amounts={procesos:'monto_disponible_clp',ofertas:'monto_ofertado_clp',resultados:'monto_adjudicado_clp',ordenescompra:'monto_total_oc_clp'};
const normalize=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const words=s=>normalize(s).match(/[a-z0-9]+/g)||[];
let serial=0;
function status(t){F('analitica-filtro-estado').textContent=t}
async function get(path){
 if(!/^data\/(catalogo-publico\.json|indices\/20\d{2}-\d{2}\.json|busqueda\/20\d{2}-\d{2}\/[a-z]+\/(meta|[a-z0-9]{2})\.json|partes\/[a-z]+\/20\d{2}-\d{2}\/[a-z0-9_-]+\.json)$/.test(path))throw Error('Ruta no permitida');
 const r=await fetch('./'+path,{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status+': '+path);return r.json();
}
function money(raw){
 if(raw==null||String(raw).trim()==='')return null;
 const x=Number(String(raw).trim().replaceAll('.','').replace(',','.'));
 return Number.isFinite(x)&&x>=0&&x<=1e15?Math.round(x):null;
}
const top=map=>[...map.entries()].sort((a,b)=>b[1]-a[1]).slice(0,10);
function aggregate(month,entity,matched){
 const count=new Map(),sums=new Map(),modes=new Map(),unique=new Map();let total=0,moneyCount=0,sum=0;
 for(const r of matched){
  total++;const name=String(r[actors[entity]]||'').trim(),amount=money(r[amounts[entity]]);
  if(entity==='procesos'){const code=String(r.codigo||'').trim().toUpperCase();if(code&&!unique.has(code))unique.set(code,{modalidad:String(r.modalidad||''),monto:money(r.monto_disponible_clp)});}
  if(name)count.set(name,(count.get(name)||0)+1);
  const mode=String(r.modalidad||r.tipo_oc||'').trim();
  if(mode)modes.set(mode,(modes.get(mode)||0)+1);
  if(amount!==null){moneyCount++;sum+=amount;if(name)sums.set(name,(sums.get(name)||0)+amount)}
 }
 const split={licitacion:0,compra_agil:0,otras:0};for(const item of unique.values()){const m=normalize(item.modalidad);if(m.includes('compra agil'))split.compra_agil++;else if(m.includes('licitacion'))split.licitacion++;else split.otras++}
 const uniqueBudget=[...unique.values()].reduce((n,x)=>n+(x.monto||0),0);
 return {monto_procesos_unicos_clp:entity==='procesos'?uniqueBudget:null,procesos_unicos:entity==='procesos'?unique.size:null,modalidades_unicas:split,periodo:month,entidad:entity,registros:total,registros_con_monto:moneyCount,monto_total_clp:sum,actores_distintos_por_nombre:count.size,top_actores:top(count),top_actores_monto:top(sums),modalidades:top(modes)};
}
// Relación exacta por código y mes; las ofertas no se buscan por texto independiente.
async function linkedOffers(month,catalog,processRows,ticket){
 const codes=new Set(processRows.map(r=>String(r.codigo||'').trim().toUpperCase()).filter(Boolean));
 if(!codes.size)return {ofertas_unicas:0,ofertas_con_monto:0,monto_ofertado_unico_clp:0,ofertas_sin_id:0};
 const index=await get('data/indices/'+month+'.json');
 if(index.periodo!==month||!index.entidades?.ofertas)throw Error('Índice de relaciones incompatible: '+month);
 const paths=catalog.periodos.find(x=>x.periodo===month)?.partes?.ofertas||[];
 const needed=new Set();
 for(const code of codes){
  for(const ref of index.entidades.ofertas[code]||[]){
   const path=typeof ref==='number'?index.archivos?.ofertas?.[ref]:ref;
   if(typeof path!=='string'||!paths.includes(path))throw Error('Ruta de oferta fuera del catálogo: '+month);
   needed.add(path);
  }
 }
 const seen=new Set();let amount=0,withAmount=0,missing=0;
 for(const path of needed){
  if(ticket!==serial)return null;
  const rows=await get(path);if(!Array.isArray(rows))throw Error('Fragmento ofertas inválido');
  for(const r of rows){
   if(!codes.has(String(r.codigo||'').trim().toUpperCase()))continue;
   const id=String(r.id_cotizacion||'').trim();
   if(!id){missing++;continue}
   const key=month+'|'+id;
   if(seen.has(key))continue;
   seen.add(key);
   const m=money(r.monto_ofertado_clp);
   if(m!==null){amount+=m;withAmount++}
  }
 }
 return {ofertas_unicas:seen.size,ofertas_con_monto:withAmount,monto_ofertado_unico_clp:amount,ofertas_sin_id:missing};
}
function progress(value,visible=true){
 const wrap=F('analitica-progreso-contenedor'),bar=F('analitica-progreso');
 wrap.hidden=!visible;bar.value=Math.max(0,Math.min(100,value));
 F('analitica-progreso-porcentaje').textContent=Math.round(bar.value)+' %';
}
async function run(ev){
 ev?.preventDefault();
 const ticket=++serial,entity=F('entidad').value,raw=F('analitica-palabra').value.trim(),tokens=[...new Set(words(raw))];
 if(!raw){window.merAnaliticaFiltro=null;document.dispatchEvent(new Event('mer-analytics-filter'));progress(0,false);status('Sin filtro: se muestran los agregados generales de todos los períodos.');return}
 if(!tokens.length||tokens.some(x=>x.length<3)){progress(0,false);status('Escribe palabras de al menos 3 caracteres.');return}
 F('analitica-aplicar').disabled=true;progress(0);status('Consultando índices para verificar coincidencias…');
 try{
  const catalog=await get('data/catalogo-publico.json'),plans=[];
  // Primero planificar todos los fragmentos: el denominador del progreso será real y estable.
  for(const p of catalog.periodos){
   if(ticket!==serial)return;
   const month=p.periodo,paths=p.partes?.[entity]||[],groups=new Map();
   if(paths.length){
    const meta=await get('data/busqueda/'+month+'/'+entity+'/meta.json');
    if(meta.version!==3||meta.fragmentos!==paths.length)throw Error('Índice no compatible con catálogo: '+month);
    const partitions=new Map();
    for(const prefix of new Set(tokens.map(x=>x.slice(0,2)))){
     try{partitions.set(prefix,await get('data/busqueda/'+month+'/'+entity+'/'+prefix+'.json'))}
     catch(e){if(String(e.message).startsWith('HTTP 404'))partitions.set(prefix,{});else throw e}
    }
    const lists=tokens.map(x=>partitions.get(x.slice(0,2))?.[x.slice(0,3)]||[]).sort((a,b)=>a.length-b.length);
    const intersections=lists.slice(1).map(a=>new Set(a.map(x=>x.join(':'))));
    for(const ref of (lists[0]||[]).filter(x=>intersections.every(s=>s.has(x.join(':'))))){
     const [part,pos]=ref;
     if(!Number.isInteger(part)||part<0||part>=paths.length||!Number.isInteger(pos)||pos<0)throw Error('Referencia inválida');
     if(!groups.has(part))groups.set(part,[]);
     groups.get(part).push(pos);
    }
   }
   plans.push({month,paths,groups});
   progress(30*plans.length/catalog.periodos.length);
   status('Índices consultados: '+plans.length+' de '+catalog.periodos.length+' períodos.');
  }
  const totalFragments=plans.reduce((sum,p)=>sum+p.groups.size,0);
  let finished=0;
  const output=[];
  for(const plan of plans){
   const matched=[];
   for(const [part,positions] of plan.groups){
    if(ticket!==serial)return;
    const rows=await get(plan.paths[part]);if(!Array.isArray(rows))throw Error('Fragmento inválido');
    for(const pos of positions){
     if(pos>=rows.length)throw Error('Posición inválida');
     const r=rows[pos],set=new Set(fields[entity].flatMap(k=>words(r[k])));
     if(tokens.every(w=>set.has(w)))matched.push(r);
    }
    finished++;
    progress(30+70*finished/Math.max(1,totalFragments));
    status('Verificando fragmentos: '+finished+' de '+totalFragments+' · '+plan.month+'.');
   }
   const result=aggregate(plan.month,entity,matched);
  if(entity==='procesos'){
   status('Vinculando ofertas a concursos únicos de '+plan.month+'…');
   const offers=await linkedOffers(plan.month,catalog,matched,ticket);
   if(ticket!==serial)return;
   Object.assign(result,offers);
  }
  output.push(result);
  }
  if(ticket!==serial)return;
  progress(100);
  window.merAnaliticaFiltro={active:true,entity,term:raw,data:output};
  document.dispatchEvent(new Event('mer-analytics-filter'));
  status('Filtro aplicado: «'+raw+'» · '+output.length+' períodos analizados. Gráficos actualizados.');
 }catch(e){
  if(ticket===serial){progress(0,false);status('No se aplicó el filtro: '+e.message+'. Se conservan los gráficos anteriores.')}
 }finally{if(ticket===serial)F('analitica-aplicar').disabled=false}
}
F('analitica-filtro-form').addEventListener('submit',run);
F('analitica-limpiar').addEventListener('click',()=>{serial++;progress(0,false);F('analitica-palabra').value='';F('analitica-aplicar').disabled=false;window.merAnaliticaFiltro=null;document.dispatchEvent(new Event('mer-analytics-filter'));status('Sin filtro: se muestran los agregados generales de todos los períodos.')});
F('entidad').addEventListener('change',()=>{serial++;F('analitica-palabra').value='';F('analitica-aplicar').disabled=false;window.merAnaliticaFiltro=null;status('Entidad modificada. Introduce una palabra clave para filtrar los gráficos.')});
