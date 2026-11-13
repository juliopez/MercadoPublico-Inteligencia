// Escenarios analíticos aislados. Solo lectura de datos públicos; no usa Gemini.
import { crearMotor, ConsultaError } from './motor.mjs';
import { crearLectorPublico } from './lector_publico.mjs';

const leerJSON = crearLectorPublico({ ttlMs: 60_000, timeoutMs: 15_000, maxBytes: 12_000_000, maxEntradas: 40 });
const motor = await crearMotor({ leerJSON });
const meses = [...motor.periodosDisponibles].sort();
if (meses.length < 2) throw new Error('Se requieren dos períodos');
const fallos = [];
let aprobadas = 0;
async function prueba(nombre, ejecutar) {
  try { await ejecutar(); aprobadas++; console.log('OK', nombre); }
  catch (error) {
    if (error instanceof ConsultaError && error.status === 503) {
      console.log('BLOQUEADO_POR_INCONSISTENCIA', nombre, error.message);
      return;
    }
    fallos.push({ nombre, error: error.message });
    console.error('FALLO', nombre, error.message);
  }
}
function exigir(condicion, motivo) { if (!condicion) throw new Error(motivo); }
const ultimo = meses.at(-1);
const anterior = meses.at(-2);
await prueba('organismos compradores del mes reciente', async () => {
  const r = await motor.consultar({ operacion: 'ranking', periodo: ultimo, entidad: 'procesos', criterio: 'registros', limite: 5 });
  exigir(r.datos.filas.length <= 5 && r.fuentes.length === 2, 'Ranking o fuentes inválidos');
});
await prueba('proveedores por ofertas', async () => {
  const r = await motor.consultar({ operacion: 'ranking', periodo: ultimo, entidad: 'ofertas', criterio: 'registros', limite: 5 });
  exigir(r.datos.filas.every(x => x.valor >= 0), 'Conteos inválidos');
});
await prueba('proveedores por montos de órdenes de compra', async () => {
  const r = await motor.consultar({ operacion: 'ranking', periodo: ultimo, entidad: 'ordenescompra', criterio: 'monto', limite: 5 });
  exigir(r.datos.unidad === 'CLP informado' && r.datos.filas.every(x => Number.isSafeInteger(x.valor)), 'Montos inválidos');
});
await prueba('montos informados en adjudicaciones', async () => {
  const r = await motor.consultar({ operacion: 'resumen', periodo: ultimo, entidad: 'resultados' });
  exigir(r.datos.registros_con_monto <= r.datos.registros && r.datos.advertencia, 'Cobertura monetaria inválida');
});
await prueba('comparación de procesos entre dos meses', async () => {
  const r = await motor.consultar({ operacion: 'serie', entidad: 'procesos', periodos: [anterior, ultimo] });
  exigir(r.datos.length === 2 && r.datos.every(x => Number.isSafeInteger(x.registros)), 'Serie inválida');
});
await prueba('comparación de ofertas entre dos meses', async () => {
  const r = await motor.consultar({ operacion: 'serie', entidad: 'ofertas', periodos: [anterior, ultimo] });
  exigir(r.datos.length === 2, 'Serie inválida');
});
console.log('RESUMEN_ESCENARIOS', JSON.stringify({ meses: [anterior, ultimo], aprobadas, fallos }));
if (fallos.length) process.exitCode = 1;
