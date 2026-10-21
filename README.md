# Plataforma Mercado Público — Observatorio de Inteligencia

Proyecto de análisis de licitaciones, Compra Ágil y órdenes de compra de ChileCompra, con frontend en GitHub Pages, carga de datos desde fuentes oficiales y almacenamiento mensual MER v2 en Google Sheets privadas.

> **Regla de continuidad (21-10-2026):** antes de cualquier tarea, leer este README, consultar el [índice documental](docs/INDICE_DOCUMENTACION.md), verificar las [decisiones vigentes](docs/DECISIONES_TECNICAS.md) y revisar el código y los resultados realmente ejecutados. Evitar repetir decisiones y soluciones ya validadas. No considerar «probado en producción» lo que solo superó pruebas offline.

## Estado del proyecto

| Componente | Situación |
|---|---|
| Frontend de consulta | Publicado en GitHub Pages; verificar publicación tras cambios de datos |
| MER v2 por mes, seis entidades | Implementado |
| Históricos de junio a septiembre de 2026 | Cargados y auditados con observaciones documentadas |
| ETL operativo diario de licitaciones y OC | Configurado en Ubuntu, separado del cierre mensual |
| Hoja octubre 2026 | Operativa; pendiente de cierre |
| Hoja noviembre 2026 | Preparada como destino operativo del nuevo mes |
| Cierre mensual | Scripts y runbook preparados; **no ejecutado todavía en producción** |
| Cron del cierre mensual | **No instalado** |

La configuración de períodos e identificadores vigente está en [`config/catalogo_sheets.json`](config/catalogo_sheets.json). Los documentos anteriores pueden conservar información histórica desactualizada: usar el registro de decisiones y el código actual para resolver dudas.

## Desarrollo paralelo del frontend MER v2

Se inició una versión independiente en [`frontend-v2/`](frontend-v2/README.md) para consulta por período con MER v2. **La versión 1 publicada (`index.html` y `data/`) se conserva intacta.** El catálogo público de v2 está vacío hasta generar extractos reales validados; no sustituir ni redirigir la publicación principal sin aprobación. Consulta el [inventario de funcionalidades heredadas de v1](frontend-v2/README.md).

## Línea base validada — frontend MER v2 (21-10-2026)

El usuario validó la navegación por períodos y entidades históricas y reportó **muy buena velocidad de carga** con lectura por fragmentos y **10 registros por página**. La referencia estable, cobertura y secuencia para recuperar las funciones de la versión 1 se registran en [BASELINE_FRONTEND_V2_2026-10-21.md](docs/BASELINE_FRONTEND_V2_2026-10-21.md). **Conservar este comportamiento antes de incorporar el detalle vinculado de ofertas, resultados y órdenes de compra.**

## Próximo hito — 10 de noviembre de 2026

**Primer cierre manual y supervisado de octubre**, sin desarrollar código nuevo durante la operación. Se requieren tres ZIP oficiales del **mes de octubre** (licitaciones, Compra Ágil/COT y órdenes de compra), conciliación con prioridad de la versión histórica oficial de ese mes, respaldo y verificación de seis entidades. Después se moverá **la misma hoja** desde Operativo a Históricos manteniendo su ID y se actualizará el catálogo GitHub.

**Guía de ejecución obligatoria:** [RUNBOOK_CIERRE_2026_10.md](docs/RUNBOOK_CIERRE_2026_10.md). **Procedimiento detallado:** [PROCEDIMIENTO_CIERRE_MENSUAL.md](docs/PROCEDIMIENTO_CIERRE_MENSUAL.md).

La cuenta de servicio dispone de JSON local en Ubuntu; **sus permisos efectivos para mover archivos Drive aún deben comprobarse**. Si falta una fuente, autorización o validación, detener el proceso sin archivar. Solo si el cierre manual es satisfactorio, configurar el cron mensual para el **10 de diciembre de 2026**. El cron diario no se altera.

## Arquitectura

```text
Archivos ZIP oficiales ChileCompra / APIs según flujo específico
            ↓
Importador MER v2 + ETL diario Ubuntu
            ↓
Google Sheets privadas por mes — catálogo de períodos
            ↓
Exportación y publicación autorizada
            ↓
Frontend GitHub Pages
```

La base MER v2 usa **Procesos, Ofertas, Resultados, OrdenesCompra, Proveedores y VinculosCOT_OC**. El esquema ejecutable está en [`scripts/importador_historicos_v2.py`](scripts/importador_historicos_v2.py). La arquitectura conceptual se describe en [CONSOLIDADOR_MER_V2.md](docs/CONSOLIDADOR_MER_V2.md).

## Procesos operativos

- **ETL diario Ubuntu:** [UBUNTU_ETL_DOS_FUENTES.md](docs/UBUNTU_ETL_DOS_FUENTES.md). Usa licitaciones y OC sin asumir que COT faltante equivale a cero.
- **Importación histórica:** [ETL_OPERATIVO_DESCARGAS_MASIVAS.md](docs/ETL_OPERATIVO_DESCARGAS_MASIVAS.md) y [cierre de carga histórica](docs/cierre-carga-historica.md). Reutilizar la experiencia de junio–septiembre.
- **Cierre mensual:** [runbook octubre](docs/RUNBOOK_CIERRE_2026_10.md) y [procedimiento técnico](docs/PROCEDIMIENTO_CIERRE_MENSUAL.md).
- **Validación del código:** [GitHub Actions](.github/workflows/validacion-mer.yml). Las pruebas offline no equivalen a ejecuciones reales contra Drive/Sheets.
- **Seguridad:** credenciales solo locales, respaldo verificable, bloqueo de concurrencia con el ETL diario, permisos generales restringidos y cierre condicionado a auditoría.

## Instalación y configuración

La operación supervisada se realiza sobre el entorno Ubuntu ya configurado en el proyecto. Antes de ejecutar cualquier comando, consultar las instrucciones del [runbook](docs/RUNBOOK_CIERRE_2026_10.md); no volver a descargar credenciales ni instalar componentes sin verificar primero la configuración existente. Los secretos no se publican en GitHub.

## Guía de documentación

**[Índice completo por temas](docs/INDICE_DOCUMENTACION.md)** · **[Decisiones técnicas vigentes](docs/DECISIONES_TECNICAS.md)** · [Catálogo y períodos](docs/CATALOGO_SHEETS_Y_PERIODOS.md) · [Plan maestro histórico](docs/PLAN_MAESTRO_21_TAREAS.md).

Los antecedentes extensos del README previo fueron conservados íntegros en [`docs/historial/README_LEGADO_2026-10-21.md`](docs/historial/README_LEGADO_2026-10-21.md). Son un **archivo histórico, no instrucciones vigentes**.

**Criterio editorial:** estado actual y próximos pasos en este README; decisiones estables en `DECISIONES_TECNICAS.md`; procedimientos en sus respectivos documentos; historial y detalles extensos en archivos especializados. Cambios relevantes requieren comprobar coherencia y enlaces.
