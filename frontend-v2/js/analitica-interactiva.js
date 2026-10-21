// Panel analítico mensual sin descargar los históricos en el navegador.
const A=id=>document.getElementById(id);
let analyticsCatalog=null,selectedMonth='',comparisonMonth='',analyticsRequest=0;
const nfmt=v=>Number(v||0).toLocaleString('es-CL');
const pesos=v=>'$'+nfmt(Math.round(Number(v||0)));
async function analyticFetch(path){
 const urls=['./'+path,'https://raw.githubusercontent.com/juliopez/MercadoPublico-Inteligencia/main/frontend-v2/'+path];
 let last;
 for(const url of urls){try{const r=await fetch(url);if(!r.ok)throw Error('HTTP '+r.status);return await r.json()}catch(e){last=e}}
 throw last;
}
async function analytics(){
 const id=++analyticsRequest,entity=A('entidad').value;
 const selected=selectedMonth||A('periodo').value,compare=A('analitica-comparar').value;
 const view=A('analitica-vista').value,area=A('analitica-detalle');
 if(!analyticsCatalog)return;
 const rows=analyticsCatalog.periodos,lookup=p=>rows.find(x=>x.periodo===p);
 const current=lookup(selected),other=lookup(compare);
 A('analitica-seleccion').textContent='Mes: '+(selected||'sin seleccionar')+(compare?' · comparación: '+compare:'')+' · '+entity+'. Octubre es un período parcial.';
 area.replaceChildren();
 if(!current)return;
 const block=document.createElement('p');
 if(view==='actividad'){
  const value=Number(current.conteos?.[entity]||0),base=Number(other?.conteos?.[entity]||0);
  block.textContent='Registros del mes seleccionado: '+nfmt(value)+(other?' · período comparado: '+nfmt(base)+' · diferencia: '+nfmt(value-base)+(base?' ('+((value/base-1)*100).toFixed(1)+' %)':''):'')+'.';
  area.append(block);
  return;
 }
 const months=[selected,...(compare?[compare]:[])],datas=[];
 try{
  for(const month of months){
   const record=await analyticFetch('data/analitica/'+month+'/'+entity+'.json');
   if(id!==analyticsRequest)return;
   datas.push(record);
  }
  if(view==='actores'){
   for(const d of datas){
    const heading=document.createElement('h4');heading.textContent=d.periodo+' · diez actores con más registros';area.append(heading);
    const chart=document.createElement('div');chart.className='actor-chart';
    const actors=d.top_actores||[],maximum=Math.max(1,...actors.map(x=>Number(x[1])||0));
    if(!actors.length){const empty=document.createElement('p');empty.textContent='Sin actores identificados en el período.';chart.append(empty)}
    for(const [name,count] of actors){
     const row=document.createElement('div');row.className='actor-bar';
     const label=document.createElement('span');label.className='actor-name';label.textContent=name;label.title=name;
     const track=document.createElement('div');track.className='actor-track';
     const fill=document.createElement('div');fill.className='actor-fill';fill.style.width=((Number(count)||0)/maximum*100).toFixed(1)+'%';track.append(fill);
     const value=document.createElement('strong');value.textContent=nfmt(count);
     row.append(label,track,value);chart.append(row);
    }
    area.append(chart);
   }
  }else{
   const chart=document.createElement('div');chart.className='amount-chart';
   const maximum=Math.max(1,...datas.map(d=>Number(d.monto_total_clp)||0));
   for(const d of datas){
    const row=document.createElement('div');row.className='amount-bar';
    const label=document.createElement('span');label.textContent=d.periodo;
    const track=document.createElement('div');track.className='actor-track';
    const fill=document.createElement('div');fill.className='actor-fill';fill.style.width=((Number(d.monto_total_clp)||0)/maximum*100).toFixed(1)+'%';track.append(fill);
    const value=document.createElement('strong');value.textContent=d.registros_con_monto?pesos(d.monto_total_clp):'Sin información';
    row.append(label,track,value);chart.append(row);
   }
   area.append(chart);
   const note=document.createElement('p');note.className='muted';note.textContent='Sumas de montos informados, no pagos ni adjudicaciones acreditadas. La comparación con meses parciales exige cautela.';area.append(note);
  }
 }catch(e){
  if(id===analyticsRequest)block.textContent='Agregados complementarios no disponibles todavía; la vista de actividad sigue funcionando.';area.append(block);
 }
}
function selectMonth(period){
 selectedMonth=period;
 A('periodo').value=period;A('periodo').dispatchEvent(new Event('change'));
 document.querySelectorAll('.evolution-row').forEach(row=>row.classList.toggle('selected',row.dataset.period===period));
 analytics();
}
async function initializeAnalytics(){
 try{
  analyticsCatalog=await analyticFetch('data/catalogo-publico.json');
  const monthSelect=A('analitica-comparar');
  for(const p of analyticsCatalog.periodos){const option=document.createElement('option');option.value=p.periodo;option.textContent=p.periodo;monthSelect.append(option)}
  selectedMonth=analyticsCatalog.periodos[0]?.periodo||'';
  analytics();
 }catch(e){A('analitica-seleccion').textContent='No se pudo consultar catálogo analítico.'}
}
A('analitica-vista').addEventListener('change',analytics);
A('analitica-comparar').addEventListener('change',analytics);
A('analitica-ver-registros').addEventListener('click',()=>{
 if(!selectedMonth)return;
 A('periodo').value=selectedMonth;A('periodo').dispatchEvent(new Event('change'));
 A('ir-busqueda-global').click();
});
A('entidad').addEventListener('change',analytics);
A('periodo').addEventListener('change',()=>{selectedMonth=A('periodo').value;analytics()});
document.addEventListener('click',e=>{
 const row=e.target.closest?.('.evolution-row[data-period]');
 if(row)selectMonth(row.dataset.period);
});
initializeAnalytics();
