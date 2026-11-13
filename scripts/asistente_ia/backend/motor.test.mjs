import test from 'node:test';
import assert from 'node:assert/strict';
import { crearMotor, rutaPublica, ConsultaError } from './motor.mjs';

const catalogo = {fecha_publicacion:'2026-11-13T12:11:57Z',periodos:[
 {periodo:'2026-08',tipo:'historico',conteos:{procesos:83944,ofertas:432111}},
 {periodo:'2026-09',tipo:'historico',conteos:{procesos:79433,ofertas:0}}
]};
const agosto = {periodo:'2026-08',entidad:'procesos',registros:83944,
 modalidades:[['Compra Ágil',75714],['Licitación',8230]],
 organismos_procesos_unicos:[{organismo:'UNIVERSIDAD DE CHILE',procesos:2962,licitaciones:24,compras_agiles:2938,otras:0}]};
const septiembre = {periodo:'2026-09',entidad:'procesos',registros:79433,modalidades:[['Compra Ágil',72459],['Licitación',6974]]};
const ofertas = {periodo:'2026-08',entidad:'ofertas',registros:432111,registros_con_monto:430000,monto_total_clp:1234,campo_monto:'monto_ofertado_clp',advertencia:'Monto informado'};
function motorCon(override={}) {
 const files={'data/catalogo-publico.json':catalogo,'data/analitica/2026-08/procesos.json':agosto,
 'data/analitica/2026-09/procesos.json':septiembre,'data/analitica/2026-08/ofertas.json':ofertas,...override};
 return crearMotor({leerJSON:async url=>{const key=new URL(url).pathname.split('/frontend-v2/')[1];if(!(key in files))throw new Error('Fixture inexistente');return structuredClone(files[key]);}});
}
test('rechaza rutas no permitidas',()=>assert.throws(()=>rutaPublica('https://example.org/a'),ConsultaError));
test('conteo agosto y fuentes',async()=>{const m=await motorCon();const r=await m.consultar({operacion:'modalidades',periodo:'2026-08'});assert.equal(r.datos.total_procesos,83944);assert.equal(r.datos.licitaciones,8230);assert.equal(r.datos.compras_agiles,75714);assert.equal(r.fuentes.length,2);});
test('organismo exacto',async()=>{const m=await motorCon();const r=await m.consultar({operacion:'organismo',periodo:'2026-08',organismo:'universidad de chile'});assert.equal(r.datos.procesos_unicos,2962);});
test('resumen ofertas',async()=>{const m=await motorCon();const r=await m.consultar({operacion:'resumen',periodo:'2026-08',entidad:'ofertas'});assert.equal(r.datos.registros,432111);});
test('período inexistente',async()=>{const m=await motorCon();await assert.rejects(m.consultar({operacion:'resumen',periodo:'2026-05'}),{status:404});});
test('serie exige dos meses distintos',async()=>{const m=await motorCon();await assert.rejects(m.consultar({operacion:'serie',periodos:['2026-08','2026-08']}),{status:400});});
test('serie dos meses',async()=>{const m=await motorCon();const r=await m.consultar({operacion:'serie',periodos:['2026-08','2026-09']});assert.deepEqual(r.datos.map(x=>x.registros),[83944,79433]);});
test('rechaza totales inconsistentes',async()=>{const m=await motorCon({'data/analitica/2026-08/procesos.json':{...agosto,registros:1}});await assert.rejects(m.consultar({operacion:'modalidades',periodo:'2026-08'}),{status:503});});
test('rechaza modalidades que no suman',async()=>{const m=await motorCon({'data/analitica/2026-08/procesos.json':{...agosto,modalidades:[['Licitación',1]]}});await assert.rejects(m.consultar({operacion:'modalidades',periodo:'2026-08'}),{status:503});});
test('no inventa organismos',async()=>{const m=await motorCon();await assert.rejects(m.consultar({operacion:'organismo',periodo:'2026-08',organismo:'organismo inexistente'}),{status:404});});

test('etiquetas compuestas de modalidades',async()=>{
 const m=await motorCon({'data/analitica/2026-08/procesos.json':{
  ...agosto,modalidades:[['Compra Ágil (API)',75714],['Licitación Pública',8230]]
 }});
 const r=await m.consultar({operacion:'modalidades',periodo:'2026-08'});
 assert.equal(r.datos.licitaciones,8230);
 assert.equal(r.datos.compras_agiles,75714);
});
test('agregado de OC desfasado queda bloqueado',async()=>{
 const m=await motorCon({'data/catalogo-publico.json':{
  ...catalogo,periodos:[{...catalogo.periodos[0],conteos:{...catalogo.periodos[0].conteos,ordenescompra:153438}},catalogo.periodos[1]]
 },'data/analitica/2026-08/ordenescompra.json':{
  periodo:'2026-08',entidad:'ordenescompra',registros:153221
 }});
 await assert.rejects(m.consultar({operacion:'resumen',periodo:'2026-08',entidad:'ordenescompra'}),{status:503});
});
test('serie rechaza entidad inválida',async()=>{
 const m=await motorCon();
 await assert.rejects(m.consultar({operacion:'serie',entidad:'privado',periodos:['2026-08','2026-09']}),{status:400});
});
