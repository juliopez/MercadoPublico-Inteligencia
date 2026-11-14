import test from 'node:test';
import assert from 'node:assert/strict';
import { crearBuscadorPublico } from './lector_indice_publico.mjs';

test('lector HTTP solo solicita manifiesto y prefijo necesario',async()=>{
 const urls=[];
 const buscar=crearBuscadorPublico({fetchIndice:async url=>{
   urls.push(url);
   return {ok:true,text:async()=>url.endsWith('manifiesto.json')
     ? JSON.stringify({periodo:'2026-10',prefijos:{ma:1},registros_origen:3})
     : JSON.stringify({clave:'makarena banares',nombre:'Makarena Bañares',periodo:'2026-10',entidad:'ofertas'})+'\n'};
 }});
 const r=await buscar({periodo:'2026-10',consulta:'Makarena Bañares'});
 assert.equal(r.total_coincidencias,1);
 assert.equal(urls.length,2);
 assert.ok(urls[1].endsWith('/2026-10/clave-ma.ndjson'));
});
test('lector HTTP no solicita prefijo inexistente',async()=>{
 let llamadas=0;
 const buscar=crearBuscadorPublico({fetchIndice:async()=>{llamadas++;return {ok:true,text:async()=>JSON.stringify({periodo:'2026-10',prefijos:{},registros_origen:3})};}});
 const r=await buscar({periodo:'2026-10',consulta:'Makarena Bañares'});
 assert.equal(r.total_coincidencias,0);
 assert.equal(llamadas,1);
});
test('lector HTTP rechaza origen ajeno',()=>assert.throws(()=>crearBuscadorPublico({fetchIndice:async()=>{},base:'https://evil.example/'})));
