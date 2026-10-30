# Orquestación API Compra Ágil desde Ubuntu — instalación y control

> **Actualización 30/10 — diseño escalable preparado:** el límite técnico de 10 ya se amplió a **1–50 detalles por ejecución**, con recorrido de varias páginas y pausa mínima de 3 segundos. `scripts/cron_api_compra_agil_ubuntu.sh` ejecuta la API fuera del filtro horario de GitHub, con lote configurable, bloqueo compartido y validación del reporte. El timer horario `deploy/systemd/mercadopublico-api.timer` está **preparado pero NO habilitado en Ubuntu**; primero ejecutar y revisar un lote real de 25, luego uno de 50. El schedule de GitHub API permanece desactivado. Esto NO constituye prueba real de 25/50 ni demuestra capacidad del servicio. La primera prueba exitosa previa de 10 procesos sí está documentada; ver `docs/AUDITORIA_API_MER_2026-10-28.md`.


**Estado: código preparado en GitHub; cron local NO activado desde ChatGPT.** Fecha: 30-10-2026.

## Arquitectura
- Cron Ubuntu de las 16:00: **no modificar**; procesa licitaciones y OC.
- Nuevo cron Ubuntu propuesto 20:00 Santiago, lunes–viernes: ejecutar `scripts/cron_api_compra_agil_ubuntu.sh`. Inicialmente 25 detalles por ejecución; máximo técnico actual 50 hasta validar estabilidad.
- El schedule automático GitHub para la API queda **desactivado** en `.github/workflows/observacion-api-2230.yml`; `workflow_dispatch` permanece para contingencias **sin simultaneidad**.
- El script emplea el mismo `scripts/mer_api_incremental_10.py`, `control/cola_api_mer.json`, MER y exportador, con bloqueos locales `flock`; no consultar de forma paralela desde GitHub.
- El código de API admite `GOOGLE_APPLICATION_CREDENTIALS` (ruta absoluta a archivo JSON de cuenta de servicio) y `CHILECOMPRA_TICKET`; también `GOOGLE_SERVICE_ACCOUNT_JSON`. No publicar secretos en Git.

## Pasos en Ubuntu, una sola vez
1. En el clon local existente, hacer `git pull --ff-only origin main` (desde el directorio del repositorio).
2. Asegurar Python, `gspread`, `google-auth`, `flock`, `git` y `gh` autenticado (`gh auth status`); verificar cuenta de servicio con permisos **de escritura** en el Sheet operativo del mes.
3. Crear `~/.config/mercadopublico/api.env` con permisos `chmod 600`. Contenido ilustrativo:
   ```bash
   export CHILECOMPRA_TICKET='COLOCAR_TICKET_REAL_LOCALMENTE'
   export GOOGLE_APPLICATION_CREDENTIALS='/ruta/absoluta/privada/servicio-google.json'
   ```
   **Jamás subir este archivo al repositorio ni pegar credenciales en conversaciones.** No modificar archivos secretos ya válidos del ETL de las 16:00.
4. Instalar mediante `crontab -e` una línea, únicamente cuando la zona horaria de Ubuntu esté comprobada:
   ```cron
   0 20 * * 1-5 /bin/bash "/RUTA/ABSOLUTA/AL/REPO/scripts/cron_api_compra_agil_ubuntu.sh" >> "$HOME/mercadopublico-api-cron.log" 2>&1
   ```
   Sustituir `/RUTA/ABSOLUTA/AL/REPO` por `pwd`. En cron, usar ruta absoluta del archivo de log si `$HOME` no está configurado. Comprobar `timedatectl`; para zona distinta de `America/Santiago`, adaptar cron a esa zona mediante el mecanismo de zona horaria de cron de esa instalación (no suponer que una variable TZ cambia la hora de cron).
5. Para prueba **sin consultas**, validar `bash -n scripts/cron_api_compra_agil_ubuntu.sh`, dependencias, secrets presentes y `gh auth status`. Para prueba real, usar solamente un lote controlado y **no ejecutar simultáneamente** con otro escritor API o ETL.

