import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { crearAsistenteUI } from './asistente-ia-ui.js';

test('el asistente permanece apagado por defecto y no modifica el contenedor', () => {
  let escrituras = 0;
  const contenedor = { replaceChildren() { escrituras++; } };
  const instancia = crearAsistenteUI({ contenedor, consultar: async () => ({ estado: 'aclaracion' }) });
  assert.equal(instancia.activo, false);
  assert.equal(escrituras, 0);
  instancia.destruir();
  assert.equal(escrituras, 0);
});
test('sin proveedor de consultas no se monta', () => {
  const contenedor = { replaceChildren() { throw new Error('No debe montarse'); } };
  assert.throws(() => crearAsistenteUI({ contenedor, habilitado: true }), /Consulta no configurada/);
});
test('sin contenedor válido no se monta', () => {
  assert.throws(() => crearAsistenteUI({ consultar: async () => ({}) }), /Contenedor inválido/);
});
test('interfaz solo usa textContent para mostrar contenido remoto', async () => {
  const codigo = await readFile(new URL('./asistente-ia-ui.js', import.meta.url), 'utf8');
  assert.match(codigo, /\.textContent\s*=/);
  assert.doesNotMatch(codigo, /\binnerHTML\b|\binsertAdjacentHTML\b|\bdocument\.write\b/);
});
test('las fuentes externas se restringen a GitHub Pages con HTTPS', async () => {
  const codigo = await readFile(new URL('./asistente-ia-ui.js', import.meta.url), 'utf8');
  assert.match(codigo, /url\.protocol\s*!==\s*'https:'/);
  assert.match(codigo, /url\.hostname\s*!==\s*'juliopez\.github\.io'/);
  assert.match(codigo, /noopener noreferrer/);
});
test('la página principal incorpora sección 07 y monta la integración aislada', async () => {
  const html = await readFile(new URL('../index.html', import.meta.url), 'utf8');
  assert.match(html, /id="bloque-asistente-ia"/);
  assert.match(html, /href="#bloque-asistente-ia"/);
  assert.match(html, /id="asistente-ia-contenedor"/);
  assert.match(html, /js\/asistente-ia-integracion\.js/);
  assert.match(html, /css\/asistente-ia\.css/);
});
test('la integración consulta el Worker sin intervenir procesos productivos', async () => {
  const codigo = await readFile(new URL('./asistente-ia-integracion.js', import.meta.url), 'utf8');
  assert.match(codigo, /crearAsistenteUI/);
  assert.match(codigo, /workers\.dev\/chat/);
  assert.match(codigo, /method: 'POST'/);
  assert.match(codigo, /controlador\.abort\(\), 30000/);
  assert.match(codigo, /estado === 'respondida'/);
  assert.match(codigo, /estado === 'aclaracion'/);
  assert.doesNotMatch(codigo, /innerHTML|localStorage|document\.write/);
});
test('estilos limitados a las clases del componente', async () => {
  const css = await readFile(new URL('../css/asistente-ia.css', import.meta.url), 'utf8');
  const reglas = css.match(/(?:^|\})\s*([^{}]+)\s*\{/g) || [];
  assert.ok(reglas.length >= 5);
  assert.doesNotMatch(css, /(^|\})\s*(body|html|header|main|button|textarea)\s*\{/m);
});

test('presenta conteos de octubre con formato legible y fecha de cobertura', async () => {
  const { formatearResultadoAsistente } = await import('./asistente-ia-ui.js');
  const texto = formatearResultadoAsistente({
    periodo: '2026-10',
    datos: { total_procesos: 92302, licitaciones: 6895, compras_agiles: 85407, otras_modalidades: 0 },
    cobertura: { actualizado: '2026-11-13T23:00:57Z' }
  });
  assert.match(texto, /octubre de 2026/);
  assert.match(texto, /6\.895/);
  assert.match(texto, /85\.407/);
  assert.match(texto, /92\.302/);
  assert.match(texto, /Actualización de datos/);
  assert.doesNotMatch(texto, /"total_procesos"/);
});
test('mantiene explicación validada y no inventa datos ausentes', async () => {
  const { formatearResultadoAsistente } = await import('./asistente-ia-ui.js');
  assert.equal(formatearResultadoAsistente({explicacion:'Explicación verificada',datos:{licitaciones:3}}),'Explicación verificada');
  assert.match(formatearResultadoAsistente({datos:{}}),/No hay cifras compatibles/);
});
