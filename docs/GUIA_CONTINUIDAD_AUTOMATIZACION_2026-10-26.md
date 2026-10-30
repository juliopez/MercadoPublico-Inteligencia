# Guía de continuidad — automatización del Observatorio (26-10-2026)

> **Archivo histórico, sustituido para continuidad actual** por [Estado y continuidad del 30/10](ESTADO_Y_CONTINUIDAD_2026-10-30.md).

**Propósito:** punto de entrada para una nueva conversación. Esta guía es un mapa de trabajo, **no acredita una ejecución del cron del 26/10** ni autoriza escrituras.

## Orden de lectura y autoridad
1. [README principal](../README.md): arquitectura y alcance.
2. [Decisiones técnicas](DECISIONES_TECNICAS.md): restricciones obligatorias y reglas vigentes.
3. [Cierre técnico y validación del 22/10](CIERRE_OPERATIVO_Y_VALIDACION_2026-10-22.md), [cron integrado](CRON_INTEGRADO_UBUNTU_2026-10-22.md), [publicación post-ETL](PUBLICACION_MER_V2_POST_ETL_2026-10-22.md): última evidencia operativa documentada; sus descripciones pueden reflejar fases sucesivas del mismo día.
4. [Manual V2](../frontend-v2/README.md) y [catálogo público](../frontend-v2/data/catalogo-publico.json): funcionalidad y cobertura publicada.
5. [Runbook octubre](RUNBOOK_CIERRE_2026_10.md): **procedimiento específico vigente** del primer cierre, previsto para el 10/11/2026. [Procedimiento mensual](PROCEDIMIENTO_CIERRE_MENSUAL.md) es antecedente de diseño general y no reemplaza las decisiones posteriores.
6. Código, workflows, logs, estados locales, Google Sheets y GitHub Actions: **evidencia real por verificar**. Ante discrepancias, no declarar éxito; inspeccionar e informar.

## Secuencia de trabajo aprobada como objetivo
**Etapa 1 — 26/10: validación sin nuevas cargas.** Comprobar el cron Ubuntu de lunes a viernes a las 16:00 America/Santiago, ETL Licitaciones/OC, conciliación COT–OC, Sheets, exportación, git push, GitHub Actions de las 17:00, índices, catálogo y Pages. Distinguir instalado / simulado / ejecutado / datos publicados / navegación comprobada. Revisar especialmente la incidencia EXDEV del 22/10 y la corrección posterior. Los logs Ubuntu no son accesibles desde GitHub: solicitarlos solo si no existe vía conectada para verlos. **No asumir que la ejecución del 26/10 ya ocurrió o fue exitosa.**

**Etapa 2 — API ChileCompra.** Auditar clientes y esquemas actuales antes de desarrollar. Completar Compra Ágil, Ofertas y Resultados según cobertura realmente disponible; evaluar fallos de lotes v2 (504/timeout) y consultas individuales con reintentos limitados. Mantener distinción selección / adjudicación verificada, idempotencia y procedencia.

**Etapa 3 — orquestación integrada.** Incorporar fuentes gradualmente, con bloqueos, validación por entidad, recuperación, bitácoras, publicación condicionada e índices regenerados. No detener el ETL diario actual ni reproducir históricos completos.

**Etapa 4 — primer cierre octubre.** Preparar controles para el **10/11/2026**. Mantener cierre **manual supervisado** bajo [runbook](RUNBOOK_CIERRE_2026_10.md): tres ZIP oficiales, respaldo, conciliación por PK, verificación seis tablas, permisos Drive, autorización documentada y traslado del **mismo archivo/ID** a históricos. **No instalar cron mensual ni efectuar el traslado sin aprobación y pruebas.**

**Etapa 5 — apertura y automatización mensual.** Diseñar apertura del nuevo mes, catálogo, credenciales, permisos y rotación de ETL. La automatización del cierre mensual es meta futura, condicionada a un primer cierre manual satisfactorio, gestión auditada de rectificaciones oficiales y autorización independiente.

## Protecciones
- Mantener V1 separado de V2; conservar seis tablas MER y cuatro entidades públicas.
- No editar manualmente JSON generados ni exponer credenciales, PII, ZIP originales o logs privados.
- No confundir publicación de código, CI verde, datos publicados y resultado visible en Pages.
- No duplicar importadores, reinsertar PK existentes, reprocesar meses cerrados o alterar reglas de precedencia.
- Los archivos de planificación del 21/10 son **antecedentes**, no el estado del cron integrado instalado el 22/10.
- Registrar hallazgos y evidencias en un informe nuevo fechado, sin sobrescribir la bitácora histórica.

## Primer resultado exigido en el próximo chat
Emitir un diagnóstico de la ejecución **lunes 26 de octubre de 2026**, con evidencias concretas para Ubuntu 16:00 → Sheets → GitHub 17:00 → Pages, estado confirmado / fallo / no verificable, y corrección mínima recomendada. **No iniciar la API antes de cerrar este diagnóstico.**