## Restricciones y riesgos conocidos
- El script llama `git pull --ff-only` al iniciar y se detiene si detecta cambios locales; usa archivo de bloqueo para evitar doble cron local.
- Actualiza `Procesos`, `Ofertas`, `Resultados`, exporta datos, registra estado y publica; requiere Git push autenticado.
- La implementación existente de 10 procesos tiene controles de cursor, seguimiento y HTTP 429. No aumentar el límite hasta pruebas de capacidad.
- La publicación derivada posterior se invoca con `gh workflow run publicacion-v2-post-etl.yml --ref main`, si `gh` está autenticado. Si no, el script advierte que deberá verificarse la publicación.
- **Precaución:** el exportador puede escribir fragmentos grandes y el repositorio contiene muchos archivos; monitorizar tiempos, espacio y permisos.
- **Importante**: el script de Python no trabaja de forma transaccional con Sheets y Git. Ante fallo a mitad, revisar estado y reconciliar antes de reintentar sin control.

## Verificación después de instalar
- Confirmar `crontab -l`, `timedatectl`, último log local, commit nuevo en Git y el reporte `control/ultimo_reporte_api_mer.json` actualizado a la fecha efectiva.
- Verificar que el reporte registra consultas **mayores que cero**, no `SKIP`; revisar `errores`, variación en conteos de Sheet, exportación, derivados y Pages.
- En caso de error, **no** activar simultáneamente el schedule GitHub; usar ejecución manual de emergencia solo tras detener cron local.

## Próxima sesión
Escalar progresivamente a varios lotes diarios, después de medir cuotas, latencia, HTTP 429, idempotencia y crecimiento de cola.

## Prueba local de capacidad (sin activar el timer)
En Ubuntu, con archivo privado `~/.config/mercadopublico/api.env` preparado, credenciales Google y ticket en el archivo privado, desde el repositorio limpio:
```bash
 git pull --ff-only origin main
 bash -n scripts/cron_api_compra_agil_ubuntu.sh
 MER_API_MAX_DETAIL=25 MER_API_DELAY_SECONDS=3 bash scripts/cron_api_compra_agil_ubuntu.sh
```
La prueba **sí escribe** en MER y **sí publica** cuando hay nuevos registros. Asegurarse de que no esté ejecutándose el ETL de las 16:00 ni el cierre y de que el estado local coincida con GitHub antes de lanzarla. Verificar reporte fresco, `consultados`, `procesos`, `ofertas`, `resultados`, `errores`, cursor, Git push y Pages. Tras validación sin 429, siguiente prueba:
```bash
 MER_API_MAX_DETAIL=50 MER_API_DELAY_SECONDS=3 bash scripts/cron_api_compra_agil_ubuntu.sh
```
No encender el timer hasta comprobar por lo menos ambas pruebas y los permisos de escritura. Después de validar, instalar y habilitar solamente bajo supervisión:
```bash
 mkdir -p ~/.config/systemd/user
 cp deploy/systemd/mercadopublico-api.{service,timer} ~/.config/systemd/user/
 systemctl --user daemon-reload
 # Ejecutar enable --now exclusivamente después de la validación real.
```
El timer propuesto llama cada hora a minuto 10, comparte el candado del MER y no se solapa con otra ejecución API local. Durante la prueba solo se procesan fechas del **mes actualmente operativo**; el retroceso histórico de meses archivados exige un procedimiento separado de conciliación y no debe escribirse directamente en históricos.

**Importante:** el script conserva reintentos cada 3 días para procesos previamente vistos; el cursor del listado es independiente y avanza únicamente si las cotizaciones de páginas completas están anotadas en estado. Una ejecución con 50 detalles no implica 50 procesos nuevos. Si la API responde 429 se detiene el lote y se conserva la cola para reintento. No se han medido aún la cuota de detalle por hora, la velocidad real y la persistencia del retraso frente al volumen total: los límites propuestos son hipótesis para probar, no capacidad acreditada.
