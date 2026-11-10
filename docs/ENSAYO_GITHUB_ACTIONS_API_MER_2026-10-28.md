# Ensayo independiente de publicación API → MER → frontend

- Se añadió `scripts/ensayo_publicacion_api_mer.py`: crea filas de Ofertas y Resultados sintéticas en memoria, genera partes JSON y manifiesto con el formato de `catalogo-publico.json`, reabre los archivos y valida conteos.
- Se añadió `.github/workflows/ensayo-api-mer-frontend.yml`: workflow exclusivamente manual o de PR, permisos `contents: read`, sin secretos ni conexiones externas y **sin despliegue de Pages**.
- Esta prueba está separada del cron de Ubuntu y de los workflows productivos, que permanecen sin cambios.
- La copia real de Google Sheets ya fue usada para escritura sintética mediante el conector, pero el nuevo ensayo automatizado NO escribe en esa copia ni ejecuta Google Apps Script.
- Para publicar registros reales siguen siendo necesarios: credencial de Google Sheets para el workflow elegido, upsert protegido y verificado con la copia real, ampliación del exportador operativo y puesta en marcha controlada del publicador. No afirmar que el flujo extremo a extremo está listo hasta verificar esos puntos.
- No se consultó ChileCompra.
