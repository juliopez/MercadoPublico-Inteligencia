import test from 'node:test';
import assert from 'node:assert/strict';
import { validarIntencion, interpretarRespuestaGemini, crearPromptIntencion } from './intencion.mjs';
const meses=['2026-08','2026-09','2026-10','2026-11'];
test('resumen estricto',()=>assert.deepEqual(validarIntencion({operacion:'resumen',periodo:'2026-08'},meses),{operacion:'resumen',periodo:'2026-08'}));
test('ranking aplica límites seguros',()=>assert.deepEqual(validarIntencion({operacion:'ranking',periodo:'2026-09'},meses),{operacion:'ranking',periodo:'2026-09',criterio:'registros',limite:10}));
test('serie válida',()=>assert.equal(validarIntencion({operacion:'serie',periodos:['2026-08','2026-09']},meses).periodos.length,2));
test('organismo válido',()=>assert.equal(validarIntencion({operacion:'organismo',periodo:'2026-10',organismo:'  Hospital Central  '},meses).organismo,'Hospital Central'));
test('rechaza operación arbitraria',()=>assert.throws(()=>validarIntencion({operacion:'ejecutar_sql',periodo:'2026-08'},meses)));
test('rechaza campos inyectados',()=>assert.throws(()=>validarIntencion({operacion:'resumen',periodo:'2026-08',sql:'DROP TABLE'},meses)));
test('rechaza campos de otra operación',()=>assert.throws(()=>validarIntencion({operacion:'resumen',periodo:'2026-08',organismo:'X'},meses)));
test('rechaza período inexistente',()=>assert.throws(()=>validarIntencion({operacion:'resumen',periodo:'2026-01'},meses)));
test('rechaza duplicados en serie',()=>assert.throws(()=>validarIntencion({operacion:'serie',periodos:['2026-08','2026-08']},meses)));
test('rechaza ranking mayor que 10',()=>assert.throws(()=>validarIntencion({operacion:'ranking',periodo:'2026-08',limite:11},meses)));
test('rechaza JSON envuelto en Markdown',()=>assert.throws(()=>interpretarRespuestaGemini('\\`\\`\\`json\\n{}\\n\\`\\`\\`',meses)));
test('rechaza texto antes del JSON',()=>assert.throws(()=>interpretarRespuestaGemini('Aquí tienes: {"operacion":"resumen","periodo":"2026-08"}',meses)));
test('acepta solicitud de aclaración',()=>assert.deepEqual(interpretarRespuestaGemini('{"necesita_aclaracion":true}',meses),{necesita_aclaracion:true}));
test('rechaza aclaración con campos extras',()=>assert.throws(()=>interpretarRespuestaGemini('{"necesita_aclaracion":true,"url":"https://evil.example"}',meses)));
test('pregunta larga rechazada',()=>assert.throws(()=>crearPromptIntencion('a'.repeat(1001),meses)));
test('prompt no incluye claves',()=>assert.ok(!crearPromptIntencion('¿Cuántas licitaciones en agosto?',meses).instrucciones.includes('GEMINI_API_KEY')));


test('normaliza alias acotados de ranking de compradores',()=>assert.deepEqual(
  interpretarRespuestaGemini(JSON.stringify({operacion:'ranking',periodo:'2026-10',entidad:'organismos_compradores',criterio:'procesos',limite:'5'}),meses),
  {operacion:'ranking',periodo:'2026-10',entidad:'procesos',criterio:'registros',limite:5}
));
test('rechaza campos no autorizados incluso con alias',()=>assert.throws(()=>
  interpretarRespuestaGemini(JSON.stringify({operacion:'ranking',periodo:'2026-10',entidad:'compradores',campo_extrano:'x'}),meses)
));

test('Gemini interpreta búsqueda exacta de participante con límites seguros',()=>assert.deepEqual(
 interpretarRespuestaGemini('{"operacion":"buscar_participante","periodo":"2026-10","nombre":" Makarena Bañares "}',meses),
 {operacion:'buscar_participante',periodo:'2026-10',nombre:'Makarena Bañares',modo:'exacto',limite:20}
));
test('rechaza búsqueda contiene no soportada por prefijos',()=>assert.throws(()=>
 validarIntencion({operacion:'buscar_participante',periodo:'2026-10',nombre:'Bañares',modo:'contiene'},meses)));
test('rechaza inyección de ruta en búsqueda',()=>assert.throws(()=>
 validarIntencion({operacion:'buscar_participante',periodo:'2026-10',nombre:'Makarena Bañares',ruta:'secreto'},meses)));
