import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { buscarEnIndiceLocal } from './lector_indice_nombres.mjs';

test('lector encuentra coincidencia exacta y conserva período y procedencia', async () => {
  const directorio = await mkdtemp(join(tmpdir(), 'lector-nombres-'));
  try {
    await writeFile(join(directorio, 'manifiesto.json'), JSON.stringify({
      periodo: '2026-10', prefijos: { ma: 1 }, fecha_catalogo: '2026-11-14', registros_origen: 2
    }));
    await writeFile(join(directorio, 'clave-ma.ndjson'), JSON.stringify({
      clave: 'makarena banares', nombre: 'Makarena Bañares', periodo: '2026-10',
      entidad: 'ofertas', parte: 'data/partes/ofertas/2026-10/0001.json', fila: 4
    }) + '\n');
    const r = await buscarEnIndiceLocal({ directorio, consulta: 'MAKARENA BAÑARES' });
    assert.equal(r.total_coincidencias, 1);
    assert.equal(r.resultados[0].fila, 4);
    assert.equal(r.periodo, '2026-10');
  } finally { await rm(directorio, { recursive: true, force: true }); }
});
test('lector devuelve cero cuando el prefijo no está indexado', async () => {
  const directorio = await mkdtemp(join(tmpdir(), 'lector-nombres-'));
  try {
    await writeFile(join(directorio, 'manifiesto.json'), JSON.stringify({
      periodo: '2026-10', prefijos: {}, registros_origen: 0
    }));
    const r = await buscarEnIndiceLocal({ directorio, consulta: 'Empresa Ausente' });
    assert.equal(r.total_coincidencias, 0);
  } finally { await rm(directorio, { recursive: true, force: true }); }
});
