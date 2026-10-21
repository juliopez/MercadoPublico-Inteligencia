# Índice de documentación — Observatorio Mercado Público

> **Punto de entrada:** [README](../README.md) → este índice → documento de la tarea → código/configuración real.
> Los documentos antiguos describen etapas históricas; **no prevalecen sobre las decisiones vigentes** recogidas en [DECISIONES_TECNICAS.md](DECISIONES_TECNICAS.md).

## 01. Arquitectura, catálogo y modelo

- [Consolidador MER v2](CONSOLIDADOR_MER_V2.md) — arquitectura por catálogo, carpetas y frontend.
- **[Auditoría tarea 14: consolidador y frontend](AUDITORIA_T14_CONSOLIDADOR_FRONTEND.md)** — compatibilidad efectiva, riesgos y condiciones para implementar consolidación por período.
- [Catálogo Sheets y períodos](CATALOGO_SHEETS_Y_PERIODOS.md) — inventario, estructura y decisiones de preservación.
- [Especificación de Proveedores y Vínculos COT–OC](Especificacion_Proveedores_Vinculos_COT_OC.md) — definición de dos entidades del MER v2.
- [Modelo MER propuesto](MER_propuesto.mmd) — diagrama fuente Mermaid.
- [Esquema objetivo](esquema-objetivo.md) — diseño histórico del contrato; contrastar con MER v2 vigente.
- [Contrato de datos v1](contrato-datos-v1.md) — versión anterior, referencia histórica, **no especificación vigente**.

## 02. Fuentes e integraciones

- [Integración ChileCompra](03-integracion-chilecompra.md) — verificación histórica API Compra Ágil v2.
- [Diccionario API-first](diccionario-api-first.md) — diseño API previo; no confundir con ETL actual por ZIP.
- [Integración Compra Ágil–OC](integracion-compra-agil-ordenes-compra-20261016.md) — antecedentes y criterios del diseño.
- [Sincronización con Google Sheets](sincronizacion-google-sheets.md) — documentación original de sincronización.

## 03. Procesamiento ETL e históricos

- [ETL de descargas masivas](ETL_OPERATIVO_DESCARGAS_MASIVAS.md) — fuentes ZIP y antecedentes de implementación.
- [Operación Ubuntu con dos fuentes](UBUNTU_ETL_DOS_FUENTES.md) — ETL diario operativo, respaldo y cron.
- [Cierre de carga histórica](cierre-carga-historica.md) — evidencia del trabajo histórico anterior.

## 04. Operación y cierre mensual

- **[Runbook del 10 de noviembre de 2026](RUNBOOK_CIERRE_2026_10.md)** — guía principal de ejecución manual supervisada de octubre.
- [Procedimiento de cierre mensual](PROCEDIMIENTO_CIERRE_MENSUAL.md) — especificaciones y bitácora técnica extensa. **Las decisiones recientes prevalecen sobre apartados históricos contradictorios.**

## 05. Validación, seguridad y decisiones

- **[Decisiones técnicas vigentes](DECISIONES_TECNICAS.md)** — criterios aprobados, jerarquía de fuentes, permisos, límites y próximos hitos.
- Los controles del cierre y recuperación se documentan en [procedimiento mensual](PROCEDIMIENTO_CIERRE_MENSUAL.md).
- La validación automática está en [GitHub Actions](../.github/workflows/validacion-mer.yml).

- **[Línea base estable frontend v2 (21-10-2026)](BASELINE_FRONTEND_V2_2026-10-21.md)** — validación del usuario, conteos, límites y siguiente fase: recuperar detalle vinculado de v1.

- **[Detalle relacionado frontend v2](DETALLE_RELACIONADO_FRONTEND_V2.md)** — vínculos por código y período, índices compactos, publicación y verificación requerida.

## 06. Plan e historial

- [Plan maestro de 21 tareas](PLAN_MAESTRO_21_TAREAS.md) — planificación histórica; **no equivale al estado actual**.
- La cronología técnica del cierre está preservada en [procedimiento mensual](PROCEDIMIENTO_CIERRE_MENSUAL.md).
- [README original y evolución](../README.md) — incorpora antecedentes históricos acumulados; consultar primero su sección inicial de orientación.

## Regla editorial

La información se consulta en este orden: **README vigente → decisiones vigentes → runbook/procedimiento específico → código y configuración comprobados → historial**. No afirmar «ejecutado» por tener solo código o CI aprobado. Al modificar documentación, revisar enlaces y no borrar material histórico sin conservar una copia íntegra.

- [Mejoras integrales de experiencia V2 — 21-10-2026](MEJORAS_UX_INTEGRALES_V2_2026-10-21.md): nueve mejoras aprobadas (búsqueda, filtros, navegación, progreso, fichas, contexto, accesibilidad, moneda CLP y códigos) y sus límites de validación.
