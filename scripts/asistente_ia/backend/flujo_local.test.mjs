import test from 'node:test';
import assert from 'node:assert/strict';
import { crearFlujoLocal } from './flujo_local.mjs';
const base='https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/';
const catalogo={fecha_publicacion:'2026-11-13',periodos:[{periodo:'2026-08',tipo:'historico',conteos:{procesos:10,ofertas:3}}]};
const procesos={periodo:'2026-08',entidad:'procesos',registros:10,registros_con_monto:8,monto_total_clp:1000,campo_monto:'monto_disponible_clp',modalidades:[['Licitación',4],['Compra Ágil',6]]};
const ofertas={periodo:'2026-08',entidad:'ofertas',registros:3,registros_con_monto:3,monto_total_clp:300,campo_monto:'monto_ofertado_clp',top_actores:[['Proveedor A',2],['Proveedor B',1]],top_actores_monto:[['Proveedor A',200],['Proveedor B',100]]};
function crear(mismatch=false){const leerJSON=async url=>{assert.ok(url.startsWith(base));if(url.endsWith('catalogo-publico.json'))return catalogo;if(url.endsWith('procesos.json'))return {...procesos,registros:mismatch?11:10};if(url.endsWith('ofertas.json'))return ofertas;throw Error('Ruta inesperada')};return crearFlujoLocal({leerJSON});}
test('pregunta de licitaciones obtiene cifra determinista y fuentes',async()=>{const r=await crear().consultar('¿Cuántas licitaciones hubo en agosto de 2026?');assert.equal(r.estado,'respondida');assert.match(r.resultado.explicacion,/4 licitaciones/);assert.equal(r.resultado.fuentes.length,2);});
test('ranking de proveedores',async()=>{const r=await crear().consultar('top proveedores por ofertas agosto de 2026');assert.equal(r.estado,'respondida');assert.match(r.resultado.explicacion,/Proveedor A/);});
test('pregunta ambigua solicita aclaración sin consultar agregados',async()=>{const r=await crear().consultar('¿Participa una persona en Mercado Público?');assert.equal(r.estado,'aclaracion');});
test('inconsistencia entre catálogo y agregado bloquea cifras',async()=>{await assert.rejects(crear(true).consultar('¿Cuántas licitaciones hubo en agosto de 2026?'),e=>e.status===503);});

const catalogoComparativo={fecha_publicacion:'2026-11-13',periodos:[
  {periodo:'2026-07',tipo:'historico',conteos:{procesos:12}},
  {periodo:'2026-08',tipo:'historico',conteos:{procesos:10}}
]};
const agregadosComparativos={
  '2026-07':{periodo:'2026-07',entidad:'procesos',registros:12,modalidades:[['Licitación',5],['Compra Ágil',7]]},
  '2026-08':{periodo:'2026-08',entidad:'procesos',registros:10,modalidades:[['Licitación',4],['Compra Ágil',6]]}
};
function comparar(mismatch=false){
  return crearFlujoLocal({leerJSON:async url=>{
    if(url.endsWith('catalogo-publico.json')) return catalogoComparativo;
    const mes=/analitica\/(2026-0[78])\/procesos.json$/.exec(url)?.[1];
    if(!mes) throw Error('Fuente inesperada');
    return {...agregadosComparativos[mes],registros:mismatch && mes==='2026-07'?13:agregadosComparativos[mes].registros};
  }});
}
test('comparación julio y agosto con año compartido, diferencia absoluta y porcentual',async()=>{
  const r=await comparar().consultar('¿Cuántas licitaciones se registraron en julio y agosto de 2026, y cuál fue la diferencia?');
  assert.equal(r.estado,'respondida');
  assert.match(r.resultado.explicacion,/2026-07: 5/);
  assert.match(r.resultado.explicacion,/2026-08: 4/);
  assert.match(r.resultado.explicacion,/disminución, 20 %/);
  assert.equal(r.resultado.fuentes.length,3);
});
test('comparación bloquea agregado inconsistente',async()=>{
  await assert.rejects(comparar(true).consultar('Licitaciones julio y agosto de 2026 diferencia'),e=>e.status===503);
});
