# Despliegue de índices históricos de nombres (R2 privado)

## Estado
El PR #20 está fusionado. Se generó y validó un artefacto histórico aislado en GitHub Actions (run 43649647588), pero no se publicó en Pages ni en Cloudflare. El índice comprimido ocupó aproximadamente 154 MB. La consulta por nombres no estará disponible hasta completar R2 y actualizar el Worker.

## Decisión de arquitectura
No publicar masivamente índices de nombres en GitHub Pages: el Observatorio es de uso personal y el corpus derivado es grande. Usar bucket R2 privado y binding solo accesible al Worker. No tocar ETL, cron, MER ni las cinco consultas existentes.

## Acciones únicas de configuración
1. En Cloudflare R2, crear bucket privado **observatorio-indices-nombres** (sin dominio público).
2. Crear token de API de R2 con lectura/escritura limitada a ese bucket; guardar Access Key ID y Secret Access Key.
3. En GitHub, repositorio > Settings > Secrets and variables > Actions, crear tres secretos: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`. Nunca enviarlos al chat.
4. En Cloudflare > Workers & Pages > Worker `observatorio-mercado-publico-ia` > Settings > Bindings, añadir R2 bucket binding **NOMBRES_BUCKET** al bucket `observatorio-indices-nombres`.
5. Ejecutar manualmente workflow **Publicar indices privados de nombres en R2**. Comprobar resultado y cobertura antes de actualizar Worker.
6. Desplegar Worker actualizado desde `scripts/asistente_ia/worker/index.mjs` (requiere la vía habitual de despliegue de Cloudflare). Verificar /health y consultas existentes antes de probar búsquedas por nombre.

## Precauciones
- El workflow publica solo `manifiesto.json` y `clave-*.ndjson` por mes; no publica los archivos de origen por partes.
- No activar un cron de actualización del índice hasta acordar política de sincronización con la publicación mensual/diaria de los datos.
- Una coincidencia textual no demuestra identidad, participación personal ni adjudicación contractual.
- La ausencia de un índice actualizado debe producir respuesta de indisponibilidad, nunca una falsa ausencia de participantes.
