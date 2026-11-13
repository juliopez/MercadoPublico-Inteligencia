import test from 'node:test';
import assert from 'node:assert/strict';
import { crearLectorPublico } from './lector_publico.mjs';
import { rutaPublica } from './motor.mjs';

const url = rutaPublica('data/catalogo-publico.json');
const respuesta = value => new Response(JSON.stringify(value), { status: 200, headers: { 'content-type': 'application/json' } });

test('caché evita segunda descarga y protege contra mutación', async () => {
  let llamadas = 0;
  const leer = crearLectorPublico({fetchImpl:async () => { llamadas++; return respuesta({ a: 1 }); }});
  const primero = await leer(url);
  primero.a = 99;
  assert.equal((await leer(url)).a, 1);
  assert.equal(llamadas, 1);
});
test('consolida solicitudes simultáneas', async () => {
  let llamadas = 0;
  const leer = crearLectorPublico({fetchImpl:async () => { llamadas++; return respuesta({ ok: true }); }});
  await Promise.all([leer(url), leer(url), leer(url)]);
  assert.equal(llamadas, 1);
});
test('rechaza origen externo antes de hacer fetch', async () => {
  const leer = crearLectorPublico({fetchImpl:async () => { throw new Error('No debió consultar'); }});
  await assert.rejects(leer('https://example.com/data/catalogo-publico.json'), {status:400});
});
test('rechaza fuentes demasiado grandes', async () => {
  const leer = crearLectorPublico({maxBytes:8,fetchImpl:async () => respuesta({texto:'demasiado largo'})});
  await assert.rejects(leer(url), {status:503});
});
test('no cachea errores de red', async () => {
  let llamadas = 0;
  const leer = crearLectorPublico({fetchImpl:async () => {llamadas++; if(llamadas===1) throw new Error('sin red'); return respuesta({ok:true});}});
  await assert.rejects(leer(url),{status:503});
  assert.deepEqual(await leer(url),{ok:true});
  assert.equal(llamadas,2);
});
test('caché expira', async () => {
  let t = 0, llamadas = 0;
  const leer = crearLectorPublico({ahora:()=>t,ttlMs:10,fetchImpl:async()=>respuesta({n:++llamadas})});
  assert.equal((await leer(url)).n,1);
  t=11;
  assert.equal((await leer(url)).n,2);
});
