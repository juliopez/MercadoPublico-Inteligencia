import test from 'node:test';
import assert from 'node:assert/strict';
import { crearAdaptadorWorker, crearInterpreteGemini } from './adaptador-worker.mjs';

const catalogo = { periodos: [{ periodo: '2026-08', tipo: 'historico', conteos: { procesos: 4 } }], fecha_publicacion: '2026-11-13' };
const agregado = { periodo: '2026-08', entidad: 'procesos', registros: 4, registros_con_monto: 2, monto_total_clp: 1200, campo_monto: 'monto_disponible_clp', advertencia: 'Montos informados' };
const fetchDatos = async url => ({ ok: true, json: async () => url.endsWith('catalogo-publico.json') ? catalogo : agregado });
test('adaptador ejecuta consulta validada con dos fuentes', async () => {
  const adaptador = crearAdaptadorWorker({ fetchDatos, interpretarGemini: async () => '{"operacion":"resumen","periodo":"2026-08","entidad":"procesos"}' });
  const r = await adaptador.consultar('Resumen de agosto');
  assert.equal(r.estado, 'respondida');
  assert.equal(r.resultado.datos.registros, 4);
  assert.equal(r.resultado.fuentes.length, 2);
});
test('no inventa cifras si agregado y catálogo difieren', async () => {
  const adaptador = crearAdaptadorWorker({
    fetchDatos: async url => ({ ok: true, json: async () => url.endsWith('catalogo-publico.json') ? catalogo : { ...agregado, registros: 3 } }),
    interpretarGemini: async () => '{"operacion":"resumen","periodo":"2026-08"}'
  });
  await assert.rejects(adaptador.consultar('Resumen'), e => e.status === 503);
});
test('rechaza fuente pública no disponible', async () => {
  const adaptador = crearAdaptadorWorker({ fetchDatos: async () => ({ ok: false }), interpretarGemini: async () => '{"necesita_aclaracion":true}' });
  await assert.rejects(adaptador.consultar('Resumen'), e => e.status === 503);
});
test('interpreta intención usando endpoint de Gemini y clave en cabecera', async () => {
  let llamada;
  const interpretar = crearInterpreteGemini({ apiKey: 'clave-prueba', fetchGemini: async (url, opciones) => {
    llamada = { url, opciones };
    return { ok: true, json: async () => ({ candidates: [{ content: { parts: [{ text: '{"necesita_aclaracion":true}' }] } }] }) };
  } });
  const salida = await interpretar({ instrucciones: 'Solo JSON', pregunta: '¿Cuántos?' });
  assert.equal(salida, '{"necesita_aclaracion":true}');
  assert.match(llamada.url, /generateContent$/);
  assert.equal(llamada.opciones.headers['x-goog-api-key'], 'clave-prueba');
  assert.equal(JSON.parse(llamada.opciones.body).generationConfig.responseMimeType, 'application/json');
  assert.ok(!llamada.url.includes('clave-prueba'));
});
test('Gemini falla de manera segura sin exponer respuesta ni secreto', async () => {
  const interpretar = crearInterpreteGemini({ apiKey: 'secreto', fetchGemini: async () => ({ ok: false, status: 429 }) });
  await assert.rejects(interpretar({ instrucciones: 'Solo JSON', pregunta: 'Pregunta' }), e => e.status === 503 && !e.message.includes('secreto'));
});
test('respuesta vacía de Gemini no se transforma en datos', async () => {
  const interpretar = crearInterpreteGemini({ apiKey: 'secreto', fetchGemini: async () => ({ ok: true, json: async () => ({ candidates: [] }) }) });
  await assert.rejects(interpretar({ instrucciones: 'Solo JSON', pregunta: 'Pregunta' }), e => e.status === 503);
});
