// Adaptador aislado compatible con Workers. No contiene secretos ni publica rutas.
// La instancia se crea por petición y recibe dependencias explícitas.
import { crearMotor, ConsultaError } from './motor.mjs';
import { crearOrquestador } from './orquestador.mjs';

export function crearAdaptadorWorker({ fetchDatos, interpretarGemini }) {
  if (typeof fetchDatos !== 'function' || typeof interpretarGemini !== 'function')
    throw new TypeError('Se requieren adaptadores de datos y Gemini');
  async function leerJSON(url) {
    const respuesta = await fetchDatos(url);
    if (!respuesta || !respuesta.ok) throw new ConsultaError('Fuente pública no disponible', 503);
    const dato = await respuesta.json();
    if (!dato || typeof dato !== 'object') throw new ConsultaError('Fuente pública inválida', 503);
    return dato;
  }
  return Object.freeze({
    async consultar(pregunta) {
      const motor = await crearMotor({ leerJSON });
      return crearOrquestador({ motor, interpretar: interpretarGemini }).consultar(pregunta);
    }
  });
}

// Utilidad opcional para un Worker futuro: no se conecta a ninguna API por sí misma.
// Un token real se obtiene exclusivamente de env y nunca se incluye en respuestas.
export function crearInterpreteGemini({ fetchGemini, apiKey, modelo = 'gemini-3.5-flash' }) {
  if (typeof fetchGemini !== 'function' || typeof apiKey !== 'string' || !apiKey.trim())
    throw new TypeError('Configuración de Gemini inválida');
  if (!/^gemini-[a-z0-9.-]{1,50}$/.test(modelo)) throw new TypeError('Modelo inválido');
  return async ({ instrucciones, pregunta }) => {
    const url = 'https://generativelanguage.googleapis.com/v1beta/models/' + modelo + ':generateContent';
    const respuesta = await fetchGemini(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-goog-api-key': apiKey },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: instrucciones }] },
        contents: [{ role: 'user', parts: [{ text: pregunta }] }],
        generationConfig: { responseMimeType: 'application/json', temperature: 0, maxOutputTokens: 256 }
      })
    });
    if (!respuesta?.ok) throw new ConsultaError('Servicio de interpretación temporalmente no disponible', 503);
    const dato = await respuesta.json();
    const partes = dato?.candidates?.[0]?.content?.parts;
    const texto = Array.isArray(partes) ? partes.filter(x => typeof x?.text === 'string').map(x => x.text).join('') : '';
    if (!texto) throw new ConsultaError('Gemini no devolvió una intención válida', 503);
    return texto;
  };
}
