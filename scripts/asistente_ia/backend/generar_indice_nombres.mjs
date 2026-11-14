// Generador explícito, fuera de producción. Lee únicamente partes públicas locales.
// Uso: node scripts/asistente_ia/backend/generar_indice_nombres.mjs <raiz-frontend-v2> <periodo> <archivo-salida>
// No altera el catálogo, las partes, ETL ni el frontend.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, join, dirname } from 'node:path';
import { construirIndiceNombres } from './indice_nombres.mjs';

export async function generarIndice({ raiz, periodo, leerArchivo = async ruta => JSON.parse(await readFile(ruta, 'utf8')) }) {
  if (!/^20\d{2}-(0[1-9]|1[0-2])$/.test(periodo)) throw new TypeError('Período inválido');
  const catalogo = await leerArchivo(join(raiz, 'data/catalogo-publico.json'));
  const seleccionado = catalogo?.periodos?.find(p => p.periodo === periodo);
  if (!seleccionado) throw new Error('Período ausente del catálogo');
  const lotes = [];
  for (const entidad of ['ofertas', 'resultados', 'ordenescompra']) {
    const partes = seleccionado.partes?.[entidad];
    if (!Array.isArray(partes)) throw new Error('Faltan partes publicadas de ' + entidad);
    for (const parte of partes) {
      if (typeof parte !== 'string' || !new RegExp('^data/partes/' + entidad + '/' + periodo + '/[a-z0-9_-]+\\.json$').test(parte))
        throw new Error('Ruta no autorizada');
      const registros = await leerArchivo(join(raiz, parte));
      if (!Array.isArray(registros)) throw new Error('Parte inválida: ' + parte);
      lotes.push({ entidad, periodo, parte, registros });
    }
  }
  return { version: 1, periodo, fecha_catalogo: catalogo.fecha_publicacion, entradas: construirIndiceNombres(lotes) };
}
if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) {
  const [raiz, periodo, salida] = process.argv.slice(2);
  if (!raiz || !periodo || !salida) { console.error('Uso: node generar_indice_nombres.mjs <raiz> <periodo> <salida>'); process.exitCode = 2; }
  else {
    try {
      const indice = await generarIndice({ raiz: resolve(raiz), periodo });
      await mkdir(dirname(resolve(salida)), { recursive: true });
      await writeFile(resolve(salida), JSON.stringify(indice));
      console.log(JSON.stringify({ periodo, entradas: indice.entradas.length, salida: resolve(salida) }));
    } catch (error) { console.error(error.message); process.exitCode = 1; }
  }
}
