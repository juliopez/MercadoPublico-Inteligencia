import test from 'node:test';
import assert from 'node:assert/strict';
import { adaptarRespuestaWorker } from './asistente-ia-adaptador.js';
const fuente = 'https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/data/analitica/2026-08/procesos.json';
const legado = { respuesta:'Hay 8230 licitaciones.', datos:{licitaciones:8230}, fuentes:[fuente], metodo:'conteo_determinista_agregado', periodo:'2026-08', cobertura:'catálogo' };
test('transforma contrato legado preservando datos y método',()=>{
 const r=adaptarRespuestaWorker(legado);
 assert.equal(r.estado,'respondida');
 assert.deepEqual(r.resultado.datos,legado.datos);
 assert.equal(r.resultado.metodo,legado.metodo);
 assert.equal(r.resultado.explicacion,legado.respuesta);
});
test('acepta contrato nuevo trazable',()=> {
 const r={estado:'respondida',resultado:{explicacion:'x',metodo:'m',fuentes:[fuente]}};
 assert.equal(adaptarRespuestaWorker(r),r);
});
test('rechaza ausencia de datos o método',()=>{
 assert.throws(()=>adaptarRespuestaWorker({...legado,datos:null}));
 assert.throws(()=>adaptarRespuestaWorker({...legado,metodo:''}));
});
test('rechaza fuentes externas y periodos inválidos',()=>{
 assert.throws(()=>adaptarRespuestaWorker({...legado,fuentes:['https://example.com/fuente']}));
 assert.throws(()=>adaptarRespuestaWorker({...legado,periodo:'ayer'}));
});
test('descarta fuentes ajenas y mantiene las públicas',()=>{
 const r=adaptarRespuestaWorker({...legado,fuentes:['https://example.com/',fuente]});
 assert.deepEqual(r.resultado.fuentes,[fuente]);
});
