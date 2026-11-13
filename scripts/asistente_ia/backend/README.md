# Backend experimental del Asistente IA V2

Módulo determinista **aislado**. No se encuentra integrado al Worker de Cloudflare ni al frontend y no modifica datos productivos.

## Archivos
- `motor.mjs`: motor con operaciones `resumen`, `modalidades`, `organismo`, `serie`.
- `motor.test.mjs`: pruebas con fixtures de catálogo y agregados.
- `README.md`: instrucciones y límites.

## Pruebas
```bash
node --test scripts/asistente_ia/backend/motor.test.mjs
```

## Integración futura
```js
import { crearMotor } from './motor.mjs';
const motor = await crearMotor({leerJSON:async url=>{
  const respuesta = await fetch(url);
  if (!respuesta.ok) throw new Error('Error de fuente pública');
  return respuesta.json();
}});
const resultado = await motor.consultar({operacion:'modalidades',periodo:'2026-08'});
```

No llamar `crearMotor` por cada pregunta sin política de caché y actualización. La validación contra fixtures no demuestra disponibilidad de fuentes en tiempo real.

## Pendiente
Control de abuso, caché versionada, telemetría sin datos privados, límites de tamaño y tiempo, validación de fuentes actuales, integración y despliegue controlado. Los resultados de organismos son coincidencias exactas por nombre normalizado; no representan una identificación legal única.
