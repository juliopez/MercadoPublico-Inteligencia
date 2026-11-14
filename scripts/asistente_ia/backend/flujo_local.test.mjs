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


const catalogoAmpliado={fecha_publicacion:'2026-11-13',periodos:[
  {periodo:'2026-07',tipo:'historico',conteos:{procesos:12,ofertas:3,resultados:2,ordenescompra:2}},
  {periodo:'2026-08',tipo:'historico',conteos:{procesos:10,ofertas:5,resultados:2,ordenescompra:3}}
]};
const agregadosAmpliados={
  '2026-07':{
    procesos:{registros:12,modalidades:[['Licitación',5],['Compra Ágil',7]]},
    ofertas:{registros:3,registros_con_monto:2,monto_total_clp:300,campo_monto:'monto_ofertado_clp'},
    resultados:{registros:2,registros_con_monto:1,monto_total_clp:200,campo_monto:'monto_adjudicado_clp'},
    ordenescompra:{registros:2,registros_con_monto:2,monto_total_clp:500,campo_monto:'monto_total_oc_clp'}
  },
  '2026-08':{
    procesos:{registros:10,modalidades:[['Licitación',4],['Compra Ágil',6]]},
    ofertas:{registros:5,registros_con_monto:4,monto_total_clp:600,campo_monto:'monto_ofertado_clp'},
    resultados:{registros:2,registros_con_monto:2,monto_total_clp:400,campo_monto:'monto_adjudicado_clp'},
    ordenescompra:{registros:3,registros_con_monto:2,monto_total_clp:900,campo_monto:'monto_total_oc_clp'}
  }
};
function ampliar(inconsistente=false){
  return crearFlujoLocal({leerJSON:async url=>{
    if(url.endsWith('catalogo-publico.json'))return catalogoAmpliado;
    const m=/analitica\/(2026-0[78])\/(procesos|ofertas|resultados|ordenescompra)\.json$/.exec(url);
    if(!m)throw Error('Ruta inesperada '+url);
    const [ , periodo, entidad]=m;
    const d=agregadosAmpliados[periodo][entidad];
    return {...d,periodo,entidad,registros:inconsistente&&periodo==='2026-08'&&entidad==='ofertas'?99:d.registros};
  }});
}
test('comparación de compras ágiles entre meses',async()=>{
  const r=await ampliar().consultar('¿Cuántas compras ágiles hubo en julio y agosto de 2026, y cuál fue la diferencia?');
  assert.equal(r.estado,'respondida');
  assert.match(r.resultado.explicacion,/2026-07: 7/);
  assert.match(r.resultado.explicacion,/2026-08: 6/);
  assert.match(r.resultado.explicacion,/disminución, 14,29 %/);
});
test('comparación de ofertas entre meses',async()=>{
  const r=await ampliar().consultar('¿Cuál fue la diferencia de ofertas entre julio y agosto de 2026?');
  assert.equal(r.estado,'respondida');
  assert.match(r.resultado.explicacion,/2026-07: 3/);
  assert.match(r.resultado.explicacion,/2026-08: 5/);
  assert.match(r.resultado.explicacion,/aumento, 66,67 %/);
});
test('montos informados de órdenes de compra, sin afirmar pagos',async()=>{
  const r=await ampliar().consultar('¿Cuál fue el monto de órdenes de compra en agosto de 2026?');
  assert.equal(r.estado,'respondida');
  assert.match(r.resultado.explicacion,/900 CLP/);
  assert.match(r.resultado.explicacion,/no son pagos comprobados/);
});
test('montos informados de ofertas y cobertura',async()=>{
  const r=await ampliar().consultar('¿Cuál fue el monto de ofertas en agosto de 2026?');
  assert.equal(r.estado,'respondida');
  assert.match(r.resultado.explicacion,/5 registros de ofertas/);
  assert.match(r.resultado.explicacion,/4 informan monto/);
  assert.match(r.resultado.explicacion,/600 CLP/);
});
test('inconsistencia de ofertas bloquea comparación y montos',async()=>{
  await assert.rejects(ampliar(true).consultar('¿Cuál fue la diferencia de ofertas entre julio y agosto de 2026?'),e=>e.status===503);
  await assert.rejects(ampliar(true).consultar('¿Cuál fue el monto de ofertas en agosto de 2026?'),e=>e.status===503);
});
