# Ayudas contextuales del Observatorio MER V2 — 22/10/2026

## Objetivo
Evitar que visitantes interpreten como adjudicaciones, pagos o compras únicas los conteos y presupuestos publicados. Ofrecer definiciones breves y advertencias metodológicas por sección.

## Implementación
- `frontend-v2/js/ayudas-contextuales.js`: diccionario centralizado `HELP`, reconocimiento de encabezados y etiquetas existentes y dinámicas, botón ⓘ accesible mediante clic y teclado, cierre al pulsar fuera o Escape. No consulta ningún servicio ni modifica datos.
- `frontend-v2/css/styles.css`: presentación de alto contraste, caja adaptada al móvil, estados de foco visibles.
- `frontend-v2/index.html`: carga del módulo por `type=module`.
- Alcance: búsqueda, entidad, filtros, consulta por período, tarjetas de evolución mensual (montos, organismos, actividad), perfiles, comparaciones, favoritos y métricas claves. Las fichas dinámicas conservan sus datos y enlaces originales.

## Reglas metodológicas
- Presupuestos CLP visibles no equivalen a montos adjudicados ni a pagos.
- Montos no informados son ausencia de datos, no cero.
- Nombres de organismos y proveedores sin homologación: no representan necesariamente entidades únicas.
- Comparaciones del mes en curso requieren cautela.
- Vínculos COT–OC deben distinguir coincidencia, evidencia documental y adjudicación contractual.
- Exploración por bloques no equivale a búsqueda global.

## Validación pendiente
Comprobar despliegue Pages, apertura con mouse y teclado, cierre Escape, visualización en móviles, no duplicación de ⓘ tras repintar tarjetas, persistencia de filtros y vínculos. No confundir código publicado con aceptación de usabilidad hasta verificación real.

## Límites
No se modificaron la BBDD Google Sheets, scripts del ETL, históricos, cron Ubuntu ni workflows de las 17:00. La auditoría desatendida del viernes 23/10 mantiene su prioridad.
