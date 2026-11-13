// Auditoría de solo lectura de todos los agregados mensuales publicados.
// Ejecutar: node scripts/asistente_ia/backend/auditar_fuentes.mjs
import { crearMotor, ENTIDADES, rutaPublica } from './motor.mjs';

async function leerJSON(url) {
  const r = await fetch(url, { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(15000) });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${url}`);
  return r.json();
}

const catalogo = await leerJSON(rutaPublica('data/catalogo-publico.json'));
const motor = await crearMotor({ leerJSON });
const fallas = [];
let verificadas = 0;
for (const periodo of motor.periodosDisponibles) {
  for (const entidad of ENTIDADES) {
    try {
      const resumen = await motor.consultar({ operacion: 'resumen', periodo, entidad });
      verificadas++;
      if (entidad === 'procesos') {
        const mod = await motor.consultar({ operacion: 'modalidades', periodo });
        if (mod.datos.total_procesos !== resumen.datos.registros) throw new Error('Total de modalidades inconsistente');
      }
      console.log(`OK ${periodo} ${entidad}: ${resumen.datos.registros}`);
    } catch (error) {
      fallas.push({ periodo, entidad, error: error.message });
      console.error(`FALLA ${periodo} ${entidad}: ${error.message}`);
    }
  }
}
console.log(JSON.stringify({ fecha_publicacion: catalogo.fecha_publicacion, verificadas, fallas }, null, 2));
if (fallas.length) process.exitCode = 1;
