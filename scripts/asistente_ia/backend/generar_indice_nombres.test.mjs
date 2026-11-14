import test from 'node:test';
import assert from 'node:assert/strict';
import { generarIndice } from './generar_indice_nombres.mjs';

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
