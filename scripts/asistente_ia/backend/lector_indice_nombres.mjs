// Lector local aislado de índices por prefijo. No modifica fuentes ni producción.
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { buscarPorPrefijo } from './indice_por_clave.mjs';

export async function buscarEnIndiceLocal({ directorio, consulta, limite = 20, modo = 'exacto' }) {
  if (typeof directorio !== 'string' || !directorio.trim()) throw new TypeError('Directorio inválido');
  const manifiesto = JSON.parse(await readFile(join(directorio, 'manifiesto.json'), 'utf8'));
  if (!/^20\d{2}-(0[1-9]|1[0-2])$/.test(manifiesto?.periodo) || !manifiesto?.prefijos || typeof manifiesto.prefijos !== 'object')
    throw new Error('Manifiesto inválido');
  const respuesta = await buscarPorPrefijo({
    consulta, limite, modo,
    leerParte: async prefijo => {
      if (!Object.hasOwn(manifiesto.prefijos, prefijo)) return [];
      const contenido = await readFile(join(directorio, 'clave-' + prefijo + '.ndjson'), 'utf8');
      return contenido.trim() ? contenido.trim().split('\n').map(linea => JSON.parse(linea)) : [];
    }
  });
  for (const registro of respuesta.resultados) {
    if (registro.periodo !== manifiesto.periodo) throw new Error('Período inconsistente en índice');
  }
  return { ...respuesta, periodo: manifiesto.periodo, cobertura: { tipo: 'indice_local', fecha_catalogo: manifiesto.fecha_catalogo, registros_origen: manifiesto.registros_origen } };
}
