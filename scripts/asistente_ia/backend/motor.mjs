// Motor determinista aislado: no modifica datos ni consulta Gemini.
export const BASE = 'https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/';
export const ENTIDADES = Object.freeze(['procesos', 'ofertas', 'resultados', 'ordenescompra']);
export const PERIODO = /^20\d{2}-(0[1-9]|1[0-2])$/;

export class ConsultaError extends Error {
  constructor(message, status = 422) { super(message); this.name = 'ConsultaError'; this.status = status; }
}

export function rutaPublica(ruta) {
  if (!/^data\/(?:catalogo-publico\.json|analitica\/20\d{2}-(?:0[1-9]|1[0-2])\/(?:procesos|ofertas|resultados|ordenescompra)\.json)$/.test(ruta))
    throw new ConsultaError('Ruta de datos no autorizada', 400);
  return new URL(ruta, BASE).toString();
}

export async function crearMotor({ leerJSON }) {
  if (typeof leerJSON !== 'function') throw new TypeError('leerJSON debe ser función');
  const catalogo = await leerJSON(rutaPublica('data/catalogo-publico.json'));
  if (!Array.isArray(catalogo?.periodos)) throw new ConsultaError('Catálogo inválido', 503);
  const disponibles = new Map();
  for (const p of catalogo.periodos) {
    if (!PERIODO.test(p.periodo) || disponibles.has(p.periodo)) throw new ConsultaError('Períodos inválidos', 503);
    disponibles.set(p.periodo, p);
  }
  async function agregado(periodo, entidad) {
    if (!PERIODO.test(periodo) || !ENTIDADES.includes(entidad)) throw new ConsultaError('Consulta inválida', 400);
    const p = disponibles.get(periodo);
    if (!p) throw new ConsultaError('Período no publicado', 404);
    const d = await leerJSON(rutaPublica(`data/analitica/${periodo}/${entidad}.json`));
    if (d?.periodo !== periodo || d?.entidad !== entidad || !Number.isSafeInteger(d.registros) || d.registros < 0 || d.registros !== p.conteos?.[entidad])
      throw new ConsultaError('Inconsistencia entre catálogo y agregado', 503);
    return { d, p };
  }
  const fuentes = (periodo, entidad) => [
    rutaPublica('data/catalogo-publico.json'),
    rutaPublica(`data/analitica/${periodo}/${entidad}.json`)
  ];
  function respuesta(periodo, entidad, p, datos, metodo) {
    return { periodo, entidad, datos, cobertura: { tipo: p.tipo, actualizado: catalogo.fecha_publicacion }, fuentes: fuentes(periodo, entidad), metodo };
  }
  async function consultar({ operacion, periodo, entidad = 'procesos', organismo, periodos }) {
    if (!['resumen', 'modalidades', 'organismo', 'serie'].includes(operacion)) throw new ConsultaError('Operación no admitida', 400);
    if (operacion === 'serie') {
      if (!Array.isArray(periodos) || periodos.length < 2 || periodos.length > 12 || new Set(periodos).size !== periodos.length || periodos.some(x => !PERIODO.test(x))) throw new ConsultaError('Períodos de serie inválidos', 400);
      const valores = await Promise.all(periodos.map(async mes => {
        const { d } = await agregado(mes, entidad);
        return { periodo: mes, registros: d.registros };
      }));
      return { entidad, datos: valores, cobertura: { actualizado: catalogo.fecha_publicacion }, fuentes: [...new Set(periodos.flatMap(mes => fuentes(mes, entidad)))], metodo: 'serie_determinista' };
    }
    const { d, p } = await agregado(periodo, entidad);
    if (operacion === 'resumen') {
      if (!Number.isSafeInteger(d.registros_con_monto) || d.registros_con_monto < 0 || d.registros_con_monto > d.registros ||
          !Number.isSafeInteger(d.monto_total_clp) || d.monto_total_clp < 0 ||
          typeof d.campo_monto !== 'string' || !d.campo_monto)
        throw new ConsultaError('Indicadores monetarios inválidos', 503);
      return respuesta(periodo, entidad, p, { registros: d.registros, registros_con_monto: d.registros_con_monto, monto_total_clp: d.monto_total_clp, campo_monto: d.campo_monto, advertencia: d.advertencia }, 'resumen_agregado');
    }
    if (entidad !== 'procesos') throw new ConsultaError('Operación disponible solo para procesos', 400);
    if (operacion === 'modalidades') {
      if (!Array.isArray(d.modalidades)) throw new ConsultaError('Modalidades ausentes', 503);
      const totales = { licitaciones: 0, compras_agiles: 0, otras_modalidades: 0 };
      let suma = 0;
      for (const par of d.modalidades) {
        if (!Array.isArray(par) || par.length !== 2 || typeof par[0] !== 'string' || !Number.isSafeInteger(par[1]) || par[1] < 0) throw new ConsultaError('Modalidades inválidas', 503);
        const clave = par[0].normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
        if (clave.includes('licitacion')) totales.licitaciones += par[1];
        else if (clave.includes('compra agil')) totales.compras_agiles += par[1];
        else totales.otras_modalidades += par[1];
        suma += par[1];
      }
      if (suma !== d.registros) throw new ConsultaError('Total de modalidades inconsistente', 503);
      return respuesta(periodo, entidad, p, { total_procesos: d.registros, ...totales }, 'conteo_determinista_agregado');
    }
    if (typeof organismo !== 'string' || organismo.trim().length < 3 || organismo.length > 200) throw new ConsultaError('Organismo inválido', 400);
    if (!Array.isArray(d.organismos_procesos_unicos)) throw new ConsultaError('Índice de organismos no disponible', 503);
    const canon = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim().replace(/\s+/g, ' ');
    const coincidencias = d.organismos_procesos_unicos.filter(x => typeof x.organismo === 'string' && canon(x.organismo) === canon(organismo));
    if (coincidencias.length !== 1) throw new ConsultaError(coincidencias.length ? 'Organismo ambiguo' : 'Organismo no encontrado; se requiere nombre exacto', 404);
    const x = coincidencias[0];
    for (const campo of ['procesos', 'licitaciones', 'compras_agiles', 'otras']) if (!Number.isSafeInteger(x[campo]) || x[campo] < 0) throw new ConsultaError('Indicadores de organismo inválidos', 503);
    if (x.licitaciones + x.compras_agiles + x.otras !== x.procesos) throw new ConsultaError('Total de organismo inconsistente', 503);
    return respuesta(periodo, entidad, p, { organismo: x.organismo, procesos_unicos: x.procesos, licitaciones: x.licitaciones, compras_agiles: x.compras_agiles, otras_modalidades: x.otras }, 'organismo_exacto_agregado');
  }
  return { consultar, periodosDisponibles: [...disponibles.keys()] };
}
