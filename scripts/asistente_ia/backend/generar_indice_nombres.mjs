// Generador explícito, fuera de producción. Lee únicamente partes públicas locales.
// Uso: node scripts/asistente_ia/backend/generar_indice_nombres.mjs <raiz-frontend-v2> <periodo> <directorio-salida>
// No altera el catálogo, las partes, ETL ni el frontend.
import { readFile, writeFile, mkdir, rename, rm, stat } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { construirIndiceNombres } from './indice_nombres.mjs';

// Generación incremental: solo una parte de origen en memoria por iteración.
export async function generarIndiceParticionado({ raiz, periodo, destino, leerArchivo = async ruta => JSON.parse(await readFile(ruta, 'utf8')) }) {
  if (!/^20\d{2}-(0[1-9]|1[0-2])$/.test(periodo)) throw new TypeError('Período inválido');
  if (typeof destino !== 'string' || !destino.trim()) throw new TypeError('Destino inválido');
  const catalogo = await leerArchivo(join(raiz, 'data/catalogo-publico.json'));
  const seleccionado = catalogo?.periodos?.find(p => p.periodo === periodo);
  if (!seleccionado) throw new Error('Período ausente del catálogo');
  const carpeta = resolve(destino);
  const temporal = carpeta + '.temporal';
  try { await stat(carpeta); throw new Error('El destino ya existe; no se sobrescribe'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  await mkdir(temporal, { recursive: false });
  const manifiesto = { version: 1, periodo, fecha_catalogo: catalogo.fecha_publicacion, archivos: [], registros_origen: 0, entradas: 0 };
  try {
    for (const entidad of ['ofertas', 'resultados', 'ordenescompra']) {
      const partes = seleccionado.partes?.[entidad];
      if (!Array.isArray(partes)) throw new Error('Faltan partes publicadas de ' + entidad);
      let total = 0;
      for (const parte of partes) {
        if (typeof parte !== 'string' || !new RegExp('^data/partes/' + entidad + '/' + periodo + '/[a-z0-9_-]+\\.json$').test(parte)) throw new Error('Ruta no autorizada');
        const registros = await leerArchivo(join(raiz, parte));
        if (!Array.isArray(registros)) throw new Error('Parte inválida: ' + parte);
        const entradas = construirIndiceNombres([{ entidad, periodo, parte, registros }]);
        const nombre = entidad + '-' + parte.split('/').at(-1);
        await writeFile(join(temporal, nombre), JSON.stringify(entradas));
        manifiesto.archivos.push({ archivo: nombre, origen: parte, registros: registros.length, entradas: entradas.length });
        manifiesto.registros_origen += registros.length;
        manifiesto.entradas += entradas.length;
        total += registros.length;
      }
      if (total !== seleccionado.conteos?.[entidad]) throw new Error('Conteo inconsistente para ' + entidad);
    }
    await writeFile(join(temporal, 'manifiesto.json'), JSON.stringify(manifiesto));
    await rename(temporal, carpeta);
    return manifiesto;
  } catch (error) { await rm(temporal, { recursive: true, force: true }); throw error; }
}

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
  if (!raiz || !periodo || !salida) { console.error('Uso: node generar_indice_nombres.mjs <raiz> <periodo> <directorio-salida>'); process.exitCode = 2; }
  else {
    try {
      const indice = await generarIndiceParticionado({ raiz: resolve(raiz), periodo, destino: resolve(salida) });
      console.log(JSON.stringify({ periodo, registros_origen: indice.registros_origen, entradas: indice.entradas, archivos: indice.archivos.length, salida: resolve(salida) }));
    } catch (error) { console.error(error.message); process.exitCode = 1; }
  }
}
