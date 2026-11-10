# Consolidación de pruebas antes de API — 28/10/2026

## Ejecución en un solo bloque, sin consultar ChileCompra
- Libro de prueba real, separado del MER operativo: https://docs.google.com/spreadsheets/d/18iPCaHbNTpjIfgMsNu3ZhQ0u9lBqx4_zaDdWgrSkcqY/edit
- Relectura adicional: una sola fila `Ofertas` con ID `TEST-API-0001`/proceso `TEST-20261028-COT26` y una sola fila `Resultados` con código `TEST-20261028-COT26` y ganadora `TEST-API-0001`. Repetir la comprobación no produjo escrituras adicionales. Es comprobación de no duplicación por conector, **no** ejecución del escritor Python en Google Sheets.
- CI de falla parcial y recuperación con doble de Sheets en memoria: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40790921461, success.
- Validador aislado nuevo: `scripts/validar_preview_api_mer_aislado.py`, ensaya manifiesto, partes y campos públicos con datos sintéticos, sin tocar `frontend-v2/data`, cron ni API.
- CI del validador: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40791097164 (verificar conclusión de ejecución).
- El frontend actual YA reconoce entidades `ofertas` y `resultados` y lee `partes` desde el catálogo, pero el exportador/publicador operativo todavía no incluye esas entidades: preview aislada no equivale a despliegue Pages.

## Único impedimento operativo para certificar la ejecución real con Python
La cuenta de servicio que utiliza Ubuntu es un archivo local `GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/mercadopublico/servicio-google.json`; los conectores Drive disponibles no exponen esa identidad ni ejecutan comandos en la máquina Ubuntu. Por ello no se puede certificar desde este entorno que esa cuenta tenga acceso al libro copiado. El escritor protegido del PR #1 no se ha ejecutado con esas credenciales.

**Habilitación pendiente:** validar la cuenta de servicio Ubuntu en la copia de ensayo, proteger recuperación de escrituras parciales y ampliar de manera regresiva el exportador/publicador del cron; no autorizar API masiva o publicación real mientras existan estas brechas. No se hizo llamada API ni se modificaron Sheets productivas.
