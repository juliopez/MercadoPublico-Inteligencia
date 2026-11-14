// Worker experimental unificado: Gemini interpreta, motor público calcula.
// No incluye secretos; desplegar solo con autorización y GEMINI_API_KEY configurada.
import { crearAdaptadorWorker, crearInterpreteGemini } from '../backend/adaptador-worker.mjs';

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
      const asistente=crearAdaptadorWorker({fetchDatos:fetch,interpretarGemini:interprete});
      const resultado=await asistente.consultar(pregunta);
      if(resultado.estado==='aclaracion') return respuesta({estado:'aclaracion',pregunta_aclaracion:resultado.mensaje});
      // La explicación se genera solo desde datos calculados, no desde texto libre de Gemini.
      return respuesta(resultado);
    } catch(error) {
      return respuesta({estado:'aclaracion',pregunta_aclaracion:error?.status===503?'Los datos o Gemini no están disponibles para una respuesta verificada.':'No se pudo interpretar la consulta. Especifica período, entidad y operación.'});
    }
  }
};
