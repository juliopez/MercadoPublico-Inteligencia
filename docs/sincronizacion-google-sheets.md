# Sincronización automática ChileCompra → Google Sheets

El workflow `Sincronizar ChileCompra a Google Sheets` se programa diariamente a las 11:00 UTC (08:00 Chile en horario de verano; 07:00 durante horario estándar). GitHub puede retrasar las ejecuciones programadas. También admite ejecución manual.

## Configuración única requerida (no colocar credenciales en archivos públicos)

1. En Google Cloud Console, crear/seleccionar un proyecto, habilitar **Google Sheets API** y crear una **cuenta de servicio** con clave JSON. La clave es sensible; restringirla y rotarla cuando sea necesario. No confundir Google AI Pro con permisos de Google Cloud.
2. En Google Sheets, compartir **Observatorio Mercado Público — Base de Datos** con el correo de la cuenta de servicio, con permiso **Editor**. Es el libro con ID `1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4`.
3. En GitHub Settings → Secrets and variables → Actions → Secrets, configurar **GOOGLE_SERVICE_ACCOUNT_JSON** con el JSON completo de la clave. Conservar **CHILECOMPRA_TICKET** previamente configurado.
4. En GitHub Settings → Secrets and variables → Actions → Variables, crear **GOOGLE_SHEET_ID** con valor `1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4`.
5. Ejecutar manualmente el workflow una vez y revisar los logs antes de dejar que opere diariamente.

## Comportamiento

Consulta procesos publicados durante los últimos 7 días con término 'capacitacion', hasta 20 páginas de 50 resultados. Si la página máxima excede el tope, **no modifica Google Sheets** para evitar cargas parciales. Inserta procesos nuevos y actualiza las filas existentes identificadas por `codigo`; completa la columna P con fecha de sincronización. Mantiene `Ofertas`, `Resultados` y `Indicadores` intactas. **No sincroniza todavía ofertas individuales ni adjudicaciones.**

Se preservan códigos existentes de otros procesos. Los procesos que dejen de aparecer en la ventana no se borran. Las fechas y montos provienen de los campos oficiales; el presupuesto disponible no es un monto adjudicado.

El informe Looker Studio conectado a la pestaña Procesos podrá refrescar sus datos según sus propios intervalos de caché; GitHub Actions no fuerza actualización instantánea.

## Seguridad y fiabilidad

No incorporar secretos al repositorio ni ejecutar el workflow hasta configurar ambos secretos. La autenticación con Google se realiza solo en GitHub Actions. Para mejorar fiabilidad más adelante, migrar a Workload Identity Federation y sincronización incremental con marcador de fecha / reintentos para estados transitorios.
