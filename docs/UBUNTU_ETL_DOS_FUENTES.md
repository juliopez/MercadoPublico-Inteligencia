# Operación Ubuntu — Licitaciones y Órdenes de compra (sin API)

**Estado:** código publicado, pendiente de prueba real y habilitación local. NO se ha activado cron ni se han cargado datos.

## Alcance
- Usa los ZIP oficiales del período vigente calculado con `America/Santiago`:
  - licitaciones `https://transparenciachc.blob.core.windows.net/lic-da/AAAA-MM.zip`
  - OC `https://transparenciachc.blob.core.windows.net/oc-da/AAAA-MM.zip`
- Nunca pide el ZIP COT. La API Compra Ágil queda para otro flujo.
- MER v2: prepara y actualiza solo `Procesos`, `OrdenesCompra` y `Proveedores`. Nunca borra filas ausentes, ni vacía `Ofertas`, `Resultados` o `VinculosCOT_OC`.
- Se bloquea si el mes no figura como `operativo` en `config/catalogo_sheets.json`. No cambia automáticamente la hoja al empezar un mes: **el nuevo archivo y catálogo deben existir antes del día 1**.
- Las claves son `codigo`, `codigo_oc` e `id_proveedor`; la misma PK no vuelve a insertarse. Los datos distintos se actualizan. Ciertas discrepancias de identidad tributaria aún deben conciliarse.

## Preparación inicial
```bash
cd ~/MercadoPublico-Inteligencia # ajustar a tu ubicación
git pull --ff-only
sudo apt install -y python3-venv util-linux
bash scripts/ubuntu_preparar_prueba.sh
.venv/bin/pip install 'gspread>=6,<7' 'google-auth>=2,<3' 'google-api-python-client>=2,<3'
bash scripts/ubuntu_etl_dos_fuentes.sh --simular
```
La simulación descarga/valida ambos ZIP y cuenta los registros, no requiere cuenta Google. Revisar `salida_operativa/etl_zip_operativo_AAAA-MM.json` y `logs/etl_dos_fuentes_*.log`.

