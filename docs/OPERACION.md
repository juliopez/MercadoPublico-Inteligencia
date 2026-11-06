# Operación, monitoreo y mantenimiento

## Comprobaciones habituales

1. Confirmar que el ETL diario y la API nocturna ejecutaron y publicaron sus resultados.
2. Revisar conteos y fechas del catálogo público y contrastarlos con índices derivados.
3. Examinar advertencias de cobertura: ausencia de índice no significa ausencia de actividad.
4. Probar búsqueda, detalle, perfiles, comparación y guardados en el navegador.
5. Revisar GitHub Actions y logs locales; distinguir fallos de ejecución de lagunas en fuentes oficiales.

## Incidencias

- **No aparecen datos recientes:** comprobar origen, fecha de publicación, catálogo y despliegue antes de modificar ETL.
- **Perfiles incompletos:** comparar metadatos de participación con conteos publicados; regenerar derivados sin fabricar registros.
- **Error 429:** respetar las pausas, reintentos y checkpoint de la API.
- **Conflicto de publicación:** regenerar sobre el catálogo más reciente; no mezclar índices antiguos con fragmentos nuevos.
- **Cierre mensual:** detenerse si faltan fuentes, respaldos o permisos; registrar el bloqueo.

## Seguridad y cambios

Conservar respaldos, no publicar secretos, no borrar históricos vigentes, y exigir pruebas específicas para cualquier cambio a los cuatro procesos protegidos. Véase [política maestra](POLITICA_PROTECCION_CUATRO_PROCESOS.md).

## Evidencia

Registrar fecha/hora, período, fuente, ejecución, conteos y resultado. Distinguir siempre **automatización configurada**, **ejecución exitosa** y **cobertura verificada**.
