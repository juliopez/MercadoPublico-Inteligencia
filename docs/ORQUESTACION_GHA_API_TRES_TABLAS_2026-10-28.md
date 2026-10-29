# Orquestación GitHub Actions — Compra Ágil MER, 28/10/2026

## Decisión y arquitectura
- GitHub Actions independiente del cron Ubuntu, lunes–viernes, 22:30 `America/Santiago` con dos disparos UTC posibles y guardia local de hora.
- Selección incremental de hasta **10 detalles API** por ejecución. Revisa primero máximo 2 seguimientos vencidos y después procesos nuevos del día más antiguo pendiente (`fecha_cursor` + `pagina`).
- Persistencia del avance por mes: `control/cola_api_mer.json`, confirmada mediante commits a `main`. Estado y último reporte sin información personal.
- API V2 rellena en el MER operativo `Procesos`, `Ofertas`, `Resultados`, con validaciones de esquema, mes oficial, PK y relecturas posteriores. Montos CLP sin moneda acreditada no se inventan; selección no equivale a adjudicación.
- Ante HTTP 429 se detienen más consultas; el código fallido entra a reintento posterior. No hace ráfagas.
- Si hay nuevas filas: `scripts/exportar_mer_operativo_v2.py --aplicar --incluir-api` exporta las cuatro entidades, incluyendo `OrdenesCompra`, al catálogo y fragmentos públicos. Un commit a catálogo dispara el workflow **existente** `publicacion-v2-post-etl.yml`, ampliado a las cuatro entidades para índices, perfiles, analítica y relaciones.
- El modo normal del exportador sin `--incluir-api` conserva solamente `Procesos` y `OrdenesCompra`: **cron Ubuntu sin cambio**.
- El workflow nocturno está en `.github/workflows/observacion-api-2230.yml`. El nombre del archivo conserva la procedencia histórica, pero su contenido ya es de sincronización real.

## Evidencia verificada
- CI de sintaxis y esquemas `Validar API nocturna MER`: ejecución 40806110547 **success**.
- Verificación autónoma de lectura Google desde el mismo GitHub Actions: ejecución 40806211507. Se observó en logs `TICKET_CONFIGURADO True`, `CREDENCIAL_GOOGLE_GHA_CONFIGURADA True`, `LECTURA_VERIFICADA Procesos`, `LECTURA_VERIFICADA Ofertas` y `LECTURA_VERIFICADA Resultados`. No se realizó escritura ni solicitud a ChileCompra en esa comprobación.
- Evidencia anterior de lote real manual: 18 filas Ofertas y 3 Resultados en MER octubre, respaldadas y verificadas.

## Límites importantes
- **Aún no existe evidencia de una ejecución nocturna completa que haya escrito y publicado de extremo a extremo.** No confundir CI/lectura exitosa con ello.
- Primer lanzamiento cron depende de la puntualidad relativa de GitHub Actions; la ventana de control es las 22 h local y un retraso fuera de esa hora se omite de forma segura.
- La escritura de Google Sheets entre pestañas no es transaccional. Un fallo parcial queda recuperable por deduplicación al reintentar, pero exige supervisión de incidentes.
- Revisión posterior de una cotización o resultado previamente registrado no sobrescribe datos validados; esta primera versión incorpora novedades y puede requerir un upsert enriquecedor para cambios de campos previamente vacíos.
- El flujo no consulta masivamente octubre: al máximo de 10 detalles por día, el histórico completo puede tardar mucho más de unos días.
- El cierre histórico y la rotación de libro mensual siguen procedimientos distintos y no se alteran con este workflow.

## Archivos clave
- `scripts/mer_api_incremental_10.py`: consulta, comprobación y escritura de tres tablas, persistencia de estado.
- `scripts/exportar_mer_operativo_v2.py`: exportación en dos modos.
- `.github/workflows/observacion-api-2230.yml`: flujo nocturno.
- `.github/workflows/publicacion-v2-post-etl.yml`: cadena existente de índices.
