import test from 'node:test';
import assert from 'node:assert/strict';
import {crearBuscadorR2} from './lector_indice_r2.mjs';
test('R2 consulta solamente el manifiesto y el prefijo necesario',async()=>{
 const claves=[];
 const buscar=crearBuscadorR2({bucket:{get:async clave=>{
  claves.push(clave);
  const dato=clave.endsWith('manifiesto.json')
   ? JSON.stringify({periodo:'2026-10',prefijos:{ma:1},registros_origen:2})
   : JSON.stringify({clave:'makarena banares',nombre:'Makarena Bañares',periodo:'2026-10',entidad:'ofertas'})+'\n';
  return {text:async()=>dato};
 }}});
 const r=await buscar({periodo:'2026-10',consulta:'Makarena Bañares'});
 assert.equal(r.total_coincidencias,1);
 assert.deepEqual(claves,['indices-nombres/2026-10/manifiesto.json','indices-nombres/2026-10/clave-ma.ndjson']);
});
test('R2 rechaza períodos ajenos al catálogo temporal',async()=>{
 const buscar=crearBuscadorR2({bucket:{get:async()=>{throw Error('no debe leerse');}}});
 await assert.rejects(buscar({periodo:'../../secreto',consulta:'Nombre válido'}),/Período inválido/);
});
