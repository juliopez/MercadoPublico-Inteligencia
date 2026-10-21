# Auditoría de compatibilidad — Tarea 14 (Consolidador MER v2)

**Fecha:** 2026-10-21. **Alcance:** inspección de `README.md`, `docs/PLAN_MAESTRO_21_TAREAS.md`, `docs/CONSOLIDADOR_MER_V2.md`, `config/catalogo_sheets.json`, `scripts/planificar_consolidacion_mer.py`, `scripts/publicar_observatorio.py`, `data/observatorio.json` e `index.html`. **No se cambiaron datos, frontend ni jobs.**

## Hallazgos comprobados

| Elemento | Estado constatado | Implicación |
|---|---|---|
| Catálogo mensual | 2026-06 a 2026-09 históricos; 2026-10 operativo; 2026-11 preparado | El catálogo debe seleccionar periodos, no carpetas o todas las hojas indistintamente |
| Planificador `planificar_consolidacion_mer.py` | Excluye futuros y solo admite operativo del mes vigente; históricos con estado que contenga `auditad` | **Es un planificador; no descarga Sheets, no consolida datos, no publica JSON** |
| Publicador `publicar_observatorio.py` | Lee un único `GOOGLE_SHEET_ID` y cuatro pestañas | **No consume el catálogo mensual** ni publica varias Sheets |
| Frontend `index.html` | Lee `data/observatorio.json`; carga todos los fragmentos en memoria | No hay selección remota por período; riesgo de carga masiva de millones de filas |
| Contrato JSON | `fecha_actualizacion`, `partes`, `conteos`; cuatro entidades públicas | Mantener compatibilidad para `procesos`, `ofertas`, `resultados`, `ordenescompra` |
| MER v2 | Seis entidades; `Proveedores` y `VinculosCOT_OC` son de soporte | No publicarlas enteras ni exponer identificadores internos sin contrato y revisión de privacidad |
| Partes del frontend | Ruta permitida por expresión `data/partes/observatorio-[a-z]+-[0-9]{4}.json` | Añadir mes/año a nombres de fragmentos exige cambiar primero el lector, no romper rutas publicadas |
| Manifiesto actual | 84.812 procesos, 398.086 ofertas, 2 resultados y 30 OC | Los cuatro contadores corresponden a la publicación existente, **no** al consolidado MER v2 de todos los períodos |

## Desajustes y riesgos

1. El principal desajuste está entre el **planificador por períodos** y el **publicador de una única Sheet**.
2. El frontend **descarga todas las partes**; publicar sin selección toda la historia sería costoso y probablemente perjudicaría los tiempos de carga.
3. Los códigos de procesos pueden repetirse entre meses; la identidad lógica durante consolidación debe incluir `periodo` para no borrar historia. Las relaciones proceso-oferta-OC pueden cruzar períodos; no deducir unicidad global.
4. Las cifras del manifiesto representan la publicación actual, no los datos almacenados en las seis entidades históricas.
5. El documento `PLAN_MAESTRO_21_TAREAS.md` preserva estados de inicio y comentarios históricos; no confundir `pendiente` en la tabla inicial con la realidad actual.

## Alcance mínimo recomendado para implementar T14

- Reutilizar `planificar_consolidacion_mer.plan()` y el catálogo.
- Leer vía cuenta de servicio **solo** Sheets seleccionadas (sin escribir ni alterar los históricos).
- Validar encabezados contra `importador_historicos_v2.SCHEMA`; imponer selección explícita de cuatro tablas públicas y campos de `PUBLIC` en `publicar_observatorio.py`.
- Construir manifiesto de selección por período y tabla con recuentos y huellas; diferenciar histórico/operativo.
- Generar exportación por período, pero **sin publicarla al sitio** hasta que la T15 adapte el contrato y T16 habilite carga selectiva. No generar una publicación monolítica.
- Validar una muestra y un período completo en entorno de prueba sin tocar `data/observatorio.json` de producción.

## Conclusión

**Tarea 14: parcialmente implementada (solo planificador).** No está finalizada la consolidación multiperíodo. **Tareas 15 y 16: no demostradas sobre MER v2**. Lo siguiente debe ser un exportador de solo lectura por período que produzca archivos en staging local; luego adaptar el frontend y la publicación en un cambio controlado. Evitar editar primero `index.html` o desplegar todos los registros históricos de una vez.

**Criterio de aceptación T14:** selección correcta de los meses aptos desde catálogo; seis encabezados verificados en origen; cuatro entidades públicas exportadas por período; conteos, huellas y ausencia de campos sensibles; sin cambios en la publicación vigente.
