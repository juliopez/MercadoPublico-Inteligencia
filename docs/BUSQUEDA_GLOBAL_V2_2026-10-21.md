# Búsqueda global V2 — avance de diseño e implementación (21-10-2026)

## Objetivo
Recuperar de V1 la búsqueda de procesos, organismos y proveedores en todo el período sin sustituir el motor de carga fragmentada de V2.

## Consulta previa
README principal, índice, decisiones, línea base V2, documento de filtros locales y código de app.js, index.html y exportar_frontend_v2.py.

## Trabajo realizado
Se incorporó `scripts/indexar_busqueda_frontend_v2.py`, generador inicial que opera únicamente sobre los JSON públicos `frontend-v2/data/partes`, valida recuentos del catálogo y prepara un índice por período, entidad y prefijo de tres caracteres de palabra. Incluye campos de consulta públicos: códigos, nombres de procesos, organismos y proveedores. No lee ni escribe Sheets ni afecta los ETL.

## Estado y limitaciones
**En desarrollo, no operativo.** El generador todavía no se ha ejecutado y validado sobre millones de registros; no hay índices publicados ni búsqueda global habilitada en frontend. Antes de integrarlo es imprescindible medir tamaño y memoria del proceso de indexación, comprobar nombres y coincidencias, controlar términos frecuentes y publicar de manera transaccional sin saturar GitHub Pages. El índice por prefijos no equivale a búsquedas arbitrarias de subcadenas; búsquedas de menos de tres caracteres quedan fuera de alcance inicial. No afirmar cobertura global en la interfaz existente.

## Archivos y cambios
- Nuevo: `scripts/indexar_busqueda_frontend_v2.py`.
- Sin cambios: app.js, HTML, CSS, índices relacionados, manifiesto, fragmentos de datos, frontend V1 y datos privados.

## Validación y siguiente hito
Se inspeccionó código/documentación y se corrigió la serialización de saltos de línea. No se ejecutaron pruebas automatizadas ni navegador. Antes de activar funcionalidad, validar el generador con dataset reducido y posteriormente con cobertura real; generar índice y comprobar búsqueda selectiva end-to-end, sin regresión de rendimiento de V2.


## Continuación — validación preventiva (21-10-2026)
- Se volvió a leer README, índice, decisiones y este documento antes de intervenir.
- Se detectó y corrigió una expresión regular que rechazaba rutas de fragmentos JSON válidos: commit `96f865db`.
- Se incorporó `tests/test_indexar_busqueda_frontend_v2.py`, con casos para índice de dos procesos, normalización con tildes, prefijos y discordancia de conteos: commit `e9a4692b`.
- **Pruebas aún no ejecutadas contra el código del repositorio:** la conexión de red del entorno local de verificación no permitió obtener el archivo remoto. Los nuevos casos de prueba quedan disponibles para ejecución en CI o en entorno de desarrollo.
- No se generaron índices masivos ni se modificó el JavaScript de carga y búsqueda actual. La interfaz continúa utilizando búsqueda local por bloque.
- Riesgos pendientes: volumen y tamaño de prefijos frecuentes, uso de memoria durante indexación, duplicación de texto por clave y latencia. No activar búsqueda global antes de medirlos.
