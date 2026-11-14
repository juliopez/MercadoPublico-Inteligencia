// Genera índices para todos los períodos publicados en una carpeta temporal aislada.
// No altera los datos de origen ni publica resultados.
import { readFile, mkdir, stat } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { generarIndiceParticionado } from './generar_indice_nombres.mjs';
export async function generarHistoricoNombres({ raiz, destino, leerArchivo }) {
  if (typeof destino !== 'string' || !destino.trim()) throw new TypeError('Destino inválido');
  const origen = resolve(raiz), salida = resolve(destino);
  if (salida === origen || salida.startsWith(origen + '/')) throw new Error('Destino dentro del frontend');
  try { await stat(salida); throw new Error('Destino existente'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  const leer = leerArchivo ?? (async ruta => JSON.parse(await readFile(ruta,'utf8')));
  const catalogo = await leer(join(origen,'data/catalogo-publico.json'));
  if (!Array.isArray(catalogo?.periodos) || !catalogo.periodos.length) throw new Error('Catálogo sin períodos');
  const periodos = catalogo.periodos.map(x=>x.periodo);
  if (new Set(periodos).size !== periodos.length || periodos.some(x=>!/^20\d{2}-(0[1-9]|1[0-2])$/.test(x))) throw new Error('Períodos inválidos');
  await mkdir(salida);
  const manifiestos = [];
  for (const periodo of periodos) {
    const manifiesto = await generarIndiceParticionado({raiz:origen,periodo,destino:join(salida,periodo),leerArchivo:leer});
    manifiestos.push(manifiesto);
  }
  return manifiestos;
}
if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) {
 const [raiz,destino] = process.argv.slice(2);
 if (!raiz || !destino) { console.error('Uso: node generar_historico_nombres.mjs <frontend-v2> <directorio-nuevo>'); process.exitCode=2; }
 else {
   try {
     const manifiestos = await generarHistoricoNombres({raiz,destino});
     console.log(JSON.stringify({periodos:manifiestos.map(x=>x.periodo),registros:manifiestos.reduce((a,x)=>a+x.registros_origen,0),entradas:manifiestos.reduce((a,x)=>a+x.entradas,0)}));
   } catch(error) { console.error(error.message); process.exitCode=1; }
 }
}
