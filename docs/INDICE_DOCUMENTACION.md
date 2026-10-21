# Índice documental — Observatorio de Mercado Público

**Revisión:** 21-10-2026. Ruta recomendada: [README del proyecto](../README.md) → **este índice** → [decisiones técnicas](DECISIONES_TECNICAS.md) → documento especializado → código/evidencias.

> Los documentos fechados conservan el contexto de una etapa y pueden contener pendientes ya resueltos. **No deben usarse como estado actual** sin contrastarlos con el README y el código. No borrar evidencia histórica ni credenciales operativas locales.

## 1. Estado, arquitectura y decisiones

- **[README vigente](../README.md)** — estado del sistema, accesos y operación.
- **[Decisiones técnicas vigentes](DECISIONES_TECNICAS.md)** — restricciones aprobadas, integridad de MER, cierre mensual y límites de frontend.
- **[Frontend V2 — guía funcional](../frontend-v2/README.md)** — uso, componentes, cobertura y restricciones reales.
- [Consolidador MER v2](CONSOLIDADOR_MER_V2.md) — arquitectura privada y publicación.
- [Catálogo de Sheets y períodos](CATALOGO_SHEETS_Y_PERIODOS.md) — identificadores y cobertura interna.
- [Especificación Proveedores y Vínculos COT–OC](Especificacion_Proveedores_Vinculos_COT_OC.md).
- [Diagrama MER](MER_propuesto.mmd).
- [Auditoría de consolidador/frontend — tarea 14](AUDITORIA_T14_CONSOLIDADOR_FRONTEND.md).

## 2. Frontend V2 — funcionamiento y mejoras

**Leer en este orden (vigencia primero):**
- [Línea base de rendimiento](BASELINE_FRONTEND_V2_2026-10-21.md).
- [Auditoría comparativa V1–V2](AUDITORIA_FRONTEND_V1_V2_2026-10-21.md).
- [Búsqueda global indexada](BUSQUEDA_GLOBAL_V2_2026-10-21.md).
- [Relaciones y detalle indexado](DETALLE_RELACIONADO_FRONTEND_V2.md).
- [Analítica interactiva y vínculos entre meses](ANALITICA_INTERACTIVA_RELACIONES_HISTORICAS_V2_2026-10-21.md).
- [Mejoras integrales de experiencia](MEJORAS_UX_INTEGRALES_V2_2026-10-21.md).

**Hitos técnicos y evidencias históricas (no sustituyen el manual vigente):**
- [Presentación visual](MEJORA_VISUAL_FRONTEND_V2_2026-10-21.md); [Tablas](MEJORA_TABLAS_FRONTEND_V2_2026-10-21.md); [Filtros locales](FILTROS_LOCALES_FRONTEND_V2_2026-10-21.md).
- [Perfiles contextuales y agregados](PERFILES_CONTEXTUALES_FRONTEND_V2_2026-10-21.md); [Comparación de proveedores y sugerencias](COMPARACION_PROVEEDORES_FRONTEND_V2_2026-10-21.md).
- [Favoritos y exportación CSV](FAVORITOS_CSV_FRONTEND_V2_2026-10-21.md).
- [Mejoras analíticas y filtros globales](MEJORAS_ANALITICAS_V2_2026-10-21.md).
- [Ajustes visuales consolidados](LOTE_AJUSTES_VISUALES_V2_2026-10-21.md).
- [Corrección de tablas y detalle OC](CORRECCION_TABLAS_Y_DETALLE_OC_V2_2026-10-21.md).
- [Validación del detalle](VALIDACION_DETALLE_V2_2026-10-21.md).

## 3. Operación MER v2 y ETL

- **[Runbook: cierre de octubre, 10-11-2026](RUNBOOK_CIERRE_2026_10.md)** — pasos manuales supervisados.
- **[Procedimiento de cierre mensual](PROCEDIMIENTO_CIERRE_MENSUAL.md)** — operación, respaldo, conciliación y recuperación.
- [ETL diario Ubuntu](UBUNTU_ETL_DOS_FUENTES.md) — cron y dos fuentes principales.
- [Carga histórica y descargas oficiales](ETL_OPERATIVO_DESCARGAS_MASIVAS.md).
- [Cierre de carga histórica](cierre-carga-historica.md).
- [Plan maestro de 21 tareas](PLAN_MAESTRO_21_TAREAS.md) — antecedente de planificación; no es lista de pendientes actual.
- [Bitácora de orden y mantenimiento del repositorio](MANTENIMIENTO_REPOSITORIO_2026-10-21.md).

## 4. Fuentes, integraciones y contratos anteriores

Referencias conservadas para trazabilidad; **no sustituyen** el MER v2 vigente.

- [Integración ChileCompra](03-integracion-chilecompra.md).
- [Diccionario API-first](diccionario-api-first.md).
- [Compra Ágil y órdenes de compra](integracion-compra-agil-ordenes-compra-20261016.md).
- [Sincronización original Google Sheets](sincronizacion-google-sheets.md).
- [Contrato de datos V1](contrato-datos-v1.md).
- [Esquema objetivo histórico](esquema-objetivo.md).

## 5. Mantenimiento y calidad documental

- **[Mantenimiento del repositorio y limpieza segura](MANTENIMIENTO_REPOSITORIO_2026-10-21.md)** — inventario de ramas y workflows, archivos protegidos y política para futuras bajas.
- [Decisiones técnicas vigentes](DECISIONES_TECNICAS.md) — restricciones de cambio.
- [Pruebas automatizadas](../tests/) y [workflows GitHub Actions](../.github/workflows/) — evidencia comprobable; no confundir con pruebas visuales.

## 6. Archivo histórico

- **[README anterior completo](historial/README_LEGADO_2026-10-21.md)** — referencia íntegra previa, no instrucciones vigentes.
- Historial de decisiones y fallos: Git y documentos fechados; mantener información probatoria antes de pensar en eliminación.

## Política editorial

1. Cada README es **punto de entrada**, no bitácora. Estado actualizado, arquitectura y enlaces esenciales.
2. Las decisiones aprobadas se mantienen en [DECISIONES_TECNICAS.md](DECISIONES_TECNICAS.md); procedimientos de operación en sus propios documentos; evidencias fechadas en los informes correspondientes.
3. Distinguir claramente **codificado → CI aprobado → probado visualmente → ejecutado con datos operativos**.
4. Los JSON públicos de gran volumen, scripts con dependencias, credenciales locales (nunca versionadas), workflows en uso y V1/V2 no se eliminan en una limpieza editorial.
5. La auditoría integral del frontend V2, distinta de pruebas visuales puntuales, sigue pendiente y deberá planificarse independientemente.

- [Búsqueda de participantes históricos: proveedores y organismos](PARTICIPANTES_HISTORICOS_V2_2026-10-21.md) — consulta transversal, métricas y límites metodológicos.

- [Auditoría de vínculo Compra Ágil–OC (839-4-COT26)](AUDITORIA_VINCULO_CA_OC_2026-10-21.md): diagnóstico de 693.688 OC, referencia incompleta y candidata aún no confirmada.
