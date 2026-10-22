// Panel de visualizaciones: únicamente agregados públicos ya publicados.
const V=id=>document.getElementById(id);
const fmt=new Intl.NumberFormat('es-CL');
const clp=n=>'$'+fmt.format(Math.round(n));
const short=n=>Math.abs(n)>=1e9?'$'+(n/1e9).toLocaleString('es-CL',{maximumFractionDigits:1})+' mil MM':Math.abs(n)>=1e6?'$'+(n/1e6).toLocaleString('es-CL',{maximumFractionDigits:1})+' MM':clp(n);
let catalog=null,request=0,cache=new Map();
async function get(path){
 if(cache.has(path))return cache.get(path);
 const p=fetch('./'+path).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()});
 cache.set(path,p);try{return await p}catch(e){cache.delete(path);throw e}
}
function node(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function metric(label,value){const x=node('div','viz-kpi');x.append(node('small','',label),node('strong','',value));return x}
function card(title,subtitle){const x=node('section','viz-card');x.append(node('h3','',title),node('p','muted',subtitle));return x}
function barRows(data,max,formatter,active){
 const box=node('div','viz-bars');
 for(const d of data){
  const row=node('div','viz-bar'+(d.label===active?' selected':'')),lab=node('span','viz-label',d.label);
  const track=node('div','viz-track'),fill=node('div','viz-fill');fill.style.width=(max>0?Math.max(0,d.value/max*100):0).toFixed(2)+'%';
  track.append(fill);row.append(lab,track,node('strong','viz-number',formatter(d.value)));
  if(d.month){row.tabIndex=0;row.setAttribute('role','button');row.setAttribute('aria-label','Explorar mes '+d.month);
   const choose=()=>{V('periodo').value=d.month;V('periodo').dispatchEvent(new Event('change'));};
   row.addEventListener('click',choose);row.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose()}});
  }
  box.append(row);
 }
 return box;
}
async function render(){
 const token=++request,root=V('analitica-visual');
 if(!root)return;
 const entity=V('entidad').value,month=V('periodo').value;
 root.replaceChildren(node('p','muted','Preparando visualizaciones mensuales…'));
 try{
  if(!catalog)catalog=await get('data/catalogo-publico.json');
  const periods=catalog.periodos.map(x=>x.periodo).sort();
  const results=await Promise.allSettled(periods.map(m=>get('data/analitica/'+m+'/'+entity+'.json')));
  if(token!==request)return;
  const good=results.flatMap((x,i)=>x.status==='fulfilled'?[x.value]:[]);
  if(!good.length){root.replaceChildren(node('p','muted','Todavía no hay agregados analíticos publicados para esta entidad.'));return}
  good.sort((a,b)=>a.periodo.localeCompare(b.periodo));
  const focus=good.find(x=>x.periodo===month)||good[good.length-1];
  const months=good.map(d=>({label:d.periodo,month:d.periodo,value:Number(d.monto_total_clp)||0,hasAmount:Number(d.registros_con_monto)>0}));
  const counts=good.map(d=>({label:d.periodo,month:d.periodo,value:Number(d.registros)||0}));
  root.replaceChildren();
  const money=card('Montos registrados','Montos informados en los registros, no pagos ni adjudicaciones.');
  const moneyKpis=node('div','viz-kpis');const valid=good.filter(d=>Number(d.registros_con_monto)>0);
  const sum=valid.reduce((n,d)=>n+Number(d.monto_total_clp||0),0);
  moneyKpis.append(metric('Suma de meses con monto',short(sum)),metric('Promedio por mes con monto',valid.length?short(sum/valid.length):'Sin datos'));
  money.append(moneyKpis,barRows(months,Math.max(1,...months.map(d=>d.value)),v=>short(v),''));
  for(const [i,r] of [...money.querySelectorAll('.viz-bar')].entries())if(!months[i].hasAmount)r.querySelector('strong').textContent='Sin monto';
  const actors=card(entity==='procesos'?'Organismos compradores':'Participantes por nombre','Registros publicados del período '+focus.periodo+'; no representa adjudicaciones.');
  const monetary=Array.isArray(focus.top_actores_monto)&&focus.top_actores_monto.length>0;
  const tops=(monetary?focus.top_actores_monto:focus.top_actores||[]).slice(0,7).map(([label,value])=>({label:String(label),value:Number(value)||0}));
  const actorKpis=node('div','viz-kpis');
  actorKpis.append(metric('Nombres distintos',fmt.format(Number(focus.actores_distintos_por_nombre)||0)),
   metric(monetary?'Monto del top 3':'Registros del top 3',monetary?short(tops.slice(0,3).reduce((n,x)=>n+x.value,0)):fmt.format(tops.slice(0,3).reduce((n,x)=>n+x.value,0))));
  actors.append(actorKpis);
  if(tops.length)actors.append(barRows(tops,Math.max(1,...tops.map(d=>d.value)),v=>monetary?short(v):fmt.format(v),''));
  else actors.append(node('p','muted','Sin participantes identificados en este período.'));
  const activity=card('Actividad mensual','Cantidad de registros disponibles por mes, no actividad diaria.');
  const activityKpis=node('div','viz-kpis');
  activityKpis.append(metric('Total de períodos publicados',fmt.format(counts.reduce((s,d)=>s+d.value,0))),
   metric('Promedio mensual',fmt.format(Math.round(counts.reduce((s,d)=>s+d.value,0)/counts.length))));
  activity.append(activityKpis,barRows(counts,Math.max(1,...counts.map(d=>d.value)),v=>fmt.format(v),focus.periodo));
  if(Array.isArray(focus.modalidades)&&focus.modalidades.length){
   const section=node('section','viz-breakdown');section.append(node('h4','','Modalidades · '+focus.periodo));
   const modes=focus.modalidades.slice(0,6).map(([label,value])=>({label:String(label),value:Number(value)||0}));
   section.append(barRows(modes,Math.max(1,...modes.map(x=>x.value)),v=>fmt.format(v),''));activity.append(section);
  }
  const foot=node('p','muted viz-disclaimer','Octubre es un período parcial. Las comparaciones pueden reflejar cobertura y no cambios reales de actividad. Los actores se agregan por nombre publicado.');
  root.append(money,actors,activity,foot);
 }catch(e){if(token===request)root.replaceChildren(node('p','muted','No fue posible preparar las visualizaciones: '+e.message))}
}
for(const id of ['entidad','periodo','analitica-vista'])V(id).addEventListener('change',render);
render();
