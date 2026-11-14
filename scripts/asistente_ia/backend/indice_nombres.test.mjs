import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizarNombre, construirIndiceNombres, buscarNombre } from './indice_nombres.mjs';
const lotes = [
 { entidad:'ofertas', periodo:'2026-10', parte:'data/partes/ofertas/2026-10/0001.json',
   registros:[{codigo:'123-1-COT26',proveedor:'Makarena Bañares'}, {codigo:'123-2-COT26',proveedor:'MÁKARENA  BAÑARES'}, {codigo:'123-3-COT26',proveedor:'Otra Empresa'}] },
 { entidad:'resultados', periodo:'2026-10', parte:'data/partes/resultados/2026-10/0001.json',
   registros:[{codigo:'123-1-COT26',adjudicatario:'Makarena Bañares',proveedor_seleccionado:'Makarena Bañares',validado:'Pendiente: selección histórica, no adjudicación verificada'}] }
];
test('normaliza tildes, espacios y mayúsculas',()=>assert.equal(normalizarNombre(' MÁKARENA   BAÑARES '),'makarena banares'));
test('preserva procedencia y evita duplicar dos campos de un mismo resultado',()=>{
 const indice=construirIndiceNombres(lotes);
 assert.equal(indice.length,4);
 assert.equal(indice.find(x=>x.entidad==='resultados').fila,0);
 assert.match(indice.find(x=>x.entidad==='resultados').validacion,/Pendiente/);
});
test('busca coincidencias exactas sin afirmar identidad',()=>{
 const res=buscarNombre(construirIndiceNombres(lotes),'makarena banares');
 assert.equal(res.total_coincidencias,3);
 assert.match(res.advertencia,/no acreditan identidad/);
});
test('busca coincidencias parciales y limita salida sin ocultar total',()=>{
 const res=buscarNombre(construirIndiceNombres(lotes),'Bañares',{modo:'contiene',limite:1});
 assert.equal(res.total_coincidencias,3);assert.equal(res.resultados.length,1);assert.equal(res.truncado,true);
});
test('ausencia no implica no participación fuera de cobertura',()=>{
 const res=buscarNombre(construirIndiceNombres(lotes),'Nombre Inexistente');
 assert.equal(res.total_coincidencias,0);assert.match(res.advertencia,/registros indexados/);
});
test('rechaza rutas ajenas y consultas inválidas',()=>{
 assert.throws(()=>construirIndiceNombres([{...lotes[0],parte:'https://evil.example/data.json'}]));
 assert.throws(()=>buscarNombre([], 'a'));
 assert.throws(()=>buscarNombre([], 'nombre',{limite:100000}));
});
