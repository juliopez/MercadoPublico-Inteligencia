// Índice de participantes en Cloudflare R2 privado: no expone el corpus por Pages.
import { buscarPorPrefijo } from './indice_por_clave.mjs';
const PERIODO=/^20\d{2}-(0[1-9]|1[0-2])$/;
export function crearBuscadorR2({bucket}) {
 if(!bucket || typeof bucket.get!=='function') throw new TypeError('Binding R2 no configurado');
 return async ({periodo,consulta,limite=20,modo='exacto'})=>{
  if(!PERIODO.test(periodo)) throw new TypeError('Período inválido');
  const raiz='indices-nombres/'+periodo+'/';
  const leer=async clave=>{
    const objeto=await bucket.get(raiz+clave);
    if(!objeto) throw new Error('Índice privado no disponible');
    return objeto.text();
  };
  const manifiesto=JSON.parse(await leer('manifiesto.json'));
  if(manifiesto?.periodo!==periodo || !manifiesto.prefijos || !Number.isSafeInteger(manifiesto.registros_origen))
   throw new Error('Manifiesto privado inválido');
  const respuesta=await buscarPorPrefijo({
   consulta,limite,modo,
   leerParte:async prefijo=>{
    if(!Object.hasOwn(manifiesto.prefijos,prefijo)) return [];
    const contenido=await leer('clave-'+prefijo+'.ndjson');
    return contenido.trim()?contenido.trim().split('\n').map(JSON.parse):[];
   }
  });
  if(respuesta.resultados.some(x=>x.periodo!==periodo)) throw new Error('Índice privado inconsistente');
  return respuesta;
 };
}
