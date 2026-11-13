// Diagnóstico aislado de compatibilidad: una sola pregunta, sin cambios de datos ni despliegues.
// Nunca imprime texto libre del modelo, claves ni el cuerpo de la respuesta.
const url = process.env.WORKER_CHAT_URL;
if (!url || new URL(url).protocol !== 'https:') throw new Error('Endpoint HTTPS requerido');
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 25000);
let response;
try {
  response = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'origin': 'https://juliopez.github.io' },
    body: JSON.stringify({ pregunta: '¿Cuántas licitaciones hubo en agosto de 2026?' }),
    signal: controller.signal
  });
} finally { clearTimeout(timeout); }
console.log('HTTP_STATUS', response.status);
console.log('CORS_ALLOW_ORIGIN', response.headers.get('access-control-allow-origin') || '(ausente)');
if (!response.ok) throw new Error('POST /chat no disponible: HTTP ' + response.status);
const type = response.headers.get('content-type') || '';
if (!type.includes('application/json')) throw new Error('Respuesta no JSON');
const raw = await response.text();
if (raw.length > 50000) throw new Error('Respuesta demasiado extensa');
const data = JSON.parse(raw);
const compatible = data?.estado === 'respondida' &&
  typeof data.resultado?.explicacion === 'string' &&
  typeof data.resultado?.metodo === 'string' &&
  data.resultado.metodo.length > 0 &&
  Array.isArray(data.resultado?.fuentes) &&
  data.resultado.fuentes.length > 0;
const aclaracion = data?.estado === 'aclaracion' &&
  typeof (data.pregunta_aclaracion || data.mensaje) === 'string';
console.log('ESTADO_CONTRATO', typeof data?.estado === 'string' ? data.estado : '(sin estado)');
console.log('COMPATIBLE_UI_NUEVA', compatible || aclaracion);
console.log('CLAVES_PRIMER_NIVEL', Object.keys(data).sort().join(','));
console.log('TIPOS_CAMPOS', Object.fromEntries(Object.entries(data).map(([k,v])=>[k,Array.isArray(v)?'array':v===null?'null':typeof v])));
console.log('FUENTES_TIPO', Array.isArray(data.fuentes)?'array':typeof data.fuentes);
console.log('DATOS_TIPO', Array.isArray(data.datos)?'array':typeof data.datos);
console.log('METODO_PRESENTE', typeof data.metodo === 'string' && !!data.metodo.trim());
console.log('PERIODO_PRESENTE', typeof data.periodo === 'string');
if (!compatible && !aclaracion)
  throw new Error('Worker responde, pero no satisface el contrato estricto de la interfaz aislada');
if (!['*', 'https://juliopez.github.io'].includes(response.headers.get('access-control-allow-origin')))
  throw new Error('CORS no habilitado para el origen de GitHub Pages');
console.log('OK: POST /chat, contrato y CORS compatibles');
