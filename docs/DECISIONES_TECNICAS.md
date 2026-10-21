# Decisiones técnicas vigentes — Plataforma Mercado Público

**Última revisión:** 21-10-2026. Documento de continuidad y decisiones **vigentes**, no bitácora de experimentos. Antes de desarrollar, consultar [README](../README.md), [índice](INDICE_DOCUMENTACION.md) y código/configuración real.

## Arquitectura

- Repositorio: `juliopez/MercadoPublico-Inteligencia`; frontend publicado en GitHub Pages; Google Sheets privadas con un libro MER v2 por mes.
- MER v2 de **seis tablas**: `Procesos`, `Ofertas`, `Resultados`, `OrdenesCompra`, `Proveedores`, `VinculosCOT_OC`. Los esquemas efectivos están en `scripts/importador_historicos_v2.py`; el catálogo en `config/catalogo_sheets.json`.
- Histórico consolidado: junio–septiembre de 2026, con experiencia acumulada de importación masiva. **No repetir pruebas de los importadores sin cambios que introduzcan nuevos riesgos**.
- ETL operativo diario de licitaciones y OC por ZIP oficial: se conserva y no debe detenerse. Compra Ágil sigue tratamiento diferenciado y el histórico mensual requiere tres fuentes oficiales completas.

## Regla del cierre del período

- Unidad de cierre: **mes calendario**, sin extrapolar ni mezclar filas de otros meses.
- En PK compartidas, **prevalece íntegramente la fila del último ZIP histórico oficial del mes** sobre el valor operativo, incluso si la celda oficial está vacía.
- En PK exclusivas del histórico, insertar; en PK exclusivas del operativo, conservar sin borrar automáticamente y documentar diferencias de cobertura.
- No deducir adjudicación jurídica confirmada de selecciones informativas.
- Respaldo completo y verificable ANTES de escribir; verificación de las seis tablas DESPUÉS de la carga; recuperar de modo idempotente ante interrupciones. Mantener candado `logs/.mer_escritura_compartida.lock` compartido con el ETL diario.

## Operación de noviembre

- **10 de noviembre de 2026:** primer cierre **manual y supervisado** de `MER_2026_10_OPERATIVO` empleando los tres ZIP oficiales de octubre. La fecha es para ejecutar el procedimiento, **no desarrollar scripts**.
- Tras cargar y verificar, mover el **mismo archivo**, conservando ID, desde `02_Operativo_MER` a `01_Historicos_MER`; actualizar catálogo GitHub solo después de confirmar Drive.
- Guía de operación: [RUNBOOK_CIERRE_2026_10.md](RUNBOOK_CIERRE_2026_10.md). La cuenta de servicio utiliza el JSON local en Ubuntu `~/.config/mercadopublico/servicio-google.json`; **el JSON no demuestra automáticamente capacidad de mover archivos entre carpetas**. Comprobar permisos efectivos con la herramienta no destructiva antes del cierre, sin exponer secretos.
- Si faltan ZIP, respaldo, permisos, autorización o verificaciones, **detener el cierre y registrar bloqueo**, sin traslado.
- El cron **mensual no está instalado**. Solo se habilitará si el cierre manual resulta satisfactorio; primer ciclo previsto el **10 de diciembre de 2026**. No modificar el cron diario vigente por esta tarea.

## Frontend V2 — decisiones de arquitectura vigentes (21-10-2026)

- V2 se publica en `frontend-v2/` sin reemplazar ni alterar V1 (`index.html` y `data/` de raíz). El frontend no consulta directamente Google Sheets ni muestra campos operativos privados.
- Períodos públicos **junio–octubre de 2026**, con octubre parcial. La cobertura real debe leerse de `frontend-v2/data/catalogo-publico.json`. Cuatro entidades públicas: Procesos, Ofertas, Resultados y Órdenes de compra. No confundirlas con las seis tablas del MER.
- Rendimiento prioritario: fragmentos de hasta 1.000 registros, paginación de 10, índices y agregados públicos para búsqueda/perfiles/analítica y relaciones multimes. No restaurar carga masiva del histórico en cliente.
- Búsqueda global y vínculos entre meses usan códigos y filtros informativos; la coincidencia no equivale a adjudicación verificada. Montos descriptivos en CLP, no necesariamente pago. El ordenamiento global solo aplica a resultados examinados progresivamente.
- Interfaces analíticas, comparador, favoritos y exportación deben conservar sus límites visibles: períodos incompletos, nombres de empresas no necesariamente unívocos por RUT, y CSV global con límite de consulta completa.
- Pruebas automatizadas y validación visual son hitos diferentes. **Auditoría integral V2 pendiente como tarea independiente**, aunque numerosas mejoras puntuales ya fueron comprobadas.
- La publicación de JSON agregados debe activar el despliegue de Pages y tener reconciliación contra el catálogo. Mantener por separado exportadores, generación de índices y frontend.

## Protocolo documental

1. Antes de cualquier tarea: leer README e índice, luego la decisión vigente y el documento específico. Contrastar con el código real y resultados de ejecución.
2. Separar estados: diseñado / codificado / probado offline / probado con servicios / ejecutado en producción.
3. Evitar añadir código o pruebas redundantes: reutilizar la experiencia de las cargas masivas. Consolidar verificaciones automáticas en GitHub Actions.
4. Actualizar este documento solo cuando cambien **decisiones aprobadas**. Registrar detalles, intentos y resultados en documentación técnica específica y no convertir el README en bitácora.
5. Ante contradicción documental, prevalecen este registro de decisiones y el runbook vigente **solo si son consistentes con la implementación y la evidencia real**; si no, señalar la discrepancia sin presuponer funcionamiento.
