import test from 'node:test';
import assert from 'node:assert/strict';
import { crearMotor } from './motor.mjs';
import { crearLectorPublico } from './lector_publico.mjs';

const catalogo = {
  fecha_publicacion: '2026-11-13T12:00:00Z',
  periodos: [{periodo:'2026-08',tipo:'historico',conteos:{procesos:10,ordenescompra:5}}]
};
const procesos = {
  periodo:'2026-08',entidad:'procesos',registros:10,registros_con_monto:8,
  monto_total_clp:1000,campo_monto:'monto_disponible_clp',
  modalidades:[['Licitación',4],['Compra Ágil',6]],
  organismos_procesos_unicos:[{organismo:'Entidad A',procesos:10,licitaciones:4,compras_agiles:6,otras:0}]
};
const oc = {
  periodo:'2026-08',entidad:'ordenescompra',registros:4,registros_con_monto:4,
  monto_total_clp:2000,campo_monto:'monto_total_oc_clp'
};
function preparar() {
  let llamadas = 0;
  const fetchImpl = async url => {
    llamadas++;
    const ruta = new URL(url).pathname.split('/frontend-v2/')[1];
    const archivos = {
      'data/catalogo-publico.json':catalogo,
      'data/analitica/2026-08/procesos.json':procesos,
      'data/analitica/2026-08/ordenescompra.json':oc
    };
    if (!(ruta in archivos)) return new Response('No encontrado',{status:404});
    return new Response(JSON.stringify(archivos[ruta]),{status:200,headers:{'content-type':'application/json'}});
  };
  return {leerJSON:crearLectorPublico({fetchImpl}),llamadas:()=>llamadas};
}
test('integración lector y motor: modalidades y caché',async()=>{
  const p=preparar();
  const motor=await crearMotor({leerJSON:p.leerJSON});
  const a=await motor.consultar({operacion:'modalidades',periodo:'2026-08'});
  const b=await motor.consultar({operacion:'resumen',periodo:'2026-08'});
  assert.equal(a.datos.licitaciones,4);
  assert.equal(a.datos.compras_agiles,6);
  assert.equal(b.datos.monto_total_clp,1000);
  assert.equal(p.llamadas(),2);
});
test('integración lector y motor: OC desfasadas no entregan cifras',async()=>{
  const p=preparar();
  const motor=await crearMotor({leerJSON:p.leerJSON});
  await assert.rejects(motor.consultar({operacion:'resumen',periodo:'2026-08',entidad:'ordenescompra'}),{status:503});
});
