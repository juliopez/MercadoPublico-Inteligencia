// Índice de acceso por nombre: permite leer únicamente el prefijo solicitado.
// Módulo aislado; no publica datos ni modifica procesos operativos.
import { normalizarNombre } from './indice_nombres.mjs';
export function prefijoNombre(nombre) {
  const clave = normalizarNombre(nombre);
  if (!clave) throw new TypeError('Nombre vacío');
  return [...clave].slice(0, 2).map(c => /^[a-z0-9]$/.test(c) ? c : '_').join('');
}
export function particionarPorNombre(entradas) {
  if (!Array.isArray(entradas)) throw new TypeError('Entradas inválidas');
  const partes = new Map();
  for (const entrada of entradas) {
    if (!entrada || typeof entrada.clave !== 'string') throw new TypeError('Entrada inválida');
    const prefijo = prefijoNombre(entrada.clave);
    if (!partes.has(prefijo)) partes.set(prefijo, []);
    partes.get(prefijo).push(entrada);
  }
  return partes;
}
export async function buscarPorPrefijo({ consulta, leerParte, modo = 'exacto', limite = 20 }) {
  if (typeof leerParte !== 'function' || !['exacto', 'contiene'].includes(modo) ||
      !Number.isSafeInteger(limite) || limite < 1 || limite > 100)
    throw new TypeError('Parámetros inválidos');
  if (modo !== 'exacto') throw new Error('Búsqueda contiene requiere un índice invertido adicional');
  const clave = normalizarNombre(consulta);
  if (clave.length < 3) throw new TypeError('Consulta demasiado corta');
  const prefijo = prefijoNombre(clave);
  const entradas = await leerParte(prefijo);
  if (!Array.isArray(entradas)) throw new TypeError('Parte de índice inválida');
  let total = 0;
  const resultados = [];
  for (const entrada of entradas) {
    if (entrada.clave !== clave) continue;
    total++;
    if (resultados.length < limite) resultados.push(entrada);
  }
  return { consulta, modo, total_coincidencias: total, resultados, truncado: total > limite,
    advertencia: 'Coincidencias textuales; no acreditan identidad personal ni adjudicación verificada.' };
}
