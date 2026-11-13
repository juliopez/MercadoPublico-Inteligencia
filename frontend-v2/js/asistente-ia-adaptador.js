// Compatibilidad aislada con el contrato del Worker actual. Sin inventar cifras ni fuentes.
export function adaptarRespuestaWorker(dato) {
  if (!dato || typeof dato !== 'object' || Array.isArray(dato)) throw new Error('Respuesta inválida');
  if (dato.estado === 'aclaracion' && typeof (dato.pregunta_aclaracion || dato.mensaje) === 'string')
    return dato;
  if (dato.estado === 'respondida' && dato.resultado &&
      typeof dato.resultado.explicacion === 'string' &&
      typeof dato.resultado.metodo === 'string' && dato.resultado.metodo.trim() &&
      Array.isArray(dato.resultado.fuentes) && dato.resultado.fuentes.length)
    return dato;
  // El Worker anterior entrega {respuesta,datos,fuentes,metodo,periodo,cobertura}.
  // No convertir respuestas sin trazabilidad o datos comprobables.
  if (typeof dato.respuesta !== 'string' || !dato.respuesta.trim() ||
      typeof dato.metodo !== 'string' || !dato.metodo.trim() ||
      typeof dato.periodo !== 'string' || !/^20\d{2}-(0[1-9]|1[0-2])$/.test(dato.periodo) ||
      !dato.datos || typeof dato.datos !== 'object' || Array.isArray(dato.datos) ||
      !dato.fuentes || !Array.isArray(dato.fuentes) || dato.fuentes.length === 0)
    throw new Error('Contrato sin trazabilidad suficiente');
  const fuentes = dato.fuentes.filter(f => {
    const ruta = typeof f === 'string' ? f : (f && typeof f === 'object' ? (f.url || f.ruta) : '');
    if (typeof ruta !== 'string') return false;
    try {
      const u = new URL(ruta, 'https://juliopez.github.io/MercadoPublico-Inteligencia/');
      return u.protocol === 'https:' && u.hostname === 'juliopez.github.io' &&
        u.pathname.startsWith('/MercadoPublico-Inteligencia/');
    } catch { return false; }
  });
  if (!fuentes.length) throw new Error('Fuentes públicas no verificables');
  return {
    estado: 'respondida',
    resultado: {
      explicacion: dato.respuesta,
      datos: dato.datos,
      fuentes,
      metodo: dato.metodo,
      periodo: dato.periodo,
      cobertura: dato.cobertura ?? null
    }
  };
}
