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
        mensaje('Asistente', r.explicacion || JSON.stringify(r.datos));
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
