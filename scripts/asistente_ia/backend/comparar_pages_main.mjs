// Diagnóstico de solo lectura: compara contenido HTTP de Pages con archivos del checkout.
// Ejecutar en la raíz del repositorio: node scripts/asistente_ia/backend/comparar_pages_main.mjs
import { readFile } from 'node:fs/promises';
import { BASE, ENTIDADES } from './motor.mjs';

const catalogo = JSON.parse(await readFile('frontend-v2/data/catalogo-publico.json','utf8'));
const resultados = [];
let fallas = 0;
for (const item of catalogo.periodos) {
  for (const entidad of ENTIDADES) {
    const ruta = `data/analitica/${item.periodo}/${entidad}.json`;
    const local = JSON.parse(await readFile('frontend-v2/' + ruta,'utf8'));
    const url = BASE + ruta;
    try {
      const response = await fetch(url + '?auditoria=' + encodeURIComponent(process.env.GITHUB_SHA || 'manual'), {
        headers: { 'Cache-Control':'no-cache', 'Pragma':'no-cache', Accept:'application/json' },
        signal: AbortSignal.timeout(15000)
      });
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const remoto = await response.json();
      const coinciden = remoto.registros === local.registros &&
        remoto.entidad === local.entidad && remoto.periodo === local.periodo;
      if (!coinciden) fallas++;
      resultados.push({
        periodo:item.periodo,entidad,
        main:local.registros,pages:remoto.registros,
        main_version:local.version,pages_version:remoto.version,
        coincide:coinciden,
        cache_control:response.headers.get('cache-control'),
        age:response.headers.get('age'),
        etag:response.headers.get('etag')
      });
    } catch (error) {
      fallas++;
      resultados.push({periodo:item.periodo,entidad,error:error.message});
    }
  }
}
for (const r of resultados) console.log(JSON.stringify(r));
console.log('RESUMEN',JSON.stringify({verificados:resultados.length,coincidentes:resultados.length-fallas,fallas}));
if (fallas) process.exitCode=1;
