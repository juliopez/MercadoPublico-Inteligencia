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
test('no existe importación ni carga automática en la página principal', async () => {
  const html = await readFile(new URL('../index.html', import.meta.url), 'utf8');
  assert.doesNotMatch(html, /asistente-ia-ui\.js|asistente-ia\.css/);
});
test('estilos limitados a las clases del componente', async () => {
  const css = await readFile(new URL('../css/asistente-ia.css', import.meta.url), 'utf8');
  const reglas = css.match(/(?:^|\})\s*([^{}]+)\s*\{/g) || [];
  assert.ok(reglas.length >= 5);
  assert.doesNotMatch(css, /(^|\})\s*(body|html|header|main|button|textarea)\s*\{/m);
});
