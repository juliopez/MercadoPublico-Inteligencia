# Mantenimiento y orden del repositorio — 21-10-2026

## Propósito
Registrar el saneamiento documental y la revisión segura de GitHub durante la validación visual de frontend V2. **No confundir limpieza del repositorio con eliminación de información histórica o automatizaciones en servicio.**

## Inventario verificado
- Raíz: `README.md`, `index.html` (V1), `data/` (V1), `frontend-v2/`, `docs/`, `scripts/`, `tests/`, `config/`, `colab/`, `.github/`, `.gitignore`.
- Ramas comprobadas: `main` y `respaldo-pre-limpieza-marcha-blanca-20261016`. **Se conserva la rama de respaldo.**
- `docs/`: documentación vigente, guías de operación y bitácoras históricas fechadas. No borrar bitácoras porque explican decisiones técnicas y fallos resueltos.
- `.github/workflows/`: flujos de publicación V1/V2, operación MER, generación de índices/agregados y pruebas de regresión. Se conservan hasta validar dependencias, disparadores y reemplazos.
- `frontend-v2/data/`: catálogo, fragmentos e índices públicos **necesarios para GitHub Pages**. No eliminarlos.
- `scripts/`: herramientas de carga operativa y de publicación; los nombres similares no prueban redundancia. No ejecutar scripts de escritura en Sheets durante esta revisión.
- `.gitignore`: protege secretos locales, cachés, bases temporales, dependencias; preserva expresamente datos públicos versionados.

## Hallazgos y decisiones
1. El índice documental referenciaba este mismo documento, que **no existía**. Se creó para reparar la navegación documental.
2. Había registros de implementación puntuales que podían parecer instrucciones vigentes. El README principal y el de frontend V2 se mantienen como resúmenes ejecutivos; el índice separa estado, operación, implementación y trazabilidad.
3. Existen numerosos workflows de pruebas incrementales. Su eliminación sin una matriz de equivalencia podría anular regresiones o afectar despliegues, por lo que **no se borran automáticamente**. Revisión posterior: confirmar qué pruebas están cubiertas por suites vigentes y eliminar solo por aprobación de lista específica.
4. No borrar ni fusionar `main`, respaldo, `index.html`, `data/`, fuentes JSON públicos, historiales de operaciones o automatizaciones de MER.
5. No se modificó Google Sheets ni se ejecutaron ETL, importadores, cierres mensuales o regeneración de históricos.

## Catálogo de operaciones seguras en GitHub
| Área | Criterio |
|---|---|
| Documentación | Actualizar README, índice y enlaces rotos; conservar documentos históricos fechados |
| Pruebas | Mantener suites; consolidar solo después de verificar cobertura y frecuencia |
| Workflows de publicación | Mantener hasta comprobar rutas, disparadores y permisos |
| Datos públicos V2 | Proteger y reconciliar contra catálogo; nunca limpiar por tamaño |
| Rama de respaldo | Conservar como punto de recuperación |
| Secretos y archivos locales | Excluir por `.gitignore`; evitar publicar secretos |

## Próximos controles separados
- Auditoría integral frontend V2: funcionalidad, rendimiento, accesibilidad y comparación V1/V2.
- Inventario de workflows activos y redundantes con trazabilidad de eventos; una eliminación requiere prueba de sustitución.
- Verificación automática de enlaces Markdown y documentación de nuevos períodos cuando se publiquen.

**Regla:** toda eliminación futura debe citar ruta exacta, justificación, sustitución y verificación posterior. No atribuir a este mantenimiento borrados de código, datos o workflows que no se hayan efectuado.

## Cierre documental de jornada (21–22/10/2026)

Se actualizaron `README.md`, `frontend-v2/README.md` y `docs/INDICE_DOCUMENTACION.md` para reflejar búsqueda transversal, detalle multimes, relación unificada de OC, enriquecimiento por ZIP y tareas pendientes. Se incorporó [plan de continuidad para cron 16:00](PLAN_MEJORAS_CRON_1600_2026-10-21.md).

**Limpieza efectuada: documental, no destructiva.** Se reorganizaron referencias del índice y retiraron afirmaciones de estado desactualizadas del manual V2, conservando los documentos de evidencia histórica. **No se borraron ramas, scripts, workflows, índices JSON ni logs**, porque sus dependencias no fueron auditadas individualmente. La depuración física sigue condicionada a inventario de uso, equivalencia y autorización.

El cron y ETL siguen intactos; no se ejecutaron trabajos operativos en el cierre documental. Verificar estado de Actions y despliegue real de las mejoras recientes antes de dar por aprobada la revisión visual.
