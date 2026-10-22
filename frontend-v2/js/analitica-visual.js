// Panel gráfico V2: utiliza exclusivamente agregados analíticos públicos.
const V=id=>document.getElementById(id);
const number=new Intl.NumberFormat('es-CL');
const pct=n=>n.toLocaleString('es-CL',{maximumFractionDigits:1})+' %';
const currency=n=>{const x=Number(n)||0;return '
const create=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e};
const svg=(tag,attrs)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));return e};
const cache=new Map();let catalog=null,request=0;
const currentMonth=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/Santiago',year:'numeric',month:'2-digit'}).format(new Date());
async function fetchData(path){if(cache.has(path))return cache.get(path);const p=fetch('./'+path).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()});cache.set(path,p);try{return await p}catch(e){cache.delete(path);throw e}}
const total=a=>a.reduce((s,v)=>s+Number(v||0),0);
function kpis(items){const root=create('div','viz-kpis');for(const [a,b] of items){const k=create('div','viz-kpi');k.append(create('small','',a),create('strong','',b));root.append(k)}return root}
function section(name,sub){const c=create('section','viz-card');c.append(create('h3','',name),create('p','muted',sub));return c}
function choose(m){V('periodo').value=m;V('periodo').dispatchEvent(new Event('change'))}
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
function variation(data){
 const root=create('div','viz-variation');root.append(create('h4','','Variación mensual de registros'));
 const plot=create('div','viz-change-list');
 for(let i=1;i<data.length;i++){
  const prior=data[i-1],now=data[i],partial=now.key===currentMonth();
  const change=!partial&&prior.value>0?(now.value/prior.value-1)*100:null;
  const item=create('div','viz-change');
  const label=change===null?'Parcial':(change>0?'+':'')+pct(change);
  const value=create('strong',change===null?'muted':change<0?'negative':'positive',label);
  item.append(value,create('span','',now.key.slice(5)));
  item.title=change===null?'Mes parcial: variación no comparable':now.key+' / '+prior.key+': '+label;
  plot.append(item);
 }
 root.append(plot);return root;
}
async function render(){
 const token=++request,root=V('analitica-visual');if(!root)return;
 root.replaceChildren(create('p','muted','Cargando gráficos analíticos…'));
 const entity=V('entidad').value,selected=V('periodo').value;
 try{
  if(!catalog)catalog=await fetchData('data/catalogo-publico.json');
  const periods=catalog.periodos.map(x=>x.periodo).sort();
  const comparator=V('analitica-comparar');
  if(comparator.options.length===1){for(const p of periods){const o=document.createElement('option');o.value=p;o.textContent=p;comparator.append(o)}}
  const reads=await Promise.allSettled(periods.map(p=>fetchData('data/analitica/'+p+'/'+entity+'.json')));
  if(token!==request)return;
  const data=reads.filter(x=>x.status==='fulfilled').map(x=>x.value).sort((a,b)=>a.periodo.localeCompare(b.periodo));
  if(!data.length){root.replaceChildren(create('p','muted','No hay agregados analíticos públicos para esta entidad.'));return}
  const focus=data.find(x=>x.periodo===selected)||data.at(-1),comparison=data.find(x=>x.periodo===comparator.value),amountRows=data.map(x=>({key:x.periodo,label:x.periodo,value:+x.monto_total_clp||0,available:+x.registros_con_monto>0})),activityRows=data.map(x=>({key:x.periodo,value:+x.registros||0}));
  V('analitica-seleccion').textContent='Mes de referencia: '+focus.periodo+(comparison?' · comparado con '+comparison.periodo:'')+' · '+entity+(focus.periodo===currentMonth()?' · mes en curso (parcial)':'');
  const money=section('Montos registrados','Suma de montos informados por mes; no acredita pagos.');
  const valid=data.filter(x=>+x.registros_con_monto>0),sum=total(valid.map(x=>x.monto_total_clp));
  money.append(kpis([['Suma de montos informados',currency(sum)],['Promedio de meses con monto',valid.length?currency(sum/valid.length):'Sin datos']]));
  money.append(bars(amountRows,currency,focus.periodo,true));money.querySelectorAll('.viz-bar').forEach((r,i)=>{if(!amountRows[i].available)r.querySelector('.viz-number').textContent='Sin monto'});
  money.append(trend(amountRows.filter(x=>x.available).map(x=>({periodo:x.key,value:x.value})),focus.periodo));
  const monetary=Array.isArray(focus.top_actores_monto)&&focus.top_actores_monto.length>0;
  const rank=(monetary?focus.top_actores_monto:focus.top_actores||[]).slice(0,7).map(([label,value])=>({label:String(label),full:String(label),value:+value||0}));
  const actors=section(entity==='procesos'?'Organismos compradores':'Participantes principales',monetary?'Distribución de montos informados por nombre publicado.':'Ranking de registros; desglose monetario aún no disponible.');
  const t3=total(rank.slice(0,3).map(x=>x.value));
  const base=monetary?+focus.monto_total_clp||0:+focus.registros||0;
  actors.append(kpis([['Nombres distintos',number.format(+focus.actores_distintos_por_nombre||0)],['Participación del top 3',base?pct(t3/base*100):'—']]));
  actors.append(bars(rank,monetary?currency:v=>number.format(v),''));
  if(monetary&&base>0)actors.append(donut(rank,base));
  else actors.append(create('p','muted','La concentración monetaria estará disponible al regenerar los agregados públicos.'));
  const activity=section('Actividad','Cantidad de registros publicados por mes.');
  const acsum=total(activityRows.map(x=>x.value));activity.append(kpis([['Total de registros publicados',number.format(acsum)],['Promedio mensual',number.format(Math.round(acsum/activityRows.length))]]));
  activity.append(columns(activityRows,focus.periodo),variation(activityRows));
  if(Array.isArray(focus.modalidades)&&focus.modalidades.length){const modes=create('div','viz-breakdown');modes.append(create('h4','','Modalidades del mes '+focus.periodo));const rows=focus.modalidades.slice(0,5).map(([label,value])=>({label:String(label),value:+value||0}));modes.append(bars(rows,v=>number.format(v),''));activity.append(modes)}
  const view=V('analitica-vista').value;
  [money,actors,activity].forEach((card,i)=>card.classList.toggle('viz-emphasis',(['montos','actores','actividad'][i]===view)));
  root.replaceChildren(money,actors,activity,create('p','muted viz-disclaimer','Cifras descriptivas de registros públicos. Octubre es un mes parcial; no interpretar variaciones como evolución contractual. Los nombres de organismos no están homologados.'));
  if(comparison){
   const comparisonPanel=create('div','viz-comparison');comparisonPanel.append(create('strong','','Comparación '+focus.periodo+' / '+comparison.periodo));
   for(const [title,key] of [['Registros','registros'],['Suma de montos informados','monto_total_clp']]){
    const current=Number(focus[key]||0),previous=Number(comparison[key]||0),delta=previous?((current/previous)-1)*100:null;
    comparisonPanel.append(create('span','',title+': '+(key==='registros'?number.format(current):currency(current))+' frente a '+(key==='registros'?number.format(previous):currency(previous))+(delta===null?'':(' · '+(delta>=0?'+':'')+pct(delta)))));
   }
   root.prepend(comparisonPanel);
  }

 }catch(e){if(token===request)root.replaceChildren(create('p','muted','No se pudo cargar el panel visual: '+e.message))}
}
V('analitica-ver-registros').addEventListener('click',()=>{const p=V('periodo').value;if(p)V('ir-busqueda-global').click()});
['entidad','periodo','analitica-vista','analitica-comparar'].forEach(id=>V(id).addEventListener('change',render));render();
+(Math.abs(x)>=1e9?(x/1e9).toLocaleString('es-CL',{maximumFractionDigits:1})+' mil millones':Math.abs(x)>=1e6?(x/1e6).toLocaleString('es-CL',{maximumFractionDigits:1})+' millones':number.format(Math.round(x)))};
const create=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e};
const svg=(tag,attrs)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));return e};
const cache=new Map();let catalog=null,request=0;
const currentMonth=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/Santiago',year:'numeric',month:'2-digit'}).format(new Date());
async function fetchData(path){if(cache.has(path))return cache.get(path);const p=fetch('./'+path).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()});cache.set(path,p);try{return await p}catch(e){cache.delete(path);throw e}}
const total=a=>a.reduce((s,v)=>s+Number(v||0),0);
function kpis(items){const root=create('div','viz-kpis');for(const [a,b] of items){const k=create('div','viz-kpi');k.append(create('small','',a),create('strong','',b));root.append(k)}return root}
function section(name,sub){const c=create('section','viz-card');c.append(create('h3','',name),create('p','muted',sub));return c}
function choose(m){V('periodo').value=m;V('periodo').dispatchEvent(new Event('change'))}
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
function variation(data){const root=create('div','viz-variation');root.append(create('h4','','Variación mensual de registros'));
 const plot=create('div','viz-change-list');
 for(let i=1;i<data.length;i++){const prev=data[i-1].value,partial=data[i].key===currentMonth(),change=(!partial&&prev)?((data[i].value/prev)-1)*100:null;const item=create('div','viz-change');item.append(create('strong',change===null?'—':(change>0?'+':'')+pct(change)));item.querySelector('strong').className=change===null?'':change<0?'negative':'positive';item.append(create('span','',data[i].key.slice(5)));plot.append(item)}
 root.append(plot);return root}
