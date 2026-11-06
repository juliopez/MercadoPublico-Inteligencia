# Adaptar el Observatorio a otra infraestructura

El Observatorio está organizado alrededor de **contratos de datos** y tareas reproducibles; no todas las alternativas descritas a continuación están implementadas.

## Ruta recomendada

1. Mantener inicialmente el frontend y el contrato JSON del catálogo.
2. Sustituir **una capa a la vez**: primero almacenamiento, después orquestación y finalmente hosting.
3. Para cada sustitución, generar una muestra de datos y comparar conteos, claves y resultados de consulta.
4. Documentar explícitamente diferencias de identidad de proveedores, selección/adjudicación y períodos.
5. Activar automatización solo después de pruebas de recuperación e idempotencia.

## Ejemplo: Google Sheets → PostgreSQL

Implementar tablas de MER según [modelo lógico](MODELO_DATOS.md), agregando claves por período, procedencia y fechas de actualización. Crear un exportador que produzca **exactamente** el catálogo y los fragmentos esperados por el frontend. No basta con cambiar la cadena de conexión: el código actual incluye integraciones específicas de Sheets.

## Ejemplo: GitHub Actions → Airflow o GitLab

Reproducir dependencias de tareas, validación previa a publicar, reintentos, checkpoint, exclusión de duplicados y serialización de escrituras. Evitar publicar índices derivados de un catálogo anterior.

## Ejemplo: GitHub Pages → servidor propio

Servir HTML, JS, CSS y JSON por HTTP(S), preservando rutas relativas, política de caché/versionado y acceso público únicamente a los artefactos exportados. Nunca exponer el MER privado.

## Estado de portabilidad

**Disponible:** código fuente y datos públicos para exploración estática, esquema lógico, scripts y workflows de referencia.

**Requiere adaptación:** credenciales, hojas privadas, disparadores Ubuntu, permisos, configuración de GitHub, proveedores alternativos y pruebas integrales de extremo a extremo.

Las alternativas tecnológicas son orientaciones de ingeniería, no compatibilidad certificada.
