import test from 'node:test';
import assert from 'node:assert/strict';
import { crearAdaptadorWorker, crearInterpreteGemini } from './adaptador-worker.mjs';

const catalogo = { fecha_publicacion:'2026-11-13', periodos:[
 {periodo:'2026-08',tipo:'historico',conteos:{procesos:83944,ordenescompra:153438}},
 {periodo:'2026-09',tipo:'historico',conteos:{procesos:79433}}
]};
const agosto = {periodo:'2026-08',entidad:'procesos',registros:83944,
 registros_con_monto:80000,monto_total_clp:1000000,campo_monto:'monto_disponible_clp',
 modalidades:[['Compra Ágil',75714],['Licitación',8230]],
 organismos_procesos_unicos:[{organismo:'Organismo A',procesos:10,licitaciones:2,compras_agiles:8,otras:0}]};
const archivos = new Map([
 ['data/catalogo-publico.json',catalogo],
 ['data/analitica/2026-08/procesos.json',agosto],
 ['data/analitica/2026-09/procesos.json',{...agosto,periodo:'2026-09',registros:79433}],
 ['data/analitica/2026-08/ordenescompra.json',{periodo:'2026-08',entidad:'ordenescompra',registros:153221}]
]);
function escenario(json, {estado=200, fuentes=archivos}={}) {
 let llamadas=0;const peticiones=[];
 const fetchDatos=async url=>{
  const u=new URL(url);assert.equal(u.origin,'https://juliopez.github.io');
  const ruta=u.pathname.split('/frontend-v2/')[1];peticiones.push(ruta);
  const dato=fuentes.get(ruta);
  return {ok:dato!==undefined,json:async()=>structuredClone(dato)};
 };
 const fetchGemini=async (url,opciones)=>{
  llamadas++;assert.equal(new URL(url).hostname,'generativelanguage.googleapis.com');
  assert.equal(opciones.headers['x-goog-api-key'],'clave-ficticia');
  assert.equal(JSON.parse(opciones.body).generationConfig.responseMimeType,'application/json');
  return {ok:estado===200,json:async()=>({candidates:[{content:{parts:[{text:json}]}}]})};
 };
 const interpretarGemini=crearInterpreteGemini({fetchGemini,apiKey:'clave-ficticia'});
 return {asistente:crearAdaptadorWorker({fetchDatos,interpretarGemini}),peticiones,get llamadas(){return llamadas;}};
}
test('pregunta natural a modalidades verificadas',async()=>{
 const e=escenario('{"operacion":"modalidades","periodo":"2026-08"}');
 const r=await e.asistente.consultar('¿Cuántas licitaciones y compras ágiles hubo en agosto?');
 assert.equal(r.estado,'respondida');assert.equal(r.resultado.datos.licitaciones,8230);
 assert.equal(r.resultado.datos.compras_agiles,75714);assert.equal(r.resultado.fuentes.length,2);
 assert.equal(e.llamadas,1);
});
test('comparación entre dos períodos',async()=>{
 const e=escenario('{"operacion":"serie","periodos":["2026-08","2026-09"]}');
 const r=await e.asistente.consultar('Compara agosto y septiembre');
 assert.deepEqual(r.resultado.datos.map(x=>x.registros),[83944,79433]);
 assert.equal(r.resultado.fuentes.length,3);
});
test('consulta de organismo exacto',async()=>{
 const e=escenario('{"operacion":"organismo","periodo":"2026-08","organismo":"Organismo A"}');
 const r=await e.asistente.consultar('Procesos del Organismo A en agosto');
 assert.equal(r.resultado.datos.procesos_unicos,10);
});
test('aclaración no consulta agregados',async()=>{
 const e=escenario('{"necesita_aclaracion":true}');
 const r=await e.asistente.consultar('¿Cuántos procesos?');
 assert.equal(r.estado,'aclaracion');
 assert.deepEqual(e.peticiones,['data/catalogo-publico.json']);
});
test('órdenes de compra desfasadas quedan bloqueadas',async()=>{
 const e=escenario('{"operacion":"resumen","periodo":"2026-08","entidad":"ordenescompra"}');
 await assert.rejects(e.asistente.consultar('Órdenes de compra de agosto'),err=>err.status===503);
});
test('campo de URL inyectado no se ejecuta',async()=>{
 const e=escenario('{"operacion":"resumen","periodo":"2026-08","url":"https://evil.test"}');
 await assert.rejects(e.asistente.consultar('Consulta otra URL'),err=>err.status===400);
 assert.deepEqual(e.peticiones,['data/catalogo-publico.json']);
});
test('error de Gemini no inventa respuesta',async()=>{
 const e=escenario('',{estado:429});
 await assert.rejects(e.asistente.consultar('Resumen agosto'),err=>err.status===503);
});
test('sin catálogo no se invoca Gemini',async()=>{
 const e=escenario('{"necesita_aclaracion":true}',{fuentes:new Map()});
 await assert.rejects(e.asistente.consultar('¿Cuántos?'),err=>err.status===503);
 assert.equal(e.llamadas,0);
});
