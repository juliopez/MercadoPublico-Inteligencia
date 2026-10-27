# Preparación Etapa 2 — APIs ChileCompra — miércoles 28 de octubre de 2026

**Estado:** plan de inicio y auditoría preliminar de código, sin ejecución sobre API, sin escrituras en Google Sheets y sin modificación del cron, MER ni Pages. **Prerequisito cumplido:** Etapa 1 cerrada el 27/10 con evidencia de Ubuntu, GitHub Actions y HTTP 200 en Pages: [auditoría 27/10](AUDITORIA_ORQUESTACION_2026-10-27.md).

## Objetivo concreto
Completar los campos y entidades que el ETL diario por ZIP oficiales no entrega: Compra Ágil (procesos y sus detalles), ofertas/cotizaciones individualizadas, selecciones/resultados y adjudicaciones de licitaciones que estén expresamente acreditadas por API. Conservar el contrato existente y los seis tabs `Procesos`, `Ofertas`, `Resultados`, `OrdenesCompra`, `Proveedores`, `VinculosCOT_OC`; separar datos faltantes de API no disponible, casos sin registros y adjudicaciones no verificadas.

## Situación conocida al cierre 27/10
- ZIP oficial diario, ETL Ubuntu y conciliación OC–COT: **funcionan y deben permanecer intactos**.
- Catálogo público octubre: 3184 procesos, 133202 OC, **0 ofertas** y **0 resultados**. Estos ceros describen cobertura publicada, **no ausencia de ofertas o resultados oficiales**.
- Hay scripts existentes, no crear un cliente nuevo sin necesidad:
  - `scripts/sync_chilecompra_sheets.py`: consulta listados Compra Ágil v2 con paginación/checkpoints y compatibilidad Procesos; también contiene consulta V1 de licitaciones. Se observan supuestos de env y cabeceras que deben cotejarse con MER vigente antes de usarlo.
  - `scripts/v2_detalle_sheets.py`: consulta v2 por código, `id_cotizacion`, upsert de Ofertas y registro de selección sin adjudicación inferida; trabaja con esquema piloto de 7 columnas Ofertas y 10 Resultados, que **no puede suponerse igual al MER vigente**. Modo `auto` prioriza un código, no constituye lote completo.
  - `scripts/sync_resultados_licitaciones.py`: intenta complementar adjudicaciones V1; exige una cabecera de Resultados de 10 columnas. Confirmar la compatibilidad y alcance real de detalle.
  - `scripts/api_retry.py`: máximo 3 intentos ante 502/503/504 y errores de red, corte inmediato ante HTTP 429.
  - `scripts/consulta_compra_agil.py`: exploratorio con cinco códigos; **no publicar sus artefactos crudos en Pages**.
- `docs/diccionario-api-first.md` describe columnas finales más amplias; algunas descripciones se refieren a prototipos de octubre 16 y requieren verificación actual. No adoptar los viejos límites de piloto ni tablas experimentales.
- `config/catalogo_sheets.json` identifica el MER operativo 2026-10 y el libro noviembre preparado. Revisar cabeceras reales, PK, capacidad por hoja, permisos de servicio y acoplamientos del publicador **antes de escribir**.

## Sesión de trabajo del miércoles 28/10 (orden de ejecución)

### Bloque A — auditoría exacta, sin escrituras
1. Inspeccionar código de listados y detalles v1/v2; entradas, salidas, códigos de retorno, zonas horarias, paginación, límites, checkpoint, reintentos y excepciones 504/429.
2. Leer cabeceras efectivas de las seis hojas del MER octubre en modo lectura, contrastarlas con `scripts/importador_historicos_v2.py` y con transformaciones/exportadores usados por V2. No exponer secretos ni RUT en documentos.
3. Crear matriz **fuente API → identificador oficial → columna MER → entidad pública → regla de verificación → comportamiento sin dato**. Diferenciar ofertas de Compra Ágil y adjudicaciones de licitaciones; verificar API directamente con una muestra pequeña y pública; nunca deducir resultados a partir de una mera OC.
4. Determinar qué datos no existen en ZIP y sí están disponibles por API, qué datos son accesibles solo con detalle individual, cuáles no se exponen y cuáles requieren esperar cierre o adjudicación.

### Bloque B — correcciones mínimas, previa viabilidad
5. Reutilizar cliente y `api_retry.py`; corregir incompatibilidades de columnas y claves sin cambiar estructura MER a ciegas. Clave de oferta `(codigo,id_cotizacion)` cuando exista, y clave de resultados distinta según selección/adjudicación oficialmente acreditada. Evitar sobrescribir valores verificados con vacíos.
6. Preparar procesamiento incremental por período y código, con paginación exhaustiva, cupos/reintentos controlados, checkpoint recuperable y reporte por fuente/cobertura. Procesos con errores temporales deben quedar **pendientes**, no marcarse como sin ofertas.
7. Ensayar en seco contra muestra pequeña y validar duplicados, integridad referencial, semántica de monto/moneda, protección de Sheets y compatibilidad del exportador. Comparar conteos antes/después, asegurando segunda pasada idempotente.

### Bloque C — activación condicionada
8. Si pasa la auditoría, ejecutar piloto supervisado y reversible únicamente sobre registros elegibles del MER operativo, previa copia de respaldo. Confirmar lectura posterior y publicación en los cuatro tipos públicos.
9. Proponer el enganche diario al orquestador ya validado como etapa **independiente** y tolerante a fallos de otra fuente; no activarlo sin verificación y autorización de cambio operativo.

## Criterios de aceptación
- No hay migraciones disruptivas, importaciones históricas, recreación de hojas o cambios de cron.
- Reporte del número de procesos elegibles, consultados, completos, sin datos confirmados, pendientes por cobertura y fallidos por HTTP; separados por entidad.
- Filas nuevas/actualizadas verificadas por PK, procedencia y fecha; rerun sin duplicados.
- Resultados distinguen `oferta_seleccionada` de `adjudicacion_verificada`; cero nunca significa desconocido.
- Cadenas posteriores: Sheets → JSON fragmentados → índices/perfiles/analítica → Pages, con verificaciones de coherencia y sin información privada.

## Documentación que prevalece
1. [Decisiones técnicas](DECISIONES_TECNICAS.md).
2. [Auditoría aprobada 27/10](AUDITORIA_ORQUESTACION_2026-10-27.md).
3. [Diccionario API-first](diccionario-api-first.md) **contrastado con el código y el MER real**.
4. [Especificación de Proveedores y Vínculos](Especificacion_Proveedores_Vinculos_COT_OC.md).
5. [Catálogo de Sheets](../config/catalogo_sheets.json) y código de ETL/exportación real.

**Instrucción de continuidad para la próxima conversación:** «Iniciemos la Etapa 2 del Observatorio según `docs/PLAN_ETAPA2_API_2026-10-28.md`. Audita primero cabeceras MER, clientes v1/v2, cobertura y claves de deduplicación. No modifiques el cron ni cargues históricos. Prioriza completar Compra Ágil, Ofertas y Resultados sin inferir adjudicaciones».
