import { BASE, ConsultaError } from './motor.js';

// Lector de fuentes públicas: origen fijo, límite de bytes, timeout y caché de corta duración.
// Sin secretos, sin escrituras y sin llamadas a Gemini.
export function crearLectorPublico({
  fetchImpl = fetch,
  ahora = () => Date.now(),
  ttlMs = 60_000,
  timeoutMs = 8_000,
  maxBytes = 8_000_000,
  maxEntradas = 32
} = {}) {
  if (typeof fetchImpl !== 'function' || typeof ahora !== 'function') throw new TypeError('Dependencias inválidas');
  for (const n of [ttlMs, timeoutMs, maxBytes, maxEntradas])
    if (!Number.isSafeInteger(n) || n <= 0) throw new TypeError('Límites inválidos');
  const cache = new Map();
  const pendientes = new Map();
  async function descargar(url) {
    const target = new URL(url);
    if (target.origin !== new URL(BASE).origin ||
        !target.pathname.startsWith(new URL(BASE).pathname + 'data/') ||
        target.search || target.hash || target.username || target.password)
      throw new ConsultaError('Origen público no autorizado', 400);
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetchImpl(url, { signal: ctrl.signal, headers: { Accept: 'application/json' } });
      if (!res.ok) throw new ConsultaError('Fuente pública no disponible', 503);
      const size = Number(res.headers?.get('content-length'));
      if (Number.isFinite(size) && size > maxBytes) throw new ConsultaError('Fuente demasiado grande', 503);
      if (!res.body || typeof res.body.getReader !== 'function') {
        const body = await res.text();
        if (new TextEncoder().encode(body).byteLength > maxBytes) throw new ConsultaError('Fuente demasiado grande', 503);
        return JSON.parse(body);
      }
      const reader = res.body.getReader();
      const chunks = [];
      let bytes = 0;
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          bytes += value.byteLength;
          if (bytes > maxBytes) throw new ConsultaError('Fuente demasiado grande', 503);
          chunks.push(value);
        }
      } finally { reader.releaseLock(); }
      const all = new Uint8Array(bytes);
      let offset = 0;
      for (const chunk of chunks) { all.set(chunk, offset); offset += chunk.byteLength; }
      return JSON.parse(new TextDecoder().decode(all));
    } catch (e) {
      if (e instanceof ConsultaError) throw e;
      throw new ConsultaError('Error al leer fuente pública', 503);
    } finally { clearTimeout(timer); }
  }
  return async function leerJSON(url) {
    const cached = cache.get(url);
    if (cached && cached.hasta > ahora()) return structuredClone(cached.datos);
    if (!pendientes.has(url)) {
      const tarea = descargar(url).then(datos => {
        cache.delete(url);
        cache.set(url, { datos, hasta: ahora() + ttlMs });
        while (cache.size > maxEntradas) cache.delete(cache.keys().next().value);
        return datos;
      }).finally(() => pendientes.delete(url));
      pendientes.set(url, tarea);
    }
    return structuredClone(await pendientes.get(url));
  };
}
