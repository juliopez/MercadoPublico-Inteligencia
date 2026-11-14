import test from 'node:test';
import assert from 'node:assert/strict';
import { generarIndice, generarIndiceParticionado } from './generar_indice_nombres.mjs';

const raiz = '/tmp/frontend-v2-fixture';
const ruta = (entidad) => 'data/partes/' + entidad + '/2026-10/0001.json';
const catalogo = {
  fecha_publicacion: '2026-11-14T08:46:24Z',
  periodos: [{ periodo: '2026-10', partes: Object.fromEntries(
    ['ofertas', 'resultados', 'ordenescompra'].map(entidad => [entidad, [ruta(entidad)]])
  ) }]
};
const archivos = {
  'data/catalogo-publico.json': catalogo,
  [ruta('ofertas')]: [{ codigo:'123-1-COT26', proveedor:'Makarena Bañares' }],
  [ruta('resultados')]: [{ codigo:'123-1-COT26', adjudicatario:'MÁKARENA BAÑARES', validado:'pendiente' }],
  [ruta('ordenescompra')]: [{ codigo_oc:'OC-100', proveedor:'Otra empresa' }]
};
const leerArchivo = async archivo => {
  const clave = archivo.slice(raiz.length + 1);
  if (!Object.hasOwn(archivos, clave)) throw new Error('Parte no encontrada');
  return structuredClone(archivos[clave]);
};
test('genera índice de tres entidades con procedencia por parte y fila', async () => {
  const indice = await generarIndice({ raiz, periodo:'2026-10', leerArchivo });
  assert.equal(indice.entradas.length, 3);
  assert.equal(indice.fecha_catalogo, catalogo.fecha_publicacion);
  assert.deepEqual(indice.entradas.filter(x => x.clave === 'makarena banares').map(x => x.entidad).sort(), ['ofertas', 'resultados']);
  assert.ok(indice.entradas.every(x => x.parte.includes('/2026-10/') && x.fila === 0));
});
test('rechaza períodos sin catálogo y partes faltantes', async () => {
  await assert.rejects(generarIndice({raiz, periodo:'2026-09', leerArchivo}), /Período ausente/);
  const roto = structuredClone(catalogo);
  delete roto.periodos[0].partes.ofertas;
  await assert.rejects(generarIndice({raiz, periodo:'2026-10', leerArchivo: async archivo => archivo.endsWith('catalogo-publico.json') ? roto : leerArchivo(archivo)}), /Faltan partes/);
});
test('rechaza rutas externas en el catálogo', async () => {
  const roto = structuredClone(catalogo);
  roto.periodos[0].partes.ofertas = ['https://example.com/evil.json'];
  await assert.rejects(generarIndice({raiz, periodo:'2026-10', leerArchivo: async archivo => archivo.endsWith('catalogo-publico.json') ? roto : leerArchivo(archivo)}), /Ruta no autorizada/);
});

test('generación incremental crea partes y manifiesto con conteos exactos', async () => {
 const { mkdtemp, readFile, rm } = await import('node:fs/promises');
 const { tmpdir } = await import('node:os');
 const { join } = await import('node:path');
 const raizTemporal = await mkdtemp(join(tmpdir(), 'indice-test-'));
 const destino = join(raizTemporal, 'indice');
 const fixture = structuredClone(catalogo);
 fixture.periodos[0].conteos = { ofertas:1, resultados:1, ordenescompra:1 };
 try {
   const res = await generarIndiceParticionado({raiz, periodo:'2026-10', destino, leerArchivo: async archivo => archivo.endsWith('catalogo-publico.json') ? fixture : leerArchivo(archivo)});
   assert.equal(res.registros_origen,3);
   assert.equal(res.archivos.length,3);
   const indice = JSON.parse(await readFile(join(destino,'ofertas-0001.json'),'utf8'));
   assert.equal(indice[0].nombre,'Makarena Bañares');
   const manifiesto = JSON.parse(await readFile(join(destino,'manifiesto.json'),'utf8'));
   assert.equal(manifiesto.entradas,3);
   assert.equal(manifiesto.prefijos.ma,2);
   const porClave = (await readFile(join(destino,'clave-ma.ndjson'),'utf8')).trim().split('\\n').map(JSON.parse);
   assert.equal(porClave.length,2);
 } finally { await rm(raizTemporal,{recursive:true,force:true}); }
});
test('generación incremental no publica índice con conteos incompletos', async () => {
 const { mkdtemp, access, rm } = await import('node:fs/promises');
 const { tmpdir } = await import('node:os');
 const { join } = await import('node:path');
 const raizTemporal = await mkdtemp(join(tmpdir(),'indice-incompleto-'));
 const destino = join(raizTemporal,'indice');
 const fixture = structuredClone(catalogo);
 fixture.periodos[0].conteos = { ofertas:2, resultados:1, ordenescompra:1 };
 try {
   await assert.rejects(generarIndiceParticionado({raiz,periodo:'2026-10',destino,leerArchivo:async archivo => archivo.endsWith('catalogo-publico.json') ? fixture : leerArchivo(archivo)}),/Conteo inconsistente/);
   await assert.rejects(access(destino));
 } finally { await rm(raizTemporal,{recursive:true,force:true}); }
});

test('no reemplaza un índice ya existente', async () => {
 const { mkdtemp, mkdir, rm } = await import('node:fs/promises');
 const { tmpdir } = await import('node:os');
 const { join } = await import('node:path');
 const carpeta = await mkdtemp(join(tmpdir(),'indice-existente-'));
 const destino = join(carpeta,'indice');
 await mkdir(destino);
 try {
   await assert.rejects(generarIndiceParticionado({raiz,periodo:'2026-10',destino,leerArchivo}),/destino ya existe/);
 } finally { await rm(carpeta,{recursive:true,force:true}); }
});
