// Integración aislada del asistente IA en la sección 07 del Observatorio V2.
// No altera los módulos de consulta, ETL, publicaciones ni el estado de las búsquedas.
import { crearAsistenteUI } from './asistente-ia-ui.js?v=20261114-integracion1';

const ENDPOINT = 'https://observatorio-mercado-publico-ia.julio-c-lopez-n-1972.workers.dev/chat';

async function consultar(pregunta) {
  const controlador = new AbortController();
  const limite = setTimeout(() => controlador.abort(), 30000);
  try {
    const respuesta = await fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pregunta }),
      signal: controlador.signal
    });
    if (!respuesta.ok) throw new Error('Worker HTTP ' + respuesta.status);
    const dato = await respuesta.json();
    if (dato?.estado === 'aclaracion' && typeof dato.pregunta_aclaracion === 'string') return dato;
    if (dato?.estado === 'respondida' && dato.resultado && typeof dato.resultado === 'object') return dato;
    throw new Error('Contrato de respuesta no reconocido');
  } finally {
    clearTimeout(limite);
  }
}

const contenedor = document.getElementById('asistente-ia-contenedor');
if (contenedor) crearAsistenteUI({ contenedor, consultar, habilitado: true });