async function render(){
 const token=++request,root=V('analitica-visual');if(!root)return;
 root.replaceChildren(create('p','muted','Cargando gráficos analíticos…'));
 const entity=V('entidad').value,selected=V('periodo').value;
 try{
  if(!catalog)catalog=await fetchData('data/catalogo-publico.json');
  const periods=catalog.periodos.map(x=>x.periodo).sort();
  const comparator=V('analitica-comparar');
  if(comparator.options.length===1){for(const p of periods){const o=document.createElement('option');o.value=p;o.textContent=p;comparator.append(o)}}
  const reads=await Promise.allSettled(periods.map(p=>fetchData('data/analitica/'+p+'/'+entity+'.json')));
  if(token!==request)return;
  const data=reads.filter(x=>x.status==='fulfilled').map(x=>x.value).sort((a,b)=>a.periodo.localeCompare(b.periodo));
  if(!data.length){root.replaceChildren(create('p','muted','No hay agregados analíticos públicos para esta entidad.'));return}
  const focus=data.find(x=>x.periodo===selected)||data.at(-1),comparison=data.find(x=>x.periodo===comparator.value),amountRows=data.map(x=>({key:x.periodo,label:x.periodo,value:+x.monto_total_clp||0,available:+x.registros_con_monto>0})),activityRows=data.map(x=>({key:x.periodo,value:+x.registros||0}));
  V('analitica-seleccion').textContent='Mes de referencia: '+focus.periodo+(comparison?' · comparado con '+comparison.periodo:'')+' · '+entity+(focus.periodo===currentMonth()?' · mes en curso (parcial)':'');
  const money=section('Montos registrados','Suma de montos informados por mes; no acredita pagos.');
  const valid=data.filter(x=>+x.registros_con_monto>0),sum=total(valid.map(x=>x.monto_total_clp));
  money.append(kpis([['Suma de montos informados',currency(sum)],['Promedio de meses con monto',valid.length?currency(sum/valid.length):'Sin datos']]));
  money.append(bars(amountRows,currency,focus.periodo,true));money.querySelectorAll('.viz-bar').forEach((r,i)=>{if(!amountRows[i].available)r.querySelector('.viz-number').textContent='Sin monto'});
  money.append(trend(amountRows.map(x=>({periodo:x.key,value:x.value})),focus.periodo));
  const monetary=Array.isArray(focus.top_actores_monto)&&focus.top_actores_monto.length>0;
  const rank=(monetary?focus.top_actores_monto:focus.top_actores||[]).slice(0,7).map(([label,value])=>({label:String(label),full:String(label),value:+value||0}));
  const actors=section(entity==='procesos'?'Organismos compradores':'Participantes principales',monetary?'Distribución de montos informados por nombre publicado.':'Ranking de registros; desglose monetario aún no disponible.');
  const t3=total(rank.slice(0,3).map(x=>x.value));
  const base=monetary?+focus.monto_total_clp||0:+focus.registros||0;
  actors.append(kpis([['Nombres distintos',number.format(+focus.actores_distintos_por_nombre||0)],['Participación del top 3',base?pct(t3/base*100):'—']]));
  actors.append(bars(rank,monetary?currency:v=>number.format(v),''));
  if(monetary&&base>0)actors.append(donut(rank,base));
  else actors.append(create('p','muted','La concentración monetaria estará disponible al regenerar los agregados públicos.'));
  const activity=section('Actividad','Cantidad de registros publicados por mes.');
  const acsum=total(activityRows.map(x=>x.value));activity.append(kpis([['Total de registros publicados',number.format(acsum)],['Promedio mensual',number.format(Math.round(acsum/activityRows.length))]]));
  activity.append(columns(activityRows,focus.periodo),variation(activityRows));
  if(Array.isArray(focus.modalidades)&&focus.modalidades.length){const modes=create('div','viz-breakdown');modes.append(create('h4','','Modalidades del mes '+focus.periodo));const rows=focus.modalidades.slice(0,5).map(([label,value])=>({label:String(label),value:+value||0}));modes.append(bars(rows,v=>number.format(v),''));activity.append(modes)}
  const view=V('analitica-vista').value;
  [money,actors,activity].forEach((card,i)=>card.classList.toggle('viz-emphasis',(['montos','actores','actividad'][i]===view)));
  root.replaceChildren(money,actors,activity,create('p','muted viz-disclaimer','Cifras descriptivas de registros públicos. Octubre es un mes parcial; no interpretar variaciones como evolución contractual. Los nombres de organismos no están homologados.'));
  if(comparison){
   const comparisonPanel=create('div','viz-comparison');comparisonPanel.append(create('strong','','Comparación '+focus.periodo+' / '+comparison.periodo));
   for(const [title,key] of [['Registros','registros'],['Suma de montos informados','monto_total_clp']]){
    const current=Number(focus[key]||0),previous=Number(comparison[key]||0),delta=previous?((current/previous)-1)*100:null;
    comparisonPanel.append(create('span','',title+': '+(key==='registros'?number.format(current):currency(current))+' frente a '+(key==='registros'?number.format(previous):currency(previous))+(delta===null?'':(' · '+(delta>=0?'+':'')+pct(delta)))));
   }
   root.prepend(comparisonPanel);
  }

 }catch(e){if(token===request)root.replaceChildren(create('p','muted','No se pudo cargar el panel visual: '+e.message))}
}
V('analitica-ver-registros').addEventListener('click',()=>{const p=V('periodo').value;if(p)V('ir-busqueda-global').click()});
['entidad','periodo','analitica-vista','analitica-comparar'].forEach(id=>V(id).addEventListener('change',render));render();
