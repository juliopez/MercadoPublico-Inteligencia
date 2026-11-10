# Etapa 2 — Ensayo del escritor de libro de prueba

Fecha: 28/10/2026.

## Evidencias
- PR borrador: https://github.com/juliopez/MercadoPublico-Inteligencia/pull/1
- Ejecución de CI offline: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40790425381, job completado con `success`.
- La rama `etapa2/escritor-prueba-20261028` no está fusionada con `main`.
- El escritor solo permite `--aplicar-en-prueba`, ID explícito `MER_API_TEST_SHEET_ID` coincidente, rechazo del libro operativo y todos los IDs registrados en `config/catalogo_sheets.json`.
- Snapshot local con permisos 0600, uso de candado `logs/.mer_escritura_compartida.lock` y relectura posterior. Los ensayos realizados fueron con dobles de Sheets en memoria: **no son una prueba contra Google Sheets real**.
- Los fallos se tratan como `ESCRITURA_PARCIAL_POSIBLE`; no existe rollback automático transaccional entre pestañas.

## Pendientes bloqueantes
1. Copia de un libro de prueba MER completamente separada del catálogo operativo y con acceso adecuado para la cuenta de servicio.
2. Ensayo de inserción, lectura posterior e idempotencia en esa copia, con datos sintéticos y respaldo real.
3. Validación del manejo de fallas parciales y recuperación supervisada.
4. Integración aislada a exportación, catálogo, índices y página web, con pruebas de regresión. No desplegar datos sintéticos al portal público.
5. Captura del JSON real de una única llamada API, sólo después de las verificaciones anteriores.

No se invocó la API ni se alteraron la hoja operativa, los ETL, cron, catálogo público o Pages.
