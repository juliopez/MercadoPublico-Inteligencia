import test from 'node:test';
import assert from 'node:assert/strict';
import { prefijoNombre, particionarPorNombre, buscarPorPrefijo } from './indice_por_clave.mjs';

const entradas = [
 { clave:'makarena banares', nombre:'Makarena Bañares', entidad:'ofertas', fila:0 },
 { clave:'makarena banares', nombre:'MAKARENA BANARES', entidad:'resultados', fila:2 },
 { clave:'empresa diferente', nombre:'Empresa Diferente', entidad:'ordenescompra', fila:1 }
];
test('prefijo normalizado es estable con tildes y mayúsculas', () => {
 assert.equal(prefijoNombre('MÁKARENA Bañares'),'ma');
 assert.equal(prefijoNombre('empresa diferente'),'em');
 assert.throws(() => prefijoNombre('ab'),/corto/);
});
test('particiona entradas por nombre sin perder procedencia', () => {
 const partes = particionarPorNombre(entradas);
 assert.equal(partes.get('ma').length,2);
 assert.equal(partes.get('em').length,1);
 assert.equal(partes.get('ma')[1].fila,2);
});
test('búsqueda exacta solo solicita un prefijo y conserva el total', async () => {
 const partes = particionarPorNombre(entradas);
 const leidos = [];
 const respuesta = await buscarPorPrefijo({ consulta:'Makarena Bañares', limite:1, leerParte:async prefijo => {
   leidos.push(prefijo); return partes.get(prefijo) ?? [];
 }});
 assert.deepEqual(leidos,['ma']);
 assert.equal(respuesta.total_coincidencias,2);
 assert.equal(respuesta.resultados.length,1);
 assert.equal(respuesta.truncado,true);
});
test('no promete búsqueda contiene sin índice invertido', async () => {
 await assert.rejects(buscarPorPrefijo({ consulta:'Bañares', modo:'contiene', leerParte:async () => [] }),/índice invertido/);
});
