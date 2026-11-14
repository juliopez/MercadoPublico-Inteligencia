import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {generarHistoricoNombres} from './generar_historico_nombres.mjs';
test('genera todos los períodos del catálogo en directorios separados',async()=>{
 const raiz='/tmp/frontend-historico-fixture';
 const carpeta=await mkdtemp(join(tmpdir(),'historico-nombres-'));
 const destino=join(carpeta,'salida');
 const periodos=['2026-09','2026-10'];
 const partes=periodo=>Object.fromEntries(['ofertas','resultados','ordenescompra'].map(e=>[e,['data/partes/'+e+'/'+periodo+'/0001.json']]));
 const catalogo={periodos:periodos.map(periodo=>({periodo,partes:partes(periodo),conteos:{ofertas:1,resultados:0,ordenescompra:0}}))};
 const leerArchivo=async ruta=>{
   if(ruta.endsWith('catalogo-publico.json')) return catalogo;
   return ruta.includes('/ofertas/')?[{proveedor:'Makarena Bañares'}]:[];
 };
 try {
   const r=await generarHistoricoNombres({raiz,destino,leerArchivo});
   assert.deepEqual(r.map(x=>x.periodo),periodos);
   assert.equal(r.reduce((a,x)=>a+x.registros_origen,0),2);
 } finally { await rm(carpeta,{recursive:true,force:true}); }
});
