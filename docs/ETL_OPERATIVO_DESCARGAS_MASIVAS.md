# ETL del mes en curso — Descargas masivas ChileCompra (diseño y etapa de simulación)

Estado: **implementación inicial de descarga y simulación, NO desplegada** (20/10/2026).

## Alcance
- Solo el período calendario corriente según `America/Santiago`.
- Fuente: tres URL parametrizadas de [config/fuentes_descarga_mensual.json](../config/fuentes_descarga_mensual.json).
- Destino: únicamente la Google Sheets marcada como `operativo` en [config/catalogo_sheets.json](../config/catalogo_sheets.json).
- Ninguna lectura ni escritura de históricos por el ETL diario; no usar API ChileCompra.
- Reutilizar `scripts/importador_historicos_v2.py` para producir seis CSV MER v2.
- **No escribir aún:** `scripts/simular_mes_operativo.py` valida las tres descargas, integridad ZIP (CRC), genera seis CSV y reporte de simulación. El modo `--comparar-sheets` solo lee la hoja para calcular nuevos/cambiados/iguales. No ejecuta un upsert, no sincroniza frontend.

## Ejecución de prueba (Python 3.9+)
```bash
python scripts/simular_mes_operativo.py --solo-local --salida ./salida_operativa
```
Opcional, con credenciales Google configuradas y `gspread` instalado:
```bash
python scripts/simular_mes_operativo.py --comparar-sheets --salida ./salida_operativa
```
Antes de ejecutar: verificar que el mes en curso está registrado como **operativo** en el catálogo y descargar bajo conexión de red autorizada.

## Reglas para permitir escritura futura
1. Descargar los tres ZIP a un staging; confirmar que son ZIP con CSV, CRC válido y que corresponden al período en curso; guardar hash/tamaño/timestamp por fuente.
2. Preparar MER v2; comparar PK únicas de cada tabla y validar integridad referencial. **Conservar las filas ausentes del corte** hasta que una política explícita defina su tratamiento.
3. Calcular INSERT para PK nuevas, UPDATE para PK existentes con contenido distinto, NOOP si no cambian. No ejecutar múltiples escritores simultáneos.
4. No utilizar el cargador histórico actual como incremental: solo añade filas y deja las existentes sin cambios.
5. La PK sintética de Ofertas utiliza `codigo + rut + monto + detalle + seleccionado`; **monto, detalle y seleccionado pueden cambiar**: riesgo de PK variable. Imprescindible estabilizarla o definir reconciliación de ofertas antes de activar escrituras.
6. Antes de publicar resultados, controlar tamaño Google Sheets (límite 10M celdas), respaldos y validación post-carga. Rechazar ejecuciones parciales; mantener última publicación válida.
7. Publicar ambas marcas temporales: momento de lectura de cada fuente (si se puede obtener del proveedor) y fin de la última sincronización íntegra. Los textos del frontend deben informar desfase posible respecto al portal.
8. Programación prevista: 16:00 Santiago, reintentos 16:30/17:00. **No está programada en GitHub Actions ni activada**.

## Cambio de mes
- Desde las 00:00 del día 1 en Santiago, seleccionar un nuevo archivo `MER_AAAA_MM_OPERATIVO` y tres ZIP del nuevo período, **solo si ya existe la nueva hoja y está catalogada**. El script bloquea expresamente períodos diferentes del calendario corriente.
- Preservar el mes saliente para cierre diferido y conciliación, sujeto a fuentes válidas desde el día 3. La rutina diaria del mes actual no tiene permiso para escribir en el anterior.
- El cambio a mes histórico y la publicación automática se implementarán en tareas posteriores, no en esta simulación.

## Evidencias y pendientes
- Publicados el código de simulación y esta especificación.
- **No se ha podido verificar mediante ejecución real** HTTP/CRC/tiempos/tamaño de las tres descargas en esta fase. Tampoco se han ejecutado pruebas con Sheets.
- Próxima aprobación técnica requerida: ensayo real de descarga+simulación, contraste de PK sintéticas entre dos versiones y diseño de upsert seguro.

## Prueba reproducible en Ubuntu (sin cron ni credenciales)

Requisitos: Ubuntu con `git`, `python3 >=3.9`, paquete del sistema `python3-venv`, `flock` (util-linux), red para descargar ZIP grandes y espacio temporal local. Ejecutar:

```bash
# Primera vez, en una carpeta de trabajo elegida por el usuario:
git clone https://github.com/juliopez/MercadoPublico-Inteligencia.git
cd MercadoPublico-Inteligencia
bash scripts/ubuntu_preparar_prueba.sh
bash scripts/ubuntu_probar_descargas.sh
```

Si el repositorio ya existe: entrar a su directorio, `git pull --ff-only` y ejecutar los dos scripts. Si `python3 -m venv` informa falta de `ensurepip`, instalar `python3-venv` con APT; no subir credenciales al repositorio.

La segunda instrucción descarga y valida los ZIP oficiales del mes local en Santiago y ejecuta la conversión MER v2. Resultados: `salida_operativa/simulacion_AAAA-MM.json`, `salida_operativa/preparado_AAAA-MM/informe.json` y `logs/prueba_descargas_*.log`. Si falla, el código de salida es no-cero y el log conserva el mensaje. Archivo de bloqueo `logs/.prueba_etl.lock` impide dos ejecuciones simultáneas. La primera ejecución puede tardar y consumir gigabytes temporales según el tamaño de los ZIP. **No programar cron ni activar carga en esta fase.**

El simulador completo todavía requiere validación empírica; si los tres ZIP descargan pero el parser rechaza un CSV, conservar el log para corregir la compatibilidad. El futuro servicio tendrá que implementar reintentos, autenticación Google, escritura incremental y cierre mensual por separado.