## Credenciales para carga real
1. Configurar un proyecto en Google Cloud con Google Sheets API y Google Drive API habilitadas y una cuenta de servicio dedicada.
2. Descargar la clave JSON únicamente a Ubuntu, fuera de Git y de carpetas públicas, permisos `chmod 600`. Nunca compartir claves o credenciales por ChatGPT/GitHub.
3. Compartir `MER_2026_10_OPERATIVO` exclusivamente con el correo de la cuenta de servicio como Editor. El respaldo se hace localmente mediante Sheets API, sin copia por Drive. No compartir los cuatro históricos ni la producción antigua.
4. En la terminal local, antes de la primera ejecución validada:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/mercadopublico/servicio-google.json"
bash scripts/ubuntu_etl_dos_fuentes.sh --aplicar
```
**Importante:** `--aplicar` realiza escrituras reales en la Sheet operativa. Hacerlo únicamente después de validar la simulación, tamaño y permisos. Crea un respaldo ZIP local de las seis pestañas antes de escribir; si una escritura falla a mitad, conserva registros ya escritos y requiere reejecución/verificación. El upsert es idempotente respecto a PK, pero **no es una transacción atómica multitabla**. No lanzar ejecuciones simultáneas ni habilitar cron antes de primera prueba completa.

## Cron (propuesto, NO activado)
Usar el huso horario del equipo: comprobar `timedatectl | grep 'Time zone'`. Si difiere de Santiago, adaptar el cron a la hora local equivalente; `TZ` dentro del script solo afecta a su ejecución, no al horario al que cron lo inicia.

Tras validar **una carga completa** y confirmar credenciales estables, abrir `crontab -e` e insertar (ajustar ruta absoluta):

```cron
0 16 * * 1-6 /bin/bash /home/USUARIO/MercadoPublico-Inteligencia/scripts/ubuntu_etl_dos_fuentes.sh --aplicar
```

El export de `GOOGLE_APPLICATION_CREDENTIALS` no se transmite entre terminal interactiva y cron. Para ejecución desatendida cargarla desde un archivo local restringido, por ejemplo un wrapper bajo `~/.config/mercadopublico/`, propiedad del usuario (`chmod 700` directorio y `chmod 600` archivo); **sin guardar la clave en Git**.

La planificación a las 16:00 aplica lunes–sábado, solo si Ubuntu está encendido. No hay reintentos automáticos dentro del programa ni cierre mensual automático aún. Esto se abordará tras la prueba real.

## Evidencia requerida
- Archivo `salida_operativa/etl_zip_operativo_2026-10.json` de simulación.
- Conteos PK y esquema, revisión de suficiencia de celdas.
- Tras carga piloto: reporte con `CARGA_VERIFICADA` y comprobación independiente de las pestañas.
- Si el servidor devuelve ZIP antiguo/vacío o error de HTTP: no publicar nueva hora de éxito en el frontend. El frontend todavía no está conectado a este flujo.

## Respaldo local obligatorio — corrección por error 403 de almacenamiento

La cuenta de servicio **puede leer la Sheet y usar la API Drive**, pero `files.copy` devolvió `storageQuotaExceeded`. No se requiere habilitar facturación. Desde esta revisión, `scripts/etl_zip_dos_fuentes.py` **no utiliza la API de Drive**. En su lugar, antes de cualquier escritura lee las seis pestañas por Sheets API y crea un ZIP verificado con seis CSV, `manifiesto.json`, SHA-256 por archivo, CRC y hash global. Se guarda fuera del repositorio, en `~/.local/share/mercadopublico/respaldos/` (directorio 700, archivo ZIP 600). Si falla, la escritura queda bloqueada.

**Prueba obligatoria de solo lectura antes de aplicar:**
```bash
git pull --ff-only
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/mercadopublico/servicio-google.json"
.venv/bin/python scripts/ubuntu_verificar_respaldo.py
```

El resultado esperado es `RESPALDO LOCAL CREADO Y VERIFICADO`. Compartir solo las estadísticas impresas (sin credenciales); no borrar el respaldo. La prueba no descarga ZIP de ChileCompra ni escribe en Google Sheets.

**Limitación:** respaldo previo y validación de carga no constituyen una transacción atómica de Google Sheets; si se interrumpe la ejecución, las tablas pueden estar parcialmente actualizadas. `cron` seguirá desactivado hasta comprobar la carga inicial de punta a punta y diseñar recuperación. El ZIP local permite restauración manual controlada; **aún no está implementado un restaurador automático**.

## Ejecución programada lunes a viernes a las 16:00 (Santiago)

El script [`ubuntu_cron_etl.sh`](../scripts/ubuntu_cron_etl.sh) determina día/hora usando explícitamente `America/Santiago`. Esto permite que Ubuntu tenga otro huso horario y evita problemas de horario de verano. `cron` lo invoca a la hora en punto de cada hora, pero el ETL **solamente se ejecuta de lunes a viernes a las 16:00 hora de Santiago**.

**Verificación previa obligatoria (NO carga):**
```bash
git pull --ff-only
bash scripts/ubuntu_cron_etl.sh --verificar
```
Comprobar que aparece `VERIFICACIÓN CRON OK`. Confirma existencia de Python, archivo de credenciales y registro del mes actual; no prueba conexión en cada invocación.

**Instalación por el usuario en Ubuntu**: ejecutar `crontab -e` e incorporar una sola vez esta línea, ajustando ruta absoluta:
```cron
0 * * * * /bin/bash "/home/julio/Julio Lopez/chilecompra/MercadoPublico-Inteligencia/scripts/ubuntu_cron_etl.sh"
```

**No colocar `GOOGLE_APPLICATION_CREDENTIALS` ni credenciales JSON en el crontab.** El wrapper lee el archivo local `$HOME/.config/mercadopublico/servicio-google.json` protegido con `chmod 600`. Se mantiene el bloqueo `flock` del ejecutor para evitar ejecuciones simultáneas. La ejecución deja logs en `logs/etl_dos_fuentes_*.log`; el JSON `salida_operativa/etl_zip_operativo_AAAA-MM.json` se sobrescribe solo tras una ejecución finalizada. La ejecución depende de que Ubuntu esté encendido a la hora pertinente; no recupera días perdidos.

**Cambio de mes**: las URL ya se generan con el mes vigente de Santiago y admiten 28, 29, 30 o 31 días. **Aún NO existe aprovisionamiento automático de una nueva Google Sheets.** Antes del primer día de cada mes, el usuario debe crear `MER_AAAA_MM_OPERATIVO`, confirmar sus seis pestañas, compartirla con la cuenta de servicio y registrar su identificador como `operativo` en `config/catalogo_sheets.json`. De no cumplirse, el wrapper detiene la carga sin tocar la hoja anterior. El archivo saliente se preserva para cierre diferido y conciliación, **sin moverlo ni renombrarlo automáticamente**. Preparar noviembre antes del 1/11/2026.

**No confundir programación con ejecución verificada**: el wrapper y este manual ya están publicados, pero el usuario debe instalar cron en Ubuntu y confirmar `crontab -l` y la primera ejecución programada. No se modifica el frontend ni el flujo API de Compra Ágil.

## Noviembre 2026 preaprovisionado — 20/10/2026

[MER_2026_11_OPERATIVO](https://docs.google.com/spreadsheets/d/1faLUhyB13Qty7dSNqbRHLCmpq-cxgW8bIOgPN0KCWnE/edit) ya existe, con seis tablas, está ubicado en `02_Operativo_MER`, compartido con la cuenta de servicio y registrado en `config/catalogo_sheets.json`. El ETL ya calcula período/URL al ejecutar, por lo que en noviembre seleccionará ese archivo. Octubre no se cierra por cambiar el reloj.

**Importante:** la creación de futuras hojas **no es autónoma** desde la cuenta de servicio por `storageQuotaExceeded`. Antes de diciembre se necesita crear/compartir/catalogar `MER_2026_12_OPERATIVO` desde la cuenta propietaria o definir OAuth de usuario autorizado; hasta entonces el wrapper bloquea la escritura del mes no provisionado. Tampoco está automatizada la conciliación de Compra Ágil ni el cierre histórico. Para mantener actualizado el código local, ejecutar `git pull --ff-only` en Ubuntu antes de la transición, ya que cron no actualiza GitHub automáticamente.
