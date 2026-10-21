# Observatorio de Inteligencia — Mercado Público (Chile)

Plataforma de análisis de licitaciones, Compra Ágil, ofertas, resultados y órdenes de compra. Código, procedimientos y extractos públicos en GitHub; fuentes operativas y MER v2 en **Google Sheets privadas**. Fecha de revisión documental: **21 de octubre de 2026**.

> **Regla de continuidad:** leer primero este README, después el [índice documental](docs/INDICE_DOCUMENTACION.md), las [decisiones técnicas](docs/DECISIONES_TECNICAS.md) y el documento de la tarea. Contrastar siempre con código, catálogo, ejecución de CI y validaciones reales; distinguir **implementado**, **validado técnicamente** y **probado visualmente**.

## Accesos

- **[Observatorio V2 — consulta y análisis](https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/)** (desarrollo paralelo con datos públicos).
- [Frontend V1 — versión original](https://juliopez.github.io/MercadoPublico-Inteligencia/) (se mantiene independiente).
- [Manual y estado funcional V2](frontend-v2/README.md).
- [Documentación ordenada por temas](docs/INDICE_DOCUMENTACION.md).
- [Decisiones técnicas vigentes](docs/DECISIONES_TECNICAS.md).

## Estado actual y cobertura

| Subsistema | Estado comprobado / restricción |
|---|---|
| Frontend V2 | Publicado en su ruta propia; selección por mes/entidad, bloques de hasta 1.000, paginación de 10, búsqueda global indexada y fichas relacionadas |
| Datos públicos V2 | Cinco períodos **2026-06 a 2026-10**; junio–septiembre históricos, octubre **parcial** |
| Entidades V2 visibles | Procesos, Ofertas, Resultados y Órdenes de compra (no confundir con las seis tablas internas del MER) |
| Funciones V2 | Indicadores interactivos por mes, perspectivas y comparación, perfiles, comparador con sugerencias, favoritos locales, CSV y enlaces entre registros |
| Relaciones multimes | Índices por código para Procesos, Ofertas, Resultados y OC, limitados a períodos publicados |
| V1 | Mantener `index.html` y `data/` aislados de `frontend-v2/` |
| ETL diario Ubuntu | Flujo operacional separado; no alterar por mejoras visuales |
| Cierre mensual MER | **Programado para supervisión manual el 10-11-2026**; no ejecutado a la fecha de este documento |
| Auditoría integral de V2 | **Pendiente**, separada de la validación funcional y de CI |

Los datos reales disponibles y su fecha se consultan en [el catálogo público V2](frontend-v2/data/catalogo-publico.json), no en cifras copiadas en documentos.

**Importante:** las cuatro entidades son conjuntos distintos. Ofertas informadas, resultados históricos, órdenes de compra y procesos no equivalen necesariamente a adjudicaciones jurídicas, operaciones únicas o pagos. Octubre no es comparable a meses cerrados sin advertencia de cobertura.

## Arquitectura y límites

```text
ZIP históricos oficiales y flujos operativos ChileCompra
           │
  Importación / ETL Ubuntu
           │
  Google Sheets privadas MER v2 (seis entidades)
           │ exportación pública controlada
           ▼
frontend-v2/data/catalogo-publico.json
 ├─ partes/                 JSON mensuales de hasta 1.000 filas
 ├─ busqueda/               índices de búsqueda global
 ├─ indices/ + relaciones-procesos/  vínculos multimes
 ├─ perfiles/ + autocompletar/      resúmenes y sugerencias
 └─ analitica/ + sugerencias/      agregados y controles
           │
    GitHub Pages V2 (sin acceso directo a Sheets)
```

El navegador **no debe descargar todos los históricos** para mostrar una página. La búsqueda por término y las relaciones utilizan índices y fragmentos públicos selectivos; los gráficos consultan agregados JSON. En la consulta por bloques, filtros y orden se aplican al bloque actual. El ordenamiento global afecta los resultados **ya comprobados**, no registros aún sin cargar. Los CSV de consulta global requieren completar la verificación y están limitados para evitar exportaciones parciales engañosas.

## Operación y próximo hito

**10 de noviembre de 2026:** cierre manual supervisado de octubre usando **tres ZIP oficiales** (licitaciones, Compra Ágil/COT y OC), respaldo previo, conciliación por PK, verificación de seis tablas y traslado de **la misma hoja** conservando su ID. Si falta fuente, permiso, respaldo o validación, detener el cierre. No configurar el cron mensual hasta aprobar este primer ciclo. No alterar el cron diario de Ubuntu.

Guías de referencia: [Runbook del cierre de octubre](docs/RUNBOOK_CIERRE_2026_10.md), [Procedimiento técnico de cierre](docs/PROCEDIMIENTO_CIERRE_MENSUAL.md), [ETL Ubuntu diario](docs/UBUNTU_ETL_DOS_FUENTES.md), [Modelo MER](docs/CONSOLIDADOR_MER_V2.md) y [Catálogo Sheets](docs/CATALOGO_SHEETS_Y_PERIODOS.md).

## Desarrollo y documentación

- **Frontend y UX V2:** [manual funcional](frontend-v2/README.md) y [analítica + relaciones históricas](docs/ANALITICA_INTERACTIVA_RELACIONES_HISTORICAS_V2_2026-10-21.md).
- **Validación automatizada:** consultar [workflows de GitHub Actions](.github/workflows/) y sus ejecuciones. CI no sustituye la prueba real en navegador ni operaciones contra Sheets.
- **Scripts:** `scripts/`; **pruebas:** `tests/`; **configuración:** `config/`. No publicar credenciales.
- **Archivo histórico:** [README legado íntegro](docs/historial/README_LEGADO_2026-10-21.md). Los documentos fechados describen hitos, **no prevalecen** sobre este estado actual y las decisiones vigentes.

Para buscar un documento, utilizar [el índice temático](docs/INDICE_DOCUMENTACION.md). No duplicar aquí bitácoras, fallos resueltos ni procedimientos extensos.
