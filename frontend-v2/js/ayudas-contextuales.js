// Ayudas metodológicas MER v2: accesibles por teclado, clic y toque. No se leen datos privados.
const HELP={
 "Buscar en todos los períodos":"Consulta índices públicos de los meses disponibles. Una coincidencia puede estar repetida entre períodos; no equivale a una contratación única.",
 "Entidad":"Determina el tipo de registros que se consultarán: procesos, ofertas, resultados u órdenes de compra. Su disponibilidad varía según el mes.",
 "Cobertura":"Todos los períodos busca en los meses indexados; solo período seleccionado restringe los resultados al mes de referencia.",
 "Palabras clave":"Buscar por códigos, nombres, organismos y proveedores. Se requieren al menos tres caracteres; las sugerencias no garantizan coincidencias.",
 "Estado":"Situación del registro según su fuente y fecha de actualización. No equivale automáticamente a adjudicación, pago o cierre contractual.",
 "Modalidad / tipo":"Forma de contratación informada en el origen; sus categorías pueden variar según el tipo de registro.",
 "Consulta por período":"Explora fragmentos de hasta 1.000 registros. Los filtros de esta consulta no buscan en todo el mes; para eso utiliza la búsqueda transversal.",
 "Mes de referencia":"Mes de origen o publicación utilizado para agrupar los registros. El mes actual es parcial y puede cambiar.",
 "Período seleccionado":"Mes de referencia vigente para la consulta. Puede contener información histórica o del mes operativo.",
 "Evolución mensual de registros":"Compara cantidad de registros publicados por mes. No representa compras únicas, gasto ejecutado ni montos adjudicados.",
 "Perspectiva":"Destaca uno de los tres paneles; los demás siguen disponibles para consultar.",
 "Comparar con":"Contrasta períodos publicados. Las variaciones del mes en curso se interpretan con cautela por su cobertura parcial.",
 "Montos registrados":"Suma de presupuestos disponibles informados en pesos chilenos y visibles en los registros. Excluye montos no informados, precios referenciales, USD y UF; no son adjudicaciones ni pagos.",
 "Suma de montos informados":"Total de importes válidos registrados en la cobertura disponible. No incluye registros sin presupuesto CLP visible.",
 "Promedio de meses con monto":"Promedio calculado únicamente entre los meses con al menos un importe informado; no es el promedio de compras adjudicadas.",
 "Tendencia de montos":"Evolución de las sumas mensuales informadas; un mes sin datos monetarios se omite del trazado en lugar de presentarse como cero.",
 "Organismos compradores":"Entidades identificadas por el nombre consignado en los registros. Los nombres todavía no están homologados y una entidad puede aparecer con variantes.",
 "Nombres distintos":"Cantidad de nombres distintos informados. No necesariamente equivale al número real de instituciones únicas.",
 "Participación del top 3":"Porcentaje del monto informado concentrado en los tres organismos con mayor suma monetaria. Si no existen montos, se presenta ranking por cantidad de registros.",
 "Concentración del monto":"Distribución porcentual del presupuesto CLP informado entre los principales organismos. No mide participación en pagos ni adjudicaciones.",
 "Actividad":"Cantidad de registros publicados por período y, cuando existe el dato, distribución por modalidad.",
 "Total de registros publicados":"Suma de filas públicas de los períodos disponibles, no de operaciones únicas ni adjudicaciones comprobadas.",
 "Promedio mensual":"Media de registros publicados por mes en la cobertura mostrada; puede incluir un mes parcial.",
 "Variación mensual de registros":"Cambio porcentual respecto del mes anterior. El mes operativo parcial no se presenta como variación comparable.",
 "Modalidades del mes":"Recuento de registros por modalidad consignada en la fuente. Es un conteo, no una distribución de montos.",
 "Registros del período":"Tabla de los registros descargados del bloque actual, con paginación. Para buscar en todo el período utiliza la búsqueda transversal.",
 "Participación histórica de empresas y organismos":"Permite explorar la presencia de nombres en diversos meses publicados. Los nombres no están necesariamente homologados.",
 "Comparar proveedores":"Comparación exploratoria por nombre exacto. Una aparición en oferta, resultado u orden no acredita por sí sola contratación efectiva o pago.",
 "Favoritos guardados":"Se guardan referencias en este navegador; no constituyen registros privados de la plataforma ni alteran los datos públicos.",
 "Código":"Identificador publicado del proceso o de la orden de compra; al abrirlo se consulta la ficha disponible.",
 "Monto Disponible Clp":"Presupuesto disponible visible y expresado en CLP. Puede faltar aunque el proceso exista. No debe confundirse con adjudicación ni con pago.",
 "Monto Total Oc Clp":"Importe informado para la orden de compra; no acredita por sí mismo pago efectivo.",
 "Total Ofertas Recibidas":"Cantidad de ofertas informada por la fuente, que puede estar ausente o pendiente de consolidación.",
 "Organismo Comprador":"Entidad compradora tal como figura en el registro de origen; las denominaciones no están homologadas.",
 "Url Detalle":"Enlace a la ficha oficial del proceso, cuando existe en la fuente o puede construirse de manera verificable.",
 "Convocatoria":"Tipo de convocatoria o procedimiento declarado en el registro; puede no estar informado.",
 "Fecha Publicacion":"Fecha asociada a la publicación original del registro; no corresponde necesariamente a la actualización de este observatorio.",
 "Fecha Cierre":"Plazo de cierre consignado en la fuente; puede cambiar o no estar disponible.",
 "OC relacionadas":"Relaciones documentales o estructuradas entre procesos y órdenes de compra. La coincidencia o vinculación no sustituye verificar el estado contractual en Mercado Público.",
 "Ofertas vinculadas":"Ofertas encontradas para el código del proceso. No implica que todas hayan sido seleccionadas.",
 "Resultados vinculados":"Datos de selección o adjudicación encontrados en la fuente. Su fiabilidad depende de los estados de verificación disponibles."
};
const normalize=s=>String(s||'').replace(/ⓘ/g,'').replace(/\s+/g,' ').replace(/\s*[↗→].*$/,'').replace(/\s+\d[\d.,]*$/,'').trim();
function attach(el,title,description){
 if(!el||el.dataset.helpReady)return;
 el.dataset.helpReady='1';
 const button=document.createElement('button');
 button.type='button';button.className='mer-help-trigger';button.setAttribute('aria-label','Ayuda: '+title);
 button.setAttribute('aria-expanded','false');button.textContent='ⓘ';
 const tip=document.createElement('span');tip.className='mer-help-tooltip';tip.setAttribute('role','tooltip');tip.textContent=description;tip.hidden=true;
 const wrapper=document.createElement('span');wrapper.className='mer-help-inline';
 button.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();const open=tip.hidden;document.querySelectorAll('.mer-help-tooltip:not([hidden])').forEach(x=>{x.hidden=true;x.previousElementSibling?.setAttribute('aria-expanded','false')});tip.hidden=!open;button.setAttribute('aria-expanded',String(open))});
 button.addEventListener('keydown',e=>{if(e.key==='Escape'){tip.hidden=true;button.setAttribute('aria-expanded','false');button.focus()}});
 wrapper.append(button,tip);el.append(wrapper);
}
function scan(){
 const root=document.querySelector('main');if(!root)return;
 for(const el of root.querySelectorAll('h2,h3,h4,label,.viz-card h3,.viz-card h4,.viz-kpi span,.stat>span')){
  if(el.closest('.mer-help-tooltip'))continue;
  const txt=normalize(el.childNodes[0]?.textContent||el.textContent);
  const desc=HELP[txt];
  if(desc)attach(el,txt,desc);
 }
 const labels=[['#indicadores .stat:first-child span','Período seleccionado']];
 for(const [selector,key] of labels){const el=document.querySelector(selector);if(el)attach(el,key,HELP[key])}
}
let scheduled=false;
const observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;queueMicrotask(()=>{scheduled=false;scan()})});
const start=()=>{scan();const main=document.querySelector('main');if(main)observer.observe(main,{childList:true,subtree:true})};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
document.addEventListener('click',e=>{if(e.target.closest('.mer-help-inline'))return;document.querySelectorAll('.mer-help-tooltip:not([hidden])').forEach(t=>{t.hidden=true;t.previousElementSibling?.setAttribute('aria-expanded','false')})});
