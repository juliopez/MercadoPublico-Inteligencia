# Migración AUX 16:15 a GitHub Actions — 12/11/2026

**Estado: PREPARADO EN PR #13, SIN ACTIVAR.** No se modificó el cron productivo de Ubuntu ni se fusionó el PR.

## Implementado
- Workflow remoto de activación manual, lotes de 200, pausa de 10 segundos.
- Checkpoint SQLite serializado en base64 y persistido en GitHub tras cada lote antes de escribir MER; respaldo adicional como artifact.
- Carga MER con preservación de PK existentes, exportación del mes operativo y publicación por lote de catálogo y fragmentos.
- Derivados y Pages: disparados por el workflow existente `publicacion-v2-post-etl.yml` al actualizar catálogo/fragmentos.
- Omite `exportar_vinculos_documentales_v2.py`, que se bloqueó el 12/11.

## Pendiente antes de pasar a productivo
1. Validar ejecución real en GitHub Actions y visibilidad en Pages. Ninguna ejecución del nuevo workflow ha sido probada.
2. Exclusión mutua con Ubuntu y otras escrituras MER. La concurrency de GitHub no protege frente al cron local.
3. Desactivar el trabajo local AUX-1615 y reemplazarlo por disparador remoto; esto requiere intervención en Ubuntu y no se puede realizar desde GitHub.
4. Considerar límite de 540 minutos, ventana 16:00-21:59, y reanudación al siguiente día; revalidar cuota API.
5. Si el piloto falla, conservar el cron actual y no ejecutar dos recuperaciones simultáneas.

## Operación actual
El cron local de las 16:00 no se modifica. El cron local de las 16:15 permanece intacto. El workflow de las 22:05 no se modifica. El PR #13 permanece en borrador para impedir activación accidental.
