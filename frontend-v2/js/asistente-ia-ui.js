// Formatea resultados deterministas sin alterar cifras ni inventar explicaciones.
export function formatearResultadoAsistente(resultado) {
  if (!resultado || typeof resultado !== 'object') return 'No hay resultados verificables.';
  if (typeof resultado.explicacion === 'string' && resultado.explicacion.trim()) return resultado.explicacion;
  const formato = n => new Intl.NumberFormat('es-CL', { maximumFractionDigits: 2 }).format(n);
  const fecha = resultado.cobertura?.actualizado;
  const actualizado = typeof fecha === 'string' && !Number.isNaN(Date.parse(fecha))
    ? '\nActualización de datos: ' + new Intl.DateTimeFormat('es-CL', {dateStyle:'medium', timeZone:'America/Santiago'}).format(new Date(fecha)) : '';
  const periodoTexto = periodo => {
    if (typeof periodo !== 'string' || !/^\d{4}-(0[1-9]|1[0-2])$/.test(periodo)) return periodo || 'período no especificado';
    const [anio, mes] = periodo.split('-').map(Number);
    return new Intl.DateTimeFormat('es-CL', {month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(Date.UTC(anio,mes-1,1)));
  };
  const datos = resultado.datos;
  if (Array.isArray(datos)) {
    if (!datos.length || !datos.every(x => x && typeof x.periodo === 'string' && typeof x.registros === 'number' && Number.isFinite(x.registros)))
      return 'No hay una serie temporal verificable para presentar.';
    const filas = datos.map(x => periodoTexto(x.periodo) + ': ' + formato(x.registros));
    if (datos.length === 2 && datos[0].registros > 0) {
      const variacion = (datos[1].registros - datos[0].registros) / datos[0].registros * 100;
      filas.push('Variación entre ambos períodos: ' + (variacion > 0 ? '+' : '') + formato(variacion) + '%');
    }
    return 'Comparación de ' + (resultado.modalidad === 'licitaciones' ? 'licitaciones' : resultado.modalidad === 'compras_agiles' ? 'compras ágiles' : resultado.entidad || 'registros') + ':\n' + filas.join('\n') + actualizado;
  }
  if (!datos || typeof datos !== 'object') return 'No hay datos verificables para presentar.';
  if (Array.isArray(datos.filas)) {
    if (!datos.filas.length) return 'El ranking no contiene registros.';
    const filas = datos.filas.map(x => x.posicion + '. ' + x.actor + ': ' + formato(x.valor));
    const unidad = datos.unidad === 'CLP informado' ? 'montos informados en CLP' : 'registros';
    return 'Ranking de ' + (resultado.entidad || 'actores') + ' por ' + unidad + ' (' + periodoTexto(resultado.periodo) + '):\n' + filas.join('\n') + actualizado;
  }
  const nombres = {
    total_procesos: 'Total de procesos', licitaciones: 'Licitaciones',
    compras_agiles: 'Compras ágiles', otras_modalidades: 'Otras modalidades',
    registros: 'Registros', registros_con_monto: 'Registros con monto',
    monto_total_clp: 'Monto total informado (CLP)', procesos_unicos: 'Procesos únicos'
  };
  const filas = Object.entries(datos).filter(([, valor]) => typeof valor === 'number' && Number.isFinite(valor))
    .map(([clave, valor]) => (nombres[clave] || clave.replaceAll('_', ' ')) + ': ' + formato(valor));
  if (typeof datos.organismo === 'string') filas.unshift('Organismo: ' + datos.organismo);
  if (typeof datos.campo_monto === 'string') filas.push('Campo monetario: ' + datos.campo_monto);
  if (typeof datos.advertencia === 'string' && datos.advertencia.trim()) filas.push('Advertencia: ' + datos.advertencia);
  if (!filas.length) return 'Resultados verificados de ' + periodoTexto(resultado.periodo) + '. No hay cifras compatibles para mostrar.';
  return 'Resultados verificados de ' + periodoTexto(resultado.periodo) + ':\n' + filas.join('\n') + actualizado;
}

// Componente aislado de interfaz conversacional. No se monta por defecto.
// La integración productiva requiere habilitación explícita y endpoint aprobado.
export function crearAsistenteUI({ contenedor, consultar, habilitado = false } = {}) {
  if (!contenedor || typeof contenedor.replaceChildren !== 'function') throw new TypeError('Contenedor inválido');
  if (typeof consultar !== 'function') throw new TypeError('Consulta no configurada');
  if (!habilitado) return { activo: false, destruir() {} };
  const doc = contenedor.ownerDocument;
  const nodo = (tag, texto, clase) => {
    const el = doc.createElement(tag);
    if (texto !== undefined) el.textContent = texto;
    if (clase) el.className = clase;
    return el;
  };
  const panel = nodo('section', undefined, 'asistente-ia');
  panel.setAttribute('aria-label', 'Asistente de consulta del Observatorio');
  const titulo = nodo('h2', 'Consultar al asistente');
  const aviso = nodo('p', 'Respuestas basadas en datos públicos verificados. Los montos informados no equivalen necesariamente a pagos.', 'asistente-ia-aviso');
  const historial = nodo('div', undefined, 'asistente-ia-historial');
  historial.setAttribute('role', 'log');
  historial.setAttribute('aria-live', 'polite');
  historial.setAttribute('aria-relevant', 'additions');
  const formulario = nodo('form');
  const etiqueta = nodo('label', 'Escribe tu pregunta');
  const entrada = nodo('textarea');
  entrada.name = 'pregunta';
  entrada.rows = 3;
  entrada.maxLength = 1000;
  entrada.required = true;
  entrada.placeholder = 'Ej.: ¿Cuántas licitaciones hubo en agosto de 2026?';
  etiqueta.append(entrada);
  const enviar = nodo('button', 'Consultar');
  enviar.type = 'submit';
  const estado = nodo('p', '', 'asistente-ia-estado');
  estado.setAttribute('role', 'status');
  formulario.append(etiqueta, enviar, estado);
  panel.append(titulo, aviso, historial, formulario);
  contenedor.replaceChildren(panel);
  let activo = true, pendiente = false;
  const mensaje = (autor, texto) => {
    const item = nodo('div', undefined, 'asistente-ia-mensaje');
    item.append(nodo('strong', autor), nodo('p', texto));
    historial.append(item);
  };
  const alEnviar = async evento => {
    evento.preventDefault();
    if (!activo || pendiente) return;
    const pregunta = entrada.value.trim();
    if (!pregunta) return;
    pendiente = true; enviar.disabled = true; entrada.disabled = true;
    estado.textContent = 'Consultando fuentes…';
    mensaje('Pregunta', pregunta);
    try {
      const respuesta = await consultar(pregunta);
      if (!activo) return;
      if (respuesta?.estado === 'aclaracion') {
        mensaje('Asistente', respuesta.pregunta_aclaracion || respuesta.mensaje || 'Especifica el período o el tipo de registro.');
      } else if (respuesta?.estado === 'respondida' && respuesta.resultado) {
        const r = respuesta.resultado;
        mensaje('Asistente', formatearResultadoAsistente(r));
        if (Array.isArray(r.fuentes)) {
          const item = nodo('div', undefined, 'asistente-ia-fuentes');
          item.append(nodo('strong', 'Fuentes: '));
          for (const fuente of r.fuentes) {
            const ruta = typeof fuente === 'string' ? fuente : (fuente.url || fuente.ruta || '');
            if (!ruta) continue;
            // Solo enlaces HTTPS del dominio público conocido, nunca URLs arbitrarias de la respuesta.
            try {
              const url = new URL(ruta, 'https://juliopez.github.io/MercadoPublico-Inteligencia/');
              if (url.protocol !== 'https:' || url.hostname !== 'juliopez.github.io') continue;
              const a = nodo('a', 'Ver fuente');
              a.href = url.href; a.target = '_blank'; a.rel = 'noopener noreferrer';
              item.append(a, doc.createTextNode(' '));
            } catch {}
          }
          historial.append(item);
        }
      } else {
        mensaje('Asistente', 'No se pudo verificar una respuesta. Intenta reformular la consulta.');
      }
      entrada.value = '';
    } catch {
      if (activo) mensaje('Asistente', 'La consulta no está disponible en este momento. No se muestran cifras sin verificar.');
    } finally {
      if (activo) { pendiente = false; enviar.disabled = false; entrada.disabled = false; estado.textContent = ''; }
    }
  };
  formulario.addEventListener('submit', alEnviar);
  return { activo: true, destruir() { activo = false; formulario.removeEventListener('submit', alEnviar); contenedor.replaceChildren(); } };
}
