// Adaptador de lectura HTTP: solo lee índices publicados y versionados, sin publicar nada.
// El publicador debe proporcionar manifiesto y archivos clave-xx.ndjson bajo esta ruta.
import { buscarPorPrefijo } from './indice_por_clave.mjs';
const PERIODO = /^20\d{2}-(0[1-9]|1[0-2])$/;
const BASE = 'https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/data/indices-nombres/';
export function crearBuscadorPublico({ fetchIndice, base = BASE }) {
  if (typeof fetchIndice !== 'function') throw new TypeError('Lector HTTP inválido');
  const urlBase = new URL(base);
  if (urlBase.protocol !== 'https:' || urlBase.hostname !== 'juliopez.github.io' ||
      !urlBase.pathname.startsWith('/MercadoPublico-Inteligencia/frontend-v2/data/indices-nombres/'))
    throw new TypeError('Origen de índices no autorizado');
  return async ({ periodo, consulta, limite = 20, modo = 'exacto' }) => {
    if (!PERIODO.test(periodo)) throw new TypeError('Período inválido');
    const ruta = new URL(periodo + '/', urlBase);
    const leer = async url => {
      const respuesta = await fetchIndice(url);
      if (!respuesta?.ok) throw new Error('Índice publicado no disponible');
      return respuesta.text();
    };
    const manifiesto = JSON.parse(await leer(new URL('manifiesto.json',ruta).toString()));
    if (manifiesto?.periodo !== periodo || !manifiesto.prefijos || !Number.isSafeInteger(manifiesto.registros_origen))
      throw new Error('Manifiesto público inválido');
    const resultado = await buscarPorPrefijo({
      consulta, limite, modo,
      leerParte: async prefijo => {
        if (!Object.hasOwn(manifiesto.prefijos,prefijo)) return [];
        const contenido = await leer(new URL('clave-' + prefijo + '.ndjson',ruta).toString());
        return contenido.trim() ? contenido.trim().split('\n').map(JSON.parse) : [];
      }
    });
    if (resultado.resultados.some(x=>x.periodo!==periodo)) throw new Error('Índice público inconsistente');
    return resultado;
  };
}
