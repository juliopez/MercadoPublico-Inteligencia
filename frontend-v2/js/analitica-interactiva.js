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
    const title=document.createElement('h4');title.textContent=d.periodo+' · principales actores por registros';
    area.append(title);
    const list=document.createElement('ol');
    for(const [name,num] of d.top_actores||[]){const li=document.createElement('li');li.textContent=name+' — '+nfmt(num)+' registros';list.append(li)}
    area.append(list);
   }
  }else{
   const tr=document.createElement('p');
   tr.textContent=datas.map(d=>d.periodo+': '+pesos(d.monto_total_clp)+' ('+nfmt(d.registros_con_monto)+' registros con monto)').join(' · ')+'. Importes informados, no pagos ni adjudicaciones acreditadas.';
   area.append(tr);
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
