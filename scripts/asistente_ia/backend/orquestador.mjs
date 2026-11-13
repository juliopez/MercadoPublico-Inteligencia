// Puente aislado: Gemini interpreta; el motor determinista calcula.
// El texto del modelo nunca se ejecuta ni se utiliza para construir URLs.
import { ConsultaError } from './motor.mjs';
import { crearPromptIntencion, interpretarRespuestaGemini } from './intencion.mjs';

export function crearOrquestador({ motor, interpretar }) {
  if (!motor || typeof motor.consultar !== 'function' || !Array.isArray(motor.periodosDisponibles))
    throw new TypeError('Motor determinista inválido');
  if (typeof interpretar !== 'function') throw new TypeError('Intérprete inválido');
  return Object.freeze({
    async consultar(pregunta) {
      const prompt = crearPromptIntencion(pregunta, motor.periodosDisponibles);
      // interpretar es un adaptador inyectado, no una llamada a producción.
      const texto = await interpretar(prompt);
      const intencion = interpretarRespuestaGemini(texto, motor.periodosDisponibles);
      if (intencion.necesita_aclaracion === true)
        return { estado: 'aclaracion', mensaje: 'Indica el período y los datos necesarios para precisar la consulta.', fuentes: [] };
      const resultado = await motor.consultar(intencion);
      if (!resultado || !Array.isArray(resultado.fuentes) || !resultado.fuentes.length ||
          typeof resultado.metodo !== 'string' || !resultado.metodo)
        throw new ConsultaError('Resultado sin trazabilidad verificable', 503);
      return { estado: 'respondida', intencion, resultado };
    }
  });
}
