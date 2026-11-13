// Prueba funcional de solo lectura contra GitHub Pages. Sin cambios productivos ni Gemini.
import { crearMotor, ENTIDADES, ConsultaError } from './motor.mjs';
import { crearLectorPublico } from './lector_publico.mjs';

const leerJSON = crearLectorPublico({ ttlMs: 60_000, timeoutMs: 15_000, maxBytes: 12_000_000, maxEntradas: 40 });
const motor = await crearMotor({ leerJSON });
const meses = motor.periodosDisponibles;
if (meses.length < 2) throw new Error('Se necesitan al menos dos períodos públicos');
let comprobaciones = 0;
const fallas = [];
async function verificar(etiqueta, fn) {
  try {
    await fn();
    comprobaciones++;
    console.log('OK', etiqueta);
  } catch (e) {
    fallas.push({ etiqueta, error: e.message, status: e.status });
    console.error('FALLA', etiqueta, e.message);
  }
}
function exigir(condicion, descripcion) {
  if (!condicion) throw new Error(descripcion);
}
for (const mes of meses) {
  for (const entidad of ENTIDADES) {
    await verificar(`resumen ${mes} ${entidad}`, async () => {
      const r = await motor.consultar({ operacion: 'resumen', periodo: mes, entidad });
      exigir(Number.isSafeInteger(r.datos.registros) && r.datos.registros >= 0, 'Registros inválidos');
      exigir(Number.isSafeInteger(r.datos.monto_total_clp) && r.datos.monto_total_clp >= 0, 'Monto inválido');
      exigir(r.fuentes.length === 2 && r.metodo === 'resumen_agregado', 'Trazabilidad inválida');
    });
    for (const criterio of ['registros', 'monto']) {
      await verificar(`ranking ${criterio} ${mes} ${entidad}`, async () => {
        const r = await motor.consultar({ operacion: 'ranking', periodo: mes, entidad, criterio, limite: 5 });
        exigir(r.datos.filas.length <= 5, 'Ranking excede límite');
        exigir(r.datos.filas.every((fila, i) => fila.posicion === i + 1), 'Posiciones inválidas');
      });
    }
  }
  await verificar(`modalidades ${mes}`, async () => {
    const r = await motor.consultar({ operacion: 'modalidades', periodo: mes });
    const d = r.datos;
    exigir(d.licitaciones + d.compras_agiles + d.otras_modalidades === d.total_procesos, 'Modalidades no cuadran');
  });
  await verificar(`organismo real ${mes}`, async () => {
    const url = new URL(`data/analitica/${mes}/procesos.json`, 'https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/').toString();
    const d = await leerJSON(url);
    const primero = d.organismos_procesos_unicos?.find(x => x.procesos > 0 && x.organismo?.length >= 3);
    exigir(!!primero, 'No existe organismo real en agregado');
    const r = await motor.consultar({ operacion: 'organismo', periodo: mes, organismo: primero.organismo });
    exigir(r.datos.procesos_unicos === primero.procesos, 'Conteo de organismo diferente');
  });
}
await verificar('serie de todos los meses', async () => {
  const r = await motor.consultar({ operacion: 'serie', entidad: 'procesos', periodos: meses });
  exigir(r.datos.length === meses.length, 'Serie incompleta');
});
await verificar('período inexistente rechazado', async () => {
  try {
    await motor.consultar({ operacion: 'resumen', periodo: '2020-01' });
    throw new Error('Aceptó período inexistente');
  } catch (e) {
    if (!(e instanceof ConsultaError) || e.status !== 404) throw e;
  }
});
console.log('RESUMEN', JSON.stringify({ meses: meses.length, comprobaciones, fallas: fallas.length, detalles: fallas }));
if (fallas.length) process.exitCode = 1;
