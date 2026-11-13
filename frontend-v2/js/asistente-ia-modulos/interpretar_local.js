// Interpretación local conservadora de consultas frecuentes. Sin Gemini ni acceso a producción.
import { validarIntencion } from './intencion.js';
const MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
function normalizar(s) { return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase(); }
function periodoEn(texto) {
  const iso = texto.match(/\b(20\d{2})-(0[1-9]|1[0-2])\b/);
  if (iso) return iso[0];
  for (let i=0;i<MESES.length;i++) {
    const m = new RegExp('\\b'+MESES[i]+'\\s+(?:de\\s+)?(20\\d{2})\\b').exec(texto);
    if (m) return m[1]+'-'+String(i+1).padStart(2,'0');
  }
  return null;
}
export function interpretarLocal(pregunta, disponibles) {
  if (typeof pregunta !== 'string' || pregunta.length > 1000 || !pregunta.trim()) return { necesita_aclaracion:true };
  const t=normalizar(pregunta);
  const entidades = [ [/\b(ofertas?|oferentes?)\b/,'ofertas'], [/\b(adjudicaciones?|resultados?)\b/,'resultados'], [/\b(ordenes? de compra|\boc\b)\b/,'ordenescompra'] ];
  const detectadas=entidades.filter(([re])=>re.test(t)).map(([,v])=>v);
  if (detectadas.length>1) return { necesita_aclaracion:true };
  const entidad=detectadas[0]??'procesos';
  const periodos=[...t.matchAll(/\b20\d{2}-(?:0[1-9]|1[0-2])\b/g)].map(x=>x[0]);
  for (let i=0;i<MESES.length;i++) {
    const re=new RegExp('\\b'+MESES[i]+'\\s+(?:de\\s+)?(20\\d{2})\\b','g');
    for (const m of t.matchAll(re)) periodos.push(m[1]+'-'+String(i+1).padStart(2,'0'));
  }
  const unicos=[...new Set(periodos)];
  let candidato;
  if (/\b(comparar|comparacion|evolucion|tendencia|entre meses)\b/.test(t)) {
    if (unicos.length<2) return { necesita_aclaracion:true };
    candidato={operacion:'serie',entidad,periodos:unicos.sort()};
  } else {
    const periodo=periodoEn(t);
    if (!periodo || unicos.length!==1) return { necesita_aclaracion:true };
    if (/\b(ranking|principales|mayores|top|lideres)\b/.test(t)) {
      candidato={operacion:'ranking',periodo,entidad,criterio:/\b(montos?|dinero|valor|clp)\b/.test(t)?'monto':'registros',limite:5};
    } else if (/\b(licitaciones?|compras? agiles?)\b/.test(t) && entidad==='procesos') {
      candidato={operacion:'modalidades',periodo};
    } else if (/\b(cuantas?|cuantos?|total|monto|suma|registros?|procesos?)\b/.test(t)) {
      candidato={operacion:'resumen',periodo,entidad};
    } else return { necesita_aclaracion:true };
  }
  try { return validarIntencion(candidato,disponibles); }
  catch { return { necesita_aclaracion:true }; }
}
