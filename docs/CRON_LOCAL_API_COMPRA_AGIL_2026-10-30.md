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

## Incidencia local 30/10 20:40 — archivos sin seguimiento
La prueba de 25 no llegó a consultar la API porque el runner rechazaba cualquier salida de `git status --porcelain`. La evidencia del usuario muestra exclusivamente `?? logs/`, `?? salida_operativa/` y tres scripts Python locales no versionados. Estos archivos deben preservarse; **no ejecutar `git clean`, `reset --hard` ni añadirlos al commit**. Corrección aplicada en `scripts/cron_api_compra_agil_ubuntu.sh`: bloquear solo modificaciones de archivos **versionados** (`git status --porcelain --untracked-files=no`); conservar los elementos `??` intactos. Tras `git pull --ff-only origin main`, reintentar el lote de 25. Validar que el ticket cargado en `api.env` no esté vacío; jamás mostrarlo en pantalla o en capturas. La prueba real continúa pendiente.

## Política aprobada para operación horaria — 30/10
**Esta sección prevalece sobre las antiguas pruebas de 25/50 y pausas de 3 segundos descritas anteriormente.** El usuario aprobó lotes de **hasta 100 procesos**, mínimo **10 segundos entre solicitudes HTTP** (listado y detalle). Si una solicitud devuelve HTTP 429, reintentar dos veces tras 10 segundos cada una. Ante la **tercera respuesta 429**, terminar las consultas de este lote y dejar `pausa_hasta` para una hora después en `control/cola_api_mer.json`. El siguiente disparo horario debe continuar desde el código pendiente, sin volver a descargar los ya marcados como exitosos.

La cola conserva el cursor de listado y estados por código. El script de producción escribe cada proceso aceptado en `Procesos`, `Ofertas`, `Resultados` y registra su finalización. Aunque se interrumpa la consulta número 81, el informe y estado se guardan en `finally`; el wrapper exporta los **80 completados**, envía commit de cambios al repositorio y dispara publicación de índices, analítica y GitHub Pages. **La publicación parcial es obligatoria**, no esperar a completar 100. Se añadió identificador por ejecución para no publicar un informe anterior si la corrida actual es omitida por pausa.

El timer `mercadopublico-api.timer` está diseñado para ejecución a minuto 10 de cada hora; la unidad service declara `MER_API_MAX_DETAIL=100`, `MER_API_DELAY_SECONDS=10`. **Todavía no se ha instalado ni activado el timer API en Ubuntu**, ni se han realizado escrituras reales bajo esta nueva política. No confundir validación estática de GitHub con una prueba de integración MER–publicación. El cron ETL de las 16:00 sigue separado y posee candado compartido.

**Puntos de validación productiva pendientes:** reanudación real después de HTTP 429, escritura incremental de 100, desempeño de Google Sheets, no duplicación, finalización de exportador y workflows derivados. Ante fallos de escritura o push, conservar logs y reconciliar estado; no reiniciar a ciegas. El mes de octubre está archivado; no iniciar escritura productiva hasta noviembre.

## Ejecución excepcional inmediata y reintento horario (30/10)

**Decisión aprobada:** hoy, con octubre ya archivado operativamente pero pendiente de conciliación oficial, ejecutar lote productivo de **hasta 100**, no una simulación, usando excepción temporal `MER_API_CIERRE_EXCEPCIONAL=2026-10`. La excepción exige que el período corresponda al mes calendario de Santiago y que la hoja esté `historico` con estado `cierre_operativo_pendiente_conciliacion_oficial`. **No se modifica el catálogo para reabrir octubre ni se mezclan sus registros con noviembre.** Se exportan datos públicos del período intervenido.

```bash
cd "$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia"
git pull --ff-only origin main
MER_API_CIERRE_EXCEPCIONAL=2026-10 MER_API_MAX_DETAIL=100 MER_API_DELAY_SECONDS=10 bash scripts/cron_api_compra_agil_ubuntu.sh
```

El script confirma cada registro de Sheets; actualiza `control/cola_api_mer.json` y `control/ultimo_reporte_api_mer.json` en `finally`. Si una solicitud recibe tres HTTP 429 consecutivos con 10 segundos entre reintentos, interrumpe el lote, guarda `pausa_hasta` y fecha de reintento del código fallido **60 minutos desde el tercer 429**, pero exporta y publica los registros ya exitosos, aunque sean menos de 100. El wrapper hace commit/push y dispara `publicacion-v2-post-etl.yml`; índices, analítica y Pages se verifican después.

Para automatizar reintentos cada hora, tras actualizar el repositorio instalar la unidad y el timer horario:
```bash
mkdir -p "$HOME/.config/systemd/user"
cp deploy/systemd/mercadopublico-api.{service,timer} "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now mercadopublico-api.timer
systemctl --user list-timers
```
El timer intenta ejecutar cada hora al minuto 10, pero **si aún no transcurren los 60 minutos desde el tercer 429, se omite la consulta y espera la siguiente hora**. La unidad define `MER_API_CIERRE_EXCEPCIONAL=auto`: el runner usa la hoja del mes actual archivado prematuramente y pendiente de conciliación; desde el 1 de noviembre **deja de aplicar la excepción de octubre** y vuelve automáticamente al libro operativo de noviembre. No modificar el cron ETL 16:00. La unidad comparte candados con ETL/rotación/conciliación. El instalador requiere que `api.env` y las credenciales Google permanezcan privados en Ubuntu.

**Alcance de validación:** la implementación y pruebas sintácticas en GitHub no acreditan todavía escrituras reales de 100 ni publicación parcial en producción. Verificar `consultados`, `errores`, `limite_429`, `reintentar_desde`, commit remoto, workflow de derivados y estado Pages. Anotar el resultado real; no afirmar éxito antes de ejecutarlo.
