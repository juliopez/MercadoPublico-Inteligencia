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

## Estado verificado al 13/11/2026
- **Incidente histórico de OC cerrado:** los valores discrepantes anteriores documentan el hallazgo original, no el estado actual. Tras regeneración y nuevo despliegue con el workflow existente, GitHub Actions `Asistente IA - comparar GitHub Pages vs main`, ejecución #2 (run `43447717761`), acreditó `verificados:24, coincidentes:24, fallas:0`. Este control compara conteos, no verifica exhaustivamente los montos.
- **Motor determinista:** workflow `Asistente IA - pruebas del motor determinista`, ejecución #2 (run `43448527612`, job `131964243234`), completado correctamente: **19 pruebas, 19 aprobadas, 0 fallidas**. Son pruebas unitarias con fixtures, no una batería funcional de consultas reales.
- **Pendiente:** validación funcional de consultas con datos públicos actuales, exactitud semántica de montos y cobertura de funcionalidades planificadas. No declarar fase 2 íntegramente cerrada por estos dos resultados.

## Validación funcional pública — 13/11/2026
Workflow `Asistente IA - consultas reales en Pages`, ejecución con job `131969401684` (run `43450012041`): **86 comprobaciones, 86 correctas, 0 fallas**, sobre seis meses publicados. Incluye resúmenes, rankings de registros y montos, modalidades, consulta de un organismo inequívoco por mes, serie temporal y rechazo de período inexistente.

El primer intento detectó nombres canónicos de organismos duplicados en el índice, lo que activó correctamente el bloqueo por ambigüedad. Se ajustó **solo el validador** (commit `fbaf4b9`) para elegir un organismo inequívoco; el motor no fue modificado.

**Alcance del cierre:** validación de las operaciones deterministas actualmente implementadas; no supone haber implementado las 18 capacidades planificadas, auditado exhaustivamente todos los importes o desplegado la integración Gemini/frontend. Próxima fase: conversación Gemini con ejecución determinista y trazabilidad.
