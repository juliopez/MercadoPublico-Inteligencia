# Backend experimental del Asistente IA V2

Módulo determinista **aislado**. No se encuentra integrado al Worker de Cloudflare ni al frontend y no modifica datos productivos.

## Archivos
- `motor.mjs`: motor con operaciones `resumen`, `modalidades`, `organismo`, `serie`.
- `motor.test.mjs`: pruebas con fixtures de catálogo y agregados.
- `README.md`: instrucciones y límites.

## Pruebas
```bash
node --test scripts/asistente_ia/backend/*.test.mjs
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

## Auditoría de coherencia detectada el 13/11/2026
El catálogo y el agregado de órdenes de compra **no coinciden** en varios meses. Evidencia (catálogo → analítica):
- Junio 2026: 150.551 → 150.451 (diferencia -100)
- Julio 2026: 151.050 → 150.980 (diferencia -70)
- Agosto 2026: 153.438 → 153.221 (diferencia -217)
- Septiembre 2026: 148.772 → 147.966 (diferencia -806)
- Octubre 2026: 177.972 → 167.042 (diferencia -10.930)
- Noviembre 2026: 54.984 → 67.023 (diferencia +12.039)

Los archivos de junio–septiembre tienen versión analítica 1; octubre–noviembre versión 3. Esto es evidencia de **diferencias de versiones o generaciones**, pero no demuestra su causa. El generador actual `scripts/generar_analitica_v2.py` incluye una aserción `total == item["conteos"][entity]`, por lo que un agregado inconsistente no debería generarse exitosamente con el catálogo actual sin una actualización posterior de alguna fuente.

**Medida de seguridad:** `motor.mjs` rechaza la consulta con error 503 al no coincidir `registros` con `conteos`. No ajustar totales manualmente ni reescribir agregados publicados hasta revisar el pipeline de generación/publicación y su trazabilidad. La auditoría `auditar_fuentes.mjs` permite repetir el contraste de solo lectura.

Esta auditoría de OC no implica que las modalidades de procesos estén incorrectas: su contraste específico de junio–noviembre fue satisfactorio. La revisión de ofertas y resultados en los seis meses sigue pendiente.

## Control de calidad CI (13/11/2026)
El workflow `.github/workflows/asistente-ia-backend-tests.yml` ejecuta **todos** los archivos `*.test.mjs` del backend, incluidos motor y lector público. La ejecución no modifica fuentes ni despliega servicios. No se ha confirmado todavía una ejecución satisfactoria del workflow desde este entorno; consultar Actions antes de declarar la fase 1 cerrada. Las pruebas con fixtures son distintas de la auditoría de fuentes reales `auditar_fuentes.mjs`.
