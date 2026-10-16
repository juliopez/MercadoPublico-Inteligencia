# Cierre de carga histórica — 2026-10-16

## Procesos
- 10.000 códigos únicos verificados en Google Sheets: octubre de 2026 (821), septiembre (6.917), agosto (2.262).
- Cupo de 10.000 alcanzado. No se amplía con meses anteriores.

## Ofertas / Resultados — decisión de integridad
- Las muestras oficiales de licitaciones `2026-10.zip` y `2026-9.zip` contienen filas por producto/línea de oferta, además de campos de proveedor, importe, selección y adjudicación.
- **No ofrecen una clave de oferta individual verificada equivalente a `id_cotizacion` de la API V2 Compra Ágil**, que es la clave de deduplicación actual del ETL y la hoja `Ofertas`. `CodigoExterno + RutProveedor + Monto` no se acepta como clave artificial por posibles ofertas/líneas repetidas.
- Las columnas `Oferta seleccionada` o `FechaAdjudicacion` de los CSV no justifican por sí solas certificar contrato ni adjudicación verificada; tampoco sustituirán valores de la API.
- El archivo de Compra Ágil disponible localmente `COT_2025-12.zip` corresponde a diciembre de 2025, fuera de los procesos cargados (agosto–octubre 2026), y carece del identificador API `id_cotizacion`.
- **Resultado:** cero ofertas y cero resultados históricos importados con esos archivos. No rellenar los máximos 20.000/10.000 con registros sin relación o claves fiables. La ausencia se mostrará como cobertura no disponible.

## Puntos de cierre
1. Publicar el snapshot real de Sheets en GitHub Pages, sin inventar ofertas/resultados.
2. Unificar la ejecución diaria de procesos + detalle, con límite de tres intentos y registro persistente de fechas/modos pendientes, recuperables al día siguiente.
3. Mantener la diferenciación entre ofertas seleccionadas y adjudicaciones/OC verificadas.
4. No habilitar cron antes de que la orquestación de recuperación esté lista.
