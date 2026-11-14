// Worker experimental unificado: Gemini interpreta, motor público calcula.
// No incluye secretos; desplegar solo con autorización y GEMINI_API_KEY configurada.
import { crearAdaptadorWorker, crearInterpreteGemini } from '../backend/adaptador-worker.mjs';
import { crearBuscadorR2 } from '../backend/lector_indice_r2.mjs';

const ORIGEN = 'https://juliopez.github.io';
const cabeceras = { 'Content-Type':'application/json; charset=utf-8', 'Access-Control-Allow-Origin':ORIGEN, 'Access-Control-Allow-Methods':'POST, OPTIONS', 'Access-Control-Allow-Headers':'Content-Type', 'Cache-Control':'no-store' };
const respuesta = (dato,status=200) => new Response(JSON.stringify(dato),{status,headers:cabeceras});
export default {
  async fetch(request,env) {
    const url=new URL(request.url);
    if(request.method==='OPTIONS') return new Response(null,{status:204,headers:cabeceras});
    if(url.pathname==='/health' && request.method==='GET') return respuesta({estado:'ok',integracion:'gemini-intencion-motor'});
    if(url.pathname!=='/chat' || request.method!=='POST') return respuesta({error:'Ruta no disponible'},404);
    if(Number(request.headers.get('content-length')||0)>4096) return respuesta({error:'Solicitud demasiado extensa'},413);
    if(!env.GEMINI_API_KEY) return respuesta({error:'Gemini no configurado'},503);
    try {
      const body=await request.json();
      const pregunta=body?.pregunta;
      if(typeof pregunta!=='string'||!pregunta.trim()||pregunta.length>1000) return respuesta({estado:'aclaracion',pregunta_aclaracion:'Escribe una pregunta de hasta 1.000 caracteres.'},400);
      const interprete=crearInterpreteGemini({fetchGemini:fetch,apiKey:env.GEMINI_API_KEY,modelo:env.GEMINI_MODEL||'gemini-3.5-flash'});
      const asistente=crearAdaptadorWorker({fetchDatos:fetch,interpretarGemini:interprete, ...(env.NOMBRES_BUCKET ? {buscarIndiceNombres:crearBuscadorR2({bucket:env.NOMBRES_BUCKET})} : {})});
      const resultado=await asistente.consultar(pregunta);
      if(resultado.estado==='aclaracion') return respuesta({estado:'aclaracion',pregunta_aclaracion:resultado.mensaje});
      // La explicación se genera solo desde datos calculados, no desde texto libre de Gemini.
      return respuesta(resultado);
    } catch(error) {
      // Diagnóstico estructurado sin exponer preguntas, respuestas ni credenciales.
      const etapa = error?.status === 503 ? 'dependencia_externa' : 'interpretacion';
      const motivosValidacion = Object.freeze({
        'Intención no es un objeto':'INTENCION_TIPO',
        'Operación no admitida':'OPERACION_NO_ADMITIDA',
        'Catálogo de períodos inválido':'CATALOGO_PERIODOS',
        'Campo de intención no permitido':'CAMPO_NO_PERMITIDO',
        'Entidad no admitida':'ENTIDAD_NO_ADMITIDA',
        'Períodos de serie inválidos':'SERIE_PERIODOS',
        'Modalidad comparativa inválida':'MODALIDAD_INVALIDA',
        'Período no publicado o ausente':'PERIODO_NO_DISPONIBLE',
        'Nombre de organismo inválido':'ORGANISMO_INVALIDO',
        'Criterio inválido':'CRITERIO_INVALIDO',
        'Límite inválido':'LIMITE_INVALIDO',
        'Respuesta del modelo inválida':'RESPUESTA_MODELO_INVALIDA',
        'Gemini no devolvió JSON válido':'JSON_INVALIDO',
        'Pregunta inválida':'PREGUNTA_INVALIDA',
        'Períodos disponibles inválidos':'PERIODOS_INVALIDOS'
      });
      const motivo = Object.prototype.hasOwnProperty.call(motivosValidacion,error?.message) ? motivosValidacion[error.message] : 'NO_CLASIFICADO';
      console.error('ASISTENTE_WORKER_FALLO', JSON.stringify({ etapa, codigo: Number(error?.status) || 500, tipo: error?.name || 'Error', motivo }));
      return respuesta({estado:'aclaracion',pregunta_aclaracion:error?.status===503?'Los datos o Gemini no están disponibles para una respuesta verificada.':'No se pudo interpretar la consulta. Especifica período, entidad y operación.'});
    }
  }
};
