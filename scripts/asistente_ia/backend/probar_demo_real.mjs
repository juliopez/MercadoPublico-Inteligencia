// Smoke test de solo lectura sobre fuentes públicas reales, sin Gemini ni Worker.
import assert from 'node:assert/strict';
import { crearLectorPublico } from './lector_publico.mjs';
import { crearFlujoLocal } from './flujo_local.mjs';
import { rutaPublica, ConsultaError } from './motor.mjs';
const leerJSON=crearLectorPublico({timeoutMs:15000});
const catalogo=await leerJSON(rutaPublica('data/catalogo-publico.json'));
assert.ok(Array.isArray(catalogo.periodos) && catalogo.periodos.length>0,'Catálogo sin períodos');
console.log('CATALOGO_OK',catalogo.periodos.map(p=>p.periodo).join(','));
const mes=catalogo.periodos.find(p=>p.periodo==='2026-08')?.periodo ?? catalogo.periodos[0].periodo;
const pregunta=`¿Cuántas licitaciones hubo en ${mes}?`;
const flujo=crearFlujoLocal({leerJSON});
try {
  const r=await flujo.consultar(pregunta);
  assert.equal(r.estado,'respondida');
  assert.ok(r.resultado?.fuentes?.length>=2);
  assert.match(r.resultado.explicacion,/\d/);
  console.log('RESPUESTA_REAL_VERIFICADA',mes,r.resultado.metodo);
} catch (e) {
  if (e instanceof ConsultaError && e.status===503) {
    console.log('RESPUESTA_BLOQUEADA_POR_INCONSISTENCIA',mes,e.message);
  } else throw e;
}
