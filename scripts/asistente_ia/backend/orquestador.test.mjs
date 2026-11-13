import test from 'node:test';
import assert from 'node:assert/strict';
import { crearOrquestador } from './orquestador.mjs';
import { ConsultaError } from './motor.mjs';

const meses = ['2026-08','2026-09'];
const fuentes = ['https://ejemplo.test/catalogo.json','https://ejemplo.test/agregado.json'];
const motor = {
  periodosDisponibles: meses,
  async consultar(intencion) {
    return { datos: { registros: 83944 }, fuentes, metodo: 'resumen_agregado', periodo: intencion.periodo };
  }
};
test('consulta válida produce resultado determinista con fuentes', async () => {
  let recibido;
  const puente = crearOrquestador({ motor: { ...motor, consultar: async i => { recibido = i; return motor.consultar(i); } }, interpretar: async p => {
    assert.match(p.instrucciones, /Períodos permitidos/);
    return '{"operacion":"resumen","periodo":"2026-08","entidad":"procesos"}';
  } });
  const r = await puente.consultar('¿Cuántos procesos hubo en agosto?');
  assert.equal(r.estado, 'respondida');
  assert.equal(r.resultado.datos.registros, 83944);
  assert.deepEqual(r.resultado.fuentes, fuentes);
  assert.deepEqual(recibido, { operacion: 'resumen', periodo: '2026-08', entidad: 'procesos' });
});
test('solicitud de aclaración no llama al motor', async () => {
  const puente = crearOrquestador({ motor: { periodosDisponibles: meses, consultar: () => { throw Error('No debe ejecutarse'); } }, interpretar: async () => '{"necesita_aclaracion":true}' });
  const r = await puente.consultar('¿Cuántos?');
  assert.equal(r.estado, 'aclaracion');
  assert.deepEqual(r.fuentes, []);
});
test('rechaza respuesta de modelo con operación desconocida', async () => {
  const puente = crearOrquestador({ motor, interpretar: async () => '{"operacion":"borrar","periodo":"2026-08"}' });
  await assert.rejects(puente.consultar('borrar'), ConsultaError);
});
test('rechaza respuesta con URL inyectada', async () => {
  const puente = crearOrquestador({ motor, interpretar: async () => '{"operacion":"resumen","periodo":"2026-08","url":"https://evil.test"}' });
  await assert.rejects(puente.consultar('datos'), ConsultaError);
});
test('rechaza resultado sin fuentes', async () => {
  const puente = crearOrquestador({ motor: { ...motor, consultar: async () => ({ datos: {}, fuentes: [], metodo: 'resumen_agregado' }) }, interpretar: async () => '{"operacion":"resumen","periodo":"2026-08"}' });
  await assert.rejects(puente.consultar('datos'), e => e.status === 503);
});
test('rechaza período inexistente antes de consultar datos', async () => {
  const puente = crearOrquestador({ motor, interpretar: async () => '{"operacion":"resumen","periodo":"2026-01"}' });
  await assert.rejects(puente.consultar('datos'), ConsultaError);
});
test('rechaza preguntas excesivamente largas antes de llamar al modelo', async () => {
  const puente = crearOrquestador({ motor, interpretar: async () => { throw Error('No debe llamarse'); } });
  await assert.rejects(puente.consultar('x'.repeat(1001)), ConsultaError);
});
test('propaga indisponibilidad del motor sin inventar cifras', async () => {
  const puente = crearOrquestador({ motor: { ...motor, consultar: async () => { throw new ConsultaError('Agregado inconsistente',503); } }, interpretar: async () => '{"operacion":"resumen","periodo":"2026-08"}' });
  await assert.rejects(puente.consultar('datos'), e => e.status === 503);
});
