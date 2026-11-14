// Prototipo aislado de índice de nombres. No lee red, no modifica datos productivos.
const CAMPOS = Object.freeze({
  ofertas: ['proveedor'],
  resultados: ['adjudicatario', 'proveedor_seleccionado'],
  ordenescompra: ['proveedor']
});
export function normalizarNombre(valor) {
  return String(valor ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/[^a-z0-9ñ]+/g, ' ').trim().replace(/\s+/g, ' ');
}
function validarRuta(entidad, periodo, parte) {
  if (!Object.hasOwn(CAMPOS, entidad) || !/^20\d{2}-(0[1-9]|1[0-2])$/.test(periodo) ||
      typeof parte !== 'string' || !new RegExp('^data/partes/' + entidad + '/' + periodo + '/[a-z0-9_-]+\\.json$').test(parte))
    throw new TypeError('Procedencia de registro inválida');
}
export function construirIndiceNombres(lotes) {
  if (!Array.isArray(lotes)) throw new TypeError('Lotes inválidos');
  const entradas = [];
  for (const lote of lotes) {
    const { entidad, periodo, parte, registros } = lote ?? {};
    validarRuta(entidad, periodo, parte);
    if (!Array.isArray(registros)) throw new TypeError('Registros inválidos');
    for (let fila = 0; fila < registros.length; fila++) {
      const registro = registros[fila];
      if (!registro || typeof registro !== 'object' || Array.isArray(registro)) continue;
      const nombres = new Set();
      for (const campo of CAMPOS[entidad]) {
        const original = registro[campo];
        if (typeof original !== 'string' || !original.trim()) continue;
        const clave = normalizarNombre(original);
        if (!clave || nombres.has(clave)) continue;
        nombres.add(clave);
        entradas.push({
          clave, nombre: original.trim(), entidad, periodo, parte, fila,
          codigo: String(registro.codigo_oc ?? registro.codigo ?? '').slice(0, 120),
          validacion: entidad === 'resultados' ? String(registro.validado ?? '').slice(0, 180) : null
        });
      }
    }
  }
  return entradas.sort((a, b) => a.clave.localeCompare(b.clave) || a.periodo.localeCompare(b.periodo) || a.parte.localeCompare(b.parte) || a.fila - b.fila);
}
export function buscarNombre(indice, consulta, { limite = 20, modo = 'exacto' } = {}) {
  if (!Array.isArray(indice) || typeof consulta !== 'string' || consulta.trim().length < 3 || consulta.length > 200 ||
      !Number.isSafeInteger(limite) || limite < 1 || limite > 100 || !['exacto', 'contiene'].includes(modo))
    throw new TypeError('Parámetros de búsqueda inválidos');
  const clave = normalizarNombre(consulta);
  if (clave.length < 3) throw new TypeError('Nombre inválido');
  const coincidentes = indice.filter(e => modo === 'exacto' ? e.clave === clave : e.clave.includes(clave));
  return { consulta, modo, total_coincidencias: coincidentes.length, resultados: coincidentes.slice(0, limite),
    truncado: coincidentes.length > limite,
    advertencia: 'Coincidencias textuales en los registros indexados; no acreditan identidad personal ni adjudicación verificada.' };
}
