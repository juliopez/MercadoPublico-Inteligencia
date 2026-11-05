// Panel gráfico V2: utiliza exclusivamente agregados analíticos públicos.
const V=id=>document.getElementById(id);
const number=new Intl.NumberFormat('es-CL');
const pct=n=>n.toLocaleString('es-CL',{maximumFractionDigits:1})+' %';
const currency=n=>'$'+(Math.abs(n)>=1e9?(n/1e9).toLocaleString('es-CL',{maximumFractionDigits:1})+' mil millones':Math.abs(n)>=1e6?(n/1e6).toLocaleString('es-CL',{maximumFractionDigits:1})+' millones':number.format(Math.round(n)));
const create=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e};
const svg=(tag,attrs)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));return e};
const cache=new Map();let catalog=null,request=0;
const reloadAnalytic=()=>{for(const key of cache.keys())if(key.startsWith('data/analitica/'))cache.delete(key)};
const currentMonth=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/Santiago',year:'numeric',month:'2-digit'}).format(new Date());
async function fetchData(path){if(cache.has(path))return cache.get(path);const p=fetch('./'+path+'?actualizacion='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()});cache.set(path,p);try{return await p}catch(e){cache.delete(path);throw e}}
const total=a=>a.reduce((s,v)=>s+Number(v||0),0);
function kpis(items){const root=create('div','viz-kpis');for(const [a,b,hint] of items){const k=create('div','viz-kpi'),label=create('small','',a);if(hint){const help=create('button','viz-kpi-help','ⓘ');help.type='button';help.title=hint;help.setAttribute('aria-label','Información sobre '+a);help.setAttribute('aria-expanded','false');const details=create('span','viz-kpi-explanation',hint);details.hidden=true;help.addEventListener('click',()=>{details.hidden=!details.hidden;help.setAttribute('aria-expanded',String(!details.hidden))});label.append(document.createTextNode(' '),help,details)}k.append(label,create('strong','',b));root.append(k)}return root}
function section(name,sub){const c=create('section','viz-card');c.append(create('h3','',name),create('p','muted',sub));return c}
let userSelectedMonth='';
function choose(m){userSelectedMonth=m;V('periodo').value=m;V('periodo').dispatchEvent(new Event('change'));updateDetailButton()}
function updateDetailButton(){const b=V('analitica-ver-registros');if(!b)return;b.disabled=!userSelectedMonth;b.textContent=userSelectedMonth?'Ver registros de '+userSelectedMonth:'Selecciona un mes en el gráfico'}
function bars(data,formatter,active,interactive=false){
 const holder=create('div','viz-bars');const max=Math.max(1,...data.map(x=>x.value));
 for(const r of data){
  const line=create('div','viz-bar'+(r.key===active?' selected':''));
  const label=create('span','viz-label',r.label);label.title=r.full||r.label;
  const track=create('div','viz-track'),fill=create('div','viz-fill');fill.style.width=(100*Math.max(0,r.value)/max).toFixed(1)+'%';track.append(fill);
  line.append(label,track,create('strong','viz-number',formatter(r.value)));
  if(interactive){line.tabIndex=0;line.setAttribute('role','button');line.setAttribute('aria-label','Ver '+r.key);line.addEventListener('click',()=>choose(r.key));line.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose(r.key)}})}
  holder.append(line);
 }
 return holder;
}
function trend(data,active){
 const box=create('div','viz-trend'),heading=create('h4','','Tendencia de montos'),S=svg('svg',{viewBox:'0 0 440 150',role:'img','aria-label':'Tendencia de montos por mes'});
 const max=Math.max(1,...data.map(d=>d.value))*1.12;
 const X=i=>30+(data.length===1?190:i*380/(data.length-1)),Y=v=>118-v/max*94;
 for(let i=0;i<4;i++){const y=118-i*31;S.append(svg('line',{x1:28,y1:y,x2:420,y2:y,stroke:'#e2ecf3','stroke-dasharray':'3 4'}))}
 const points=data.map((d,i)=>[X(i),Y(d.value)]);
 if(points.length){const area=svg('path',{d:'M '+points[0][0]+' 118 L '+points.map(p=>p.join(' ')).join(' L ')+' L '+points.at(-1)[0]+' 118 Z',fill:'#dceefa'});S.append(area);
  S.append(svg('polyline',{points:points.map(p=>p.join(',')).join(' '),fill:'none',stroke:'#1a78ad','stroke-width':3,'stroke-linejoin':'round'}));
  points.forEach((p,i)=>{const dot=svg('circle',{cx:p[0],cy:p[1],r:data[i].periodo===active?6:4,fill:'#176b92',stroke:'#fff','stroke-width':2});S.append(dot);const label=svg('text',{x:p[0],y:141,'text-anchor':'middle',fill:'#52697a','font-size':10});label.textContent=data[i].periodo.slice(5);S.append(label)});
 }
 box.append(heading,S);return box;
}
function donut(tops,totalAmount){
 const top3=total(tops.slice(0,3).map(x=>x.value)),next=total(tops.slice(3).map(x=>x.value));
 const rem=Math.max(0,totalAmount-top3-next),denom=Math.max(1,totalAmount);
 const first=top3/denom*100,second=next/denom*100;
 const root=create('div','viz-donut-area');root.append(create('h4','','Concentración del monto'));
 const layout=create('div','viz-donut-content'),wheel=create('div','viz-donut');
 wheel.style.background='conic-gradient(#176b92 0 '+first+'%,#63a9dc '+first+'% '+(first+second)+'%,#c7dfef '+(first+second)+'% 100%)';
 const middle=create('div','viz-donut-center');middle.append(create('strong','',pct(first)),create('small','','Top 3'));wheel.append(middle);
 const legend=create('div','viz-donut-legend');
 [['Top 3 organismos',first],['Siguientes del top 10',second],['Otros o no identificados',rem/denom*100]].forEach(([label,value],i)=>{const r=create('div','viz-legend-row');const dot=create('i','viz-legend-dot shade-'+i);r.append(dot,create('span','',label),create('strong','',pct(value)));legend.append(r)});
 layout.append(wheel,legend);root.append(layout);return root;
}
function columns(data,active){
 const root=create('div','viz-columns'),max=Math.max(1,...data.map(x=>x.value));
 for(const d of data){const cell=create('button','viz-column'+(d.key===active?' selected':''));cell.type='button';cell.title=d.key+': '+number.format(d.value)+' registros';cell.setAttribute('aria-label',cell.title);cell.addEventListener('click',()=>choose(d.key));
  cell.append(create('strong','',number.format(d.value)));const track=create('div','viz-column-track'),fill=create('div','viz-column-fill');fill.style.height=(100*d.value/max)+'%';track.append(fill);cell.append(track,create('span','',d.key.slice(5)));root.append(cell)}
 return root;
}
function compositionColumns(data,active){
 const root=create('div','viz-columns viz-composition');
 const legend=create('div','viz-composition-legend');
 for(const [name,cls] of [['Licitación','licitacion'],['Compra Ágil','agil']]){
  const item=create('span','viz-composition-key');
  item.append(create('i','viz-composition-dot '+cls),document.createTextNode(name));
  legend.append(item);
 }
 root.append(legend);
 const panel=create('div','viz-composition-columns');
 for(const d of data){
  const cell=create('button','viz-column'+(d.key===active?' selected':''));cell.type='button';
  const modes=Array.isArray(d.modalidades)?d.modalidades:[];
  const agile=modes.reduce((n,[label,value])=>n+(/compra\s*ágil|compra\s*agil/i.test(String(label))?Number(value)||0:0),0);
  const lic=modes.reduce((n,[label,value])=>n+(/licitaci[oó]n/i.test(String(label))?Number(value)||0:0),0);
  const other=Math.max(0,d.value-agile-lic);
  const denom=Math.max(1,d.value);
  const agilePct=100*agile/denom,licPct=100*lic/denom,otherPct=100*other/denom;
  const detail=d.key+': '+number.format(d.value)+' procesos; '+number.format(lic)+' licitaciones ('+pct(licPct)+'); '+number.format(agile)+' Compras Ágiles ('+pct(agilePct)+')'+(other?' y '+number.format(other)+' otras modalidades':'');
  cell.title=detail;cell.setAttribute('aria-label',detail+'; seleccionar mes');cell.addEventListener('click',()=>choose(d.key));
  cell.append(create('strong','',number.format(d.value)));
  const track=create('div','viz-column-track viz-stack-track');
  for(const [value,cls] of [[other,'other'],[agile,'agil'],[lic,'licitacion']]){
   if(!value)continue;
   const part=create('div','viz-stack-segment '+cls);part.style.height=(100*value/denom)+'%';track.append(part);
  }
  cell.append(track,create('span','',d.key.slice(5)),create('small','viz-composition-ratio',agile?pct(agilePct)+' ágil':'0 % ágil'));
  if(d.key===active)cell.setAttribute('aria-current','true');
  panel.append(cell);
 }
 root.append(panel);
 root.append(create('p','muted viz-composition-note','Columnas de igual altura: muestran proporciones, no volumen. Los totales figuran arriba; el desglose inferior muestra las cantidades, incluso cuando una modalidad representa menos del 1 %.'));
 return root;
}
function variation(data){
 const root=create('div','viz-variation');
 root.append(create('h4','','Variación mensual de registros'));
 const plot=create('div','viz-change-list');
 for(let i=1;i<data.length;i++){
  const prev=data[i-1].value,partial=data[i].key===currentMonth();
  const change=!partial&&prev>0?(data[i].value/prev-1)*100:null;
  const item=create('div','viz-change');
  item.append(create('strong',change===null?'muted':change<0?'negative':'positive',change===null?'Parcial':(change>0?'+':'')+pct(change)));
  item.append(create('span','',data[i].key.slice(5)));
  plot.append(item);
 }
 root.append(plot);return root;
}
async function render(){
 catalog=null;
 cache.delete('data/catalogo-publico.json');
 reloadAnalytic();
 const token=++request,root=V('analitica-visual');if(!root)return;
 root.replaceChildren(create('p','muted','Cargando gráficos analíticos…'));
 const entity=V('entidad').value,selected=V('periodo').value;
 try{
  if(!catalog)catalog=await fetchData('data/catalogo-publico.json');
  const periods=catalog.periodos.map(x=>x.periodo).sort();
  const filterBefore=window.merAnaliticaFiltro;
  const reads=filterBefore?.active&&filterBefore.entity===entity ? [] : await Promise.allSettled(periods.map(p=>fetchData('data/analitica/'+p+'/'+entity+'.json')));
  if(token!==request)return;
  const filter=window.merAnaliticaFiltro;
  const data=(filter?.active && filter.entity===entity ? filter.data : reads.filter(x=>x.status==='fulfilled').map(x=>x.value)).slice().sort((a,b)=>a.periodo.localeCompare(b.periodo));
  if(!data.length){root.replaceChildren(create('p','muted','No hay agregados analíticos públicos para esta entidad.'));return}
  const focus=data.find(x=>x.periodo===selected)||data.at(-1),amountRows=data.map(x=>({key:x.periodo,label:x.periodo,value:+x.monto_total_clp||0,available:+x.registros_con_monto>0})),activityRows=data.map(x=>({key:x.periodo,value:+x.registros||0}));
  // El contexto se comunica en el propio gráfico y el botón, no en un rótulo redundante.
  const money=section('Montos registrados','Importes declarados en los registros publicados de los meses visibles. La suma puede incluir varias filas de un mismo concurso; no equivale a concursos únicos ni a pagos comprobados.');
  const valid=data.filter(x=>+x.registros_con_monto>0),sum=total(valid.map(x=>x.monto_total_clp));
  const moneyKinds={procesos:['Presupuestos disponibles','Los montos disponibles informados en procesos publicados; no son adjudicaciones ni pagos.'],ofertas:['Montos ofertados','Importes declarados en las ofertas; no necesariamente adjudicados.'],resultados:['Montos adjudicados informados','Importes asociados a resultados publicados, sujetos a su estado de verificación.'],ordenescompra:['Montos de órdenes de compra','Importes consignados en órdenes de compra, no pagos realizados.']};
  const [moneyTitle,moneyHint]=moneyKinds[entity];
  money.append(kpis([['Suma de '+moneyTitle.toLowerCase(),currency(sum),moneyHint+' Se suman filas con monto de los meses visibles.'],['Promedio por mes con montos informados',valid.length?currency(sum/valid.length):'Sin datos','La suma de montos se divide por los '+valid.length+' meses con algún importe informado; NO es un promedio por concurso ni por oferta.']]));
  if(entity==='procesos'&&filter?.active){
   const budget=new Map();
   // Se informa solamente la suma deduplicada por código, generada por el filtro de procesos.
   const uniqueBudget=data.reduce((n,x)=>n+Number(x.monto_procesos_unicos_clp||0),0);
   if(data.every(x=>Number.isFinite(x.monto_procesos_unicos_clp)))money.append(kpis([['Monto disponible de procesos únicos',currency(uniqueBudget),'Suma de presupuestos de códigos únicos coincidentes; cada código se cuenta una vez por mes. No corresponde a dinero adjudicado.']]));
  }
  money.append(bars(amountRows,currency,focus.periodo,true));money.querySelectorAll('.viz-bar').forEach((r,i)=>{if(!amountRows[i].available)r.querySelector('.viz-number').textContent='Sin monto'});
  money.append(trend(amountRows.filter(x=>x.available).map(x=>({periodo:x.key,value:x.value})),focus.periodo));
  const monetary=Array.isArray(focus.top_actores_monto)&&focus.top_actores_monto.length>0;
  const rankingUnico=entity==='procesos'&&Array.isArray(focus.organismos_procesos_unicos);
  const rank=rankingUnico?focus.organismos_procesos_unicos.slice(0,7).map(x=>({key:String(x.organismo),label:String(x.organismo),full:String(x.organismo),value:+x.monto||0,detail:x})):
   (monetary?focus.top_actores_monto:focus.top_actores||[]).slice(0,7).map(([label,value])=>({label:String(label),full:String(label),value:+value||0}));
  const actors=section(entity==='procesos'?'Organismos compradores':'Participantes principales',rankingUnico?'Presupuestos disponibles de procesos únicos del mes; cada barra corresponde a un organismo publicado. No son adjudicaciones.':entity==='procesos'?'Aún no está publicado el ranking certificado de procesos únicos para este mes. Los montos por filas no se muestran como presupuestos únicos.':monetary?'Distribución de montos informados por nombre publicado.':'Ranking de registros; desglose monetario aún no disponible.');
  if(rankingUnico){
   const totalUnico=focus.organismos_procesos_unicos.reduce((n,x)=>n+(+x.monto||0),0);
   const top3=rank.slice(0,3).reduce((n,x)=>n+x.value,0);
   actors.append(kpis([['Organismos identificados',number.format(focus.organismos_procesos_unicos.length),'Agrupados por nombre publicado, sin homologar variantes.'],['Presupuesto del top 3',totalUnico?pct(top3/totalUnico*100):'—','Porcentaje del monto disponible de procesos únicos del mes, no del dinero adjudicado.']]));
   if(rank.length){
    const rankingBarras=bars(rank,currency,'');
    rankingBarras.querySelectorAll('.viz-bar').forEach((row,i)=>{
     const name=rank[i].full;
     if(!name||name==='Sin organismo informado')return;
     const label=row.querySelector('.viz-label'),link=create('button','viz-org-link',name);
     link.type='button';link.title='Ver procesos del organismo · '+focus.periodo;
     link.setAttribute('aria-label','Ver procesos de '+name+' en '+focus.periodo);
     link.addEventListener('click',()=>window.buscarProcesosOrganismo?.(name,focus.periodo));
     label.replaceChildren(link);
    });
    actors.append(rankingBarras);
    if(totalUnico>0&&rank.some(x=>x.value>0))actors.append(donut(rank,totalUnico));
    const details=create('div','viz-org-details');
    details.append(create('h4','','Concursos que componen cada barra'));
    for(const item of rank){
     const x=item.detail,line=create('p','viz-org-detail');
     const nameLabel=create('strong','');
     if(x.organismo&&x.organismo!=='Sin organismo informado'){
      const link=create('button','viz-org-link',x.organismo);
      link.type='button';link.title='Ver procesos del organismo · '+focus.periodo;
      link.setAttribute('aria-label','Ver procesos de '+x.organismo+' en '+focus.periodo);
      link.addEventListener('click',()=>window.buscarProcesosOrganismo?.(x.organismo,focus.periodo));
      nameLabel.append(link);
     }else nameLabel.textContent=x.organismo;
     line.append(nameLabel,document.createTextNode(': '+number.format(x.procesos)+' procesos únicos · '+number.format(x.licitaciones)+' licitaciones · '+number.format(x.compras_agiles)+' Compras Ágiles · '+number.format(x.otras)+' otras modalidades · '+number.format(x.con_monto)+' con presupuesto disponible.'));
     details.append(line);
    }
    actors.append(details);
   }else actors.append(create('p','muted','No se identificaron concursos para este mes y búsqueda.'));
  }else if(entity==='procesos'){
   actors.append(create('p','muted','La clasificación por organismo y código único requiere regenerar el agregado mensual. No se muestran montos por registros como si fueran concursos únicos.'));
  }else{
   const t3=total(rank.slice(0,3).map(x=>x.value)),base=monetary?+focus.monto_total_clp||0:+focus.registros||0;
   actors.append(kpis([['Nombres distintos',number.format(+focus.actores_distintos_por_nombre||0)],['Participación del top 3',base?pct(t3/base*100):'—']]));
   actors.append(bars(rank,monetary?currency:v=>number.format(v),''));
   if(monetary&&base>0)actors.append(donut(rank,base));
   else actors.append(create('p','muted','La concentración monetaria estará disponible al regenerar los agregados públicos.'));
  }
  const activity=section('Cobertura mensual de registros','Cantidad de procesos o registros disponibles en el Observatorio por período. El mes operativo es parcial y no representa una caída de actividad del mercado.');
  const acsum=total(activityRows.map(x=>x.value));
  const names={procesos:'registros de procesos',ofertas:'ofertas',resultados:'resultados',ordenescompra:'órdenes de compra'};
  activity.append(kpis([
   ['Total de '+names[entity],number.format(acsum),'Suma de filas publicadas de la entidad seleccionada en los '+data.length+' meses mostrados. Una oferta, resultado u orden de compra no equivale a un concurso distinto. No se mezclan entidades.'],
   ['Promedio mensual de '+names[entity],number.format(Math.round(acsum/activityRows.length)),'Total de registros de esta entidad dividido entre los '+activityRows.length+' meses mostrados, incluidos meses sin coincidencias y períodos parciales. No es el promedio de concursos únicos.']
  ]));
  if(entity==='procesos'){
   const complete=Number.isInteger(focus.procesos_unicos);
   const splits=focus.modalidades_unicas||{};
   const agile=Number(splits.compra_agil||0),licit=Number(splits.licitacion||0),other=Number(splits.otras||0);
   const label=focus.periodo+' · '+(filter?.active?'procesos coincidentes con «'+filter.term+'»':'procesos publicados');
   const card=section('Concursos por modalidad · '+focus.periodo,'Procesos con código único del mes seleccionado. '+(filter?.active?'Se aplica la palabra clave.':'Sin filtro temático.'));
   if(complete){
    card.append(kpis([['Procesos únicos',number.format(focus.procesos_unicos),'Se cuenta cada código de proceso una sola vez dentro del mes; no se cuentan las ofertas ni adjudicaciones.'],['Licitaciones',number.format(licit),'Códigos de procesos únicos clasificados como licitación.'],['Compras Ágiles',number.format(agile),'Códigos únicos clasificados como Compra Ágil.'],['Otras modalidades',number.format(other),'Códigos únicos de otras modalidades o sin clasificación.']]));
    card.append(create('p','muted','Cobertura: '+label+'. El conteo se basa en la clasificación publicada, no en interpretación semántica.'));
   }else card.append(create('p','muted','El agregado general de este mes aún no contiene códigos únicos certificados. Se mantienen los conteos de registros existentes; aplica una palabra clave para obtener el conteo deduplicado de coincidencias.'));
   if(filter?.active&&Number.isInteger(focus.ofertas_unicas)){
    const offerCard=section('Ofertas vinculadas · '+focus.periodo,'Ofertas presentadas a los concursos coincidentes, relacionadas por código de proceso y dentro del mismo mes.');
    offerCard.append(kpis([
     ['Ofertas únicas',number.format(focus.ofertas_unicas),'Deduplicadas por id_cotizacion en el mes; una empresa puede presentar más de una oferta.'],
     ['Suma de montos ofertados',currency(focus.monto_ofertado_unico_clp),'Suma de las ofertas únicas con importe disponible. No equivale al presupuesto del concurso ni a pagos.'],
     ['Ofertas con monto',number.format(focus.ofertas_con_monto),'Ofertas distintas con importe numérico válido; es el denominador de cualquier promedio por oferta.']
    ]));
    if(focus.ofertas_sin_id)offerCard.append(create('p','muted',number.format(focus.ofertas_sin_id)+' filas vinculadas sin identificador de oferta excluidas del conteo único.'));
    card.append(offerCard);
   }
   activity.append(card);
  }
  activity.append(entity==='procesos'?compositionColumns(data.map(d=>({key:d.periodo,value:+d.registros||0,modalidades:d.modalidades})),focus.periodo):columns(activityRows,focus.periodo),variation(activityRows));
  if(entity==='procesos'&&Array.isArray(focus.modalidades)&&focus.modalidades.length){const modes=create('div','viz-breakdown');modes.append(create('h4','','Modalidades del mes '+focus.periodo+(focus.periodo===currentMonth()?' · Parcial':'')));const rows=focus.modalidades.slice(0,5).map(([label,value])=>({label:String(label),value:+value||0}));const modeTotal=total(rows.map(x=>x.value));modes.append(bars(rows,v=>number.format(v)+' · '+pct(modeTotal?100*v/modeTotal:0),''));activity.append(modes)}
  root.replaceChildren(money,actors,activity,create('p','muted viz-disclaimer','Cifras descriptivas de registros públicos. El mes operativo puede ser parcial; no interpretar variaciones como evolución contractual. Los nombres de organismos no están homologados.'));

 }catch(e){if(token===request)root.replaceChildren(create('p','muted','No se pudo cargar el panel visual: '+e.message))}
}
V('analitica-ver-registros').addEventListener('click',()=>{
 const p=userSelectedMonth;if(!p)return;
 const filter=window.merAnaliticaFiltro;
 V('periodo').value=p;V('busqueda-global-alcance').value='mes';
 V('busqueda-global-alcance').dispatchEvent(new Event('change'));
 V('busqueda-global-texto').value=filter?.active&&filter.entity===V('entidad').value?filter.term:'';
 if(filter?.active&&filter.entity===V('entidad').value){V('busqueda-global-boton').click();V('busqueda-global').scrollIntoView({behavior:'smooth'});}
 else {V('ir-busqueda-global').click();V('consulta').scrollIntoView({behavior:'smooth'});}
});
['entidad','periodo'].forEach(id=>V(id).addEventListener('change',render));
document.addEventListener('mer-analytics-filter',render);
updateDetailButton();render();
