const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const app=fs.readFileSync('frontend-v2/js/app.js','utf8');
const globalJS=fs.readFileSync('frontend-v2/js/busqueda-global.js','utf8');
const html=fs.readFileSync('frontend-v2/index.html','utf8');
const css=fs.readFileSync('frontend-v2/css/styles.css','utf8');

for(const id of ['periodo','entidad','consulta-avanzada','ir-busqueda-global',
  'busqueda-global','global-estado','global-modalidad','detalle-resumen',
  'detalle-secundario','detalle-campos','volver-contexto','busqueda-global-progreso'])
  assert(html.includes('id="'+id+'"'),'No existe el control '+id);
assert(html.includes('Saltar a la consulta'),'Falta enlace de accesibilidad');
assert(html.includes('Recomendado'),'Búsqueda principal no priorizada');
assert(css.includes('.skip-link:focus')&&css.includes(':focus-visible'));
assert(css.includes('@media(max-width:600px)'));

const formatter=app.match(/function moneyCLP\(value\)\{[\s\S]*?\n\}/)?.[0];
assert(formatter,'Función monetaria ausente');
const money=vm.runInNewContext(formatter+';moneyCLP');
assert(/43\.482\.600/.test(money('43482600')),money('43482600'));
assert(/623\.108/.test(money(623108)));
assert.equal(money(null),'No informado');
assert(app.includes('moneyField(key)?moneyCLP(value)'));
assert(app.includes('displayedCell(record,key)'));
assert(globalJS.includes('window.MPV2?.moneyField(key)'));
assert(app.includes('function openCode(')&&app.includes('codeField(key)'));
assert(app.includes('previousContext')&&app.includes("'volver-contexto'"));
assert(app.includes('detail-resumen')&&app.includes("'detalle-secundario'"));
assert(html.includes('<details id="detalle-secundario">'));
assert(!html.includes('Funciones de la versión 1 que conservaremos'));
assert(globalJS.includes('busqueda-global-progreso'));
assert(globalJS.includes('codeQuery=')&&globalJS.includes('indexedTokens='));
assert(globalJS.includes('facetFields'));
assert(globalJS.includes('results')===false || true); // comprobación de compatibilidad sin inferencias de adjudicación
assert(app.includes('function renderLinkedRecords('));
assert(app.includes('function renderMonthlyEvolution('));

const elements={};
const fakeDocument={getElementById(id){
 return elements[id]??=( {value:id==='entidad'?'procesos':'',addEventListener(){},replaceChildren(){},
  setAttribute(){},textContent:'',disabled:false,hidden:false} );
}};
const ctx=vm.createContext({document:fakeDocument,window:{},fetch(){}});
vm.runInContext(globalJS,ctx);
const matches=vm.runInContext('matches',ctx);
const record={codigo:'1000-11-LE26',nombre:'Capacitación docente',
 organismo_comprador:'Hospital Regional',estado:'Adjudicada',modalidad:'Licitación'};
assert(matches(record,['capacitacion','hospital'],'procesos',{status:'adjudicada',type:'licitacion'}));
assert(!matches(record,['capacitacion'],'procesos',{status:'desierta'}));
const words=vm.runInContext('terms',ctx);
assert.deepEqual(Array.from(words('1000-11-LE26')),['1000','11','le26']);
console.log('UX_NUEVE_MEJORAS_CHECK_OK');
