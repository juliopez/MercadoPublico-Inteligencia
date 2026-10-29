# Activación autónoma MER API — condiciones y estado
**Fecha:** 28 octubre 2026

Se preparó `scripts/ejecutar_mer_api_incremental_nocturno.py` para una primera ejecución nocturna controlada, con máximo 10 detalles (5 por defecto), filtro de mes oficial, sin sobrescribir ofertas ni resultados existentes, parada ante HTTP 429 y seguimiento de errores.

**IMPORTANTE: NO ESTÁ ACTIVADO.** No es correcto presentar este prototipo como una solución completa por estas razones:

1. El conector de Google Sheets usado de manera interactiva no entrega por sí solo una cuenta de servicio para ejecuciones autónomas de GitHub Actions. Debe confirmarse el acceso `GOOGLE_APPLICATION_CREDENTIALS` para el MER operativo, bajo identidad autorizada.
2. Se requiere una pestaña técnica `_Control_API` aprobada; el ejecutor aborta si falta, no altera el modelo oficial inadvertidamente.
3. La paginación está configurada por `MER_API_PAGE` y necesita cursor persistente para cubrir todo octubre sin reprocesar solo la primera página.
4. La consulta mensual a `Procesos` después del cierre aún necesita integrarse con el importador histórico de Compra Ágil existente; no utilizar este ejecutor de ofertas como sustituto de la carga mensual.
5. Debe probarse la estructura real de listado, la idempotencia, la fecha de publicación oficial, y mejorar recuperación de escrituras parciales (Sheets no ofrece transacción multi-tabla).
6. No habilitar el cron ni prometer plazo de 48h mientras haya 429 y no se conozca capacidad efectiva del ticket.

Próximo paso operativo: resolver credenciales autónomas y persistencia de control, ensayo de extremo a extremo en copia, integración del importador mensual y publicación. Conservar intactos cron Ubuntu 16:00 y workflow de publicación de 17:00.
