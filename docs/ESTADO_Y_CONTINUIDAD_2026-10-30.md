# Estado operativo y continuidad — 30 de octubre de 2026

**Este es el punto de entrada vigente**. Las guías y planes fechados antes del 30/10 son antecedentes técnicos, no instrucciones prioritarias si contradicen esta página.

## Alcance y estados comprobados

| Componente | Estado al 30/10 | Evidencia o siguiente control |
|---|---|---|
| Cron Ubuntu 16:00, licitaciones/OC y conciliación documental COT–OC | **Operativo (cadena de publicación verificada)** | Exportación 16:02 Chile, [publicación derivada](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41111950651) y [supervisor sin errores](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41112286441). Los logs del cron local deben revisarse localmente si se necesita su detalle |
| MER octubre | **Operativo al momento de la verificación** | Hoja original preservada; cierre definitivo oficial pendiente |
| MER noviembre | **Preparado y verificado en Drive** | `MER_2026_11_OPERATIVO` existe en carpeta operativa, seis pestañas con cabeceras correctas, filas de datos vacías y permiso de escritura declarado para la cuenta de servicio; sin prueba de escritura real desde Ubuntu |
| Exportación del siguiente mes público | **Implementada en código, pendiente de primer ciclo** | `scripts/exportar_mer_operativo_v2.py` abre período nuevo en catálogo público tras ETL validado |
| Rotación último día hábil, 19:00 | **Implementada; timer preparado; NO instalada/ejecutada en Ubuntu** | `scripts/rotar_mes_operativo.py`, `scripts/ubuntu_rotacion_mensual.sh`, unidades `deploy/systemd/mercadopublico-rotacion.*`. El movimiento real de archivos y permisos del propietario siguen sin prueba |
| Preparación conciliación del día 10 hábil | **Implementada; timer preparado; NO instalado/ejecutado en Ubuntu** | `scripts/verificar_ventana_conciliacion.py`, `scripts/ubuntu_preparar_conciliacion_persistente.sh`, `deploy/systemd/mercadopublico-conciliacion.*`; tres ZIP del mes previo; no escribe en Sheets |
| Conciliación histórica definitiva | **Supervisada, no automatizada** | Carga, auditoría, conciliación, aprobación y confirmación; [runbook octubre](RUNBOOK_CIERRE_2026_10.md) requiere adaptación de indicaciones de traslado a la rotación previa |
| API ChileCompra Compra Ágil | **Código local preparado, prueba real local y activación pendientes** | `scripts/mer_api_incremental_10.py` y `scripts/cron_api_compra_agil_ubuntu.sh`; máximo diez detalles/ejecución; **schedule de GitHub Actions desactivado**, queda despacho manual de contingencia |

## Decisiones operativas

1. **Un mes vigente para cargas nuevas:** el ETL de las 16:00 resuelve el período con `America/Santiago`, sin reprogramarlo ni reescribir históricos.
2. **Último día hábil:** rotación operativa separada del cierre histórico definitivo; archivo anterior se resguarda conservando ID, y se crea o reutiliza un archivo operativo del mes siguiente. Esta rotación **aún no se ha probado en Drive bajo Ubuntu**.
3. **Día 10 o hábil posterior:** al encender Ubuntu debe poder prepararse la conciliación del mes anterior. Se obtienen los tres ZIP oficiales (licitaciones, COT y OC), se valida su integridad y se construye paquete de revisión; **no equivale a aplicar la reconciliación final**.
4. **No simultaneidad:** cron ETL, rotación y preparación de cierre utilizan el candado compartido `logs/.mer_escritura_compartida.lock`. API local queda para etapa posterior.
5. **Calendario:** feriados nacionales de Chile configurados solo para **2026**; verificar y agregar 2027 y posteriores, así como los feriados regionales pertinentes, antes de esas fechas. En años no verificados se bloquea.
6. **Sin secretos en Git:** credenciales permanecen en Ubuntu, nunca en documentación, commits o logs.
7. **No confundir estados:** código implementado ≠ prueba CI ≠ instalación local ≠ movimiento Drive confirmado ≠ publicación efectiva.

## Trabajo inmediato del usuario en Ubuntu

El usuario actualizará su clon mediante `git pull --ff-only origin main` e instalará los dos temporizadores locales desde [la guía de instalación](INSTALACION_ROTACION_CONCILIACION_2026-10-30.md). Debe comprobar `systemctl --user list-timers`, `journalctl`, credenciales locales y permisos de Drive antes de declarar operación automatizada. El cron vigente de las 16:00 **no debe modificarse**.

**Precaución del primer mes:** el viernes 30/10 fue el último día hábil de octubre. La rotación solo se ejecutará con el temporizador instalado dentro de su ventana y después de ETL verificado; si la ventana pasó, debe revisarse el estado real de Drive y la recuperación antes de ejecutar manualmente. No asegurar retrospectivamente que octubre se movió.

## Próxima etapa después de comprobar instalación

Probar **API Compra Ágil desde Ubuntu**, inicialmente diez procesos, sin schedule GitHub simultáneo: credenciales, llamadas reales, respuestas HTTP 429, Google Sheets, cola/reintentos, exportación y publicación. Luego evaluar lotes mayores y horarios distribuidos.

## Guías de referencia

- [Instalación de rotación y conciliación](INSTALACION_ROTACION_CONCILIACION_2026-10-30.md)
- [Preparación del cambio a noviembre y verificación Drive](APERTURA_NOVIEMBRE_2026_PREPARACION_30-10.md)
- [Conciliación recuperable y límites del automatismo](CONCILIACION_DIA_HABIL_RECUPERACION_2026-10-30.md)
- [Runbook de conciliación oficial de octubre](RUNBOOK_CIERRE_2026_10.md)
- [API local, instrucciones sin activar](CRON_LOCAL_API_COMPRA_AGIL_2026-10-30.md)
- [Índice y antecedentes históricos](INDICE_DOCUMENTACION.md)

## Texto para continuar en otro chat

> Continúa Observatorio Mercado Público desde `docs/ESTADO_Y_CONTINUIDAD_2026-10-30.md`. El cron Ubuntu 16:00 fue validado; rotación y preparación recuperable de conciliación quedaron codificadas pero pendientes de instalación local y prueba Drive; noviembre existe con seis tablas verificadas. Primero confirma instalación y logs de los timers y el estado real de Drive, sin volver a desarrollar la rotación. Luego inicia prueba de API Compra Ágil desde Ubuntu con diez procesos, sin activar el schedule GitHub ni tocar el cron de las 16:00. Mantén README, índice, decisiones y procedimientos sincronizados, diferenciando implementado, probado e instalado.

## Incidencia de rotación detectada el 30/10 a las 20:18 Chile
- Ubuntu ejecutó `python scripts/rotar_mes_operativo.py` en modo de comprobación, **sin `--aplicar`**.
- Validó acceso a los datos de octubre, pero la API Drive invocada con cuenta de servicio devolvió `parents=[]` para el archivo `MER_2026_10_OPERATIVO`. El script detuvo la operación en `BLOQUEO DRIVE ORIGEN`; **no ocurrió traslado ni actualización de catálogo**.
- Verificación separada mediante Drive de la cuenta propietaria confirma que la hoja sí pertenece a la carpeta operativa configurada. La discrepancia es de visibilidad/permisos entre identidades, **no demuestra que el archivo esté fuera de la carpeta**.
- **Bloqueo operativo**: no ejecutar `--aplicar` ni eliminar el control `parents`. Confirmar si la cuenta de servicio tiene acceso real a ambas carpetas y capacidad para mover el archivo; el permiso de edición sobre la hoja no implica permiso para moverla. Si no lo tiene, requerir movimiento por cuenta propietaria o ajustar permisos con seguridad, y adaptar la verificación sin comprometer integridad.
- Los temporizadores `mercadopublico-rotacion.timer` y `mercadopublico-conciliacion.timer` figuran `enabled, active (waiting)` en Ubuntu; esto **no acredita que sus tareas hayan funcionado**.
- Para evitar falsas certezas, revisar logs y resultado de una prueba no destructiva antes de considerar cerrado octubre o comenzar API local.

## Diagnóstico definitivo de permisos Drive — 30/10, 20:19 Chile

**Evidencia aportada desde Ubuntu:** `bash scripts/ubuntu_cierre_supervisado.sh verificar-acceso` terminó con **código 1**, porque la API Drive respondió `HTTP 404 File not found` para la **carpeta operativa** configurada (`1m3feqWXUNtur6v17qvhZ9bQrB38-ruVS`).

Esto explica el fallo anterior: la consulta del archivo octubre con la cuenta de servicio devolvió `parents=[]`. **La cuenta de servicio tiene acceso a la hoja, pero no acceso suficiente a sus carpetas padre por la API Drive.** La cuenta propietaria sí confirmó que ambas hojas están en la carpeta operativa correcta. No hay evidencia de que se hayan perdido archivos o que su ubicación sea incorrecta.

**NO repetir:** `rotar_mes_operativo.py` en simulación, `ubuntu_cierre_supervisado.sh verificar-acceso`, ni múltiples `git pull` para diagnosticar el mismo HTTP 404; la causa está identificada. Ninguno de esos comandos solucionará permisos de carpeta.

**Resolución estructural, una sola vez:** la persona propietaria debe conceder permisos adecuados a la identidad de servicio sobre **las carpetas** `02_Operativo_MER` y `01_Historicos_MER`, no solamente sobre las hojas, y comprobar si Google permite mover entre ambas con esa identidad (la propiedad del documento puede imponer restricciones adicionales). Si esa ruta no fuera viable, diseñar una rotación por la identidad propietaria con autorización OAuth, no saltarse el chequeo `parents` ni suponer que permiso `writer` de Sheets autoriza movimientos. Mantener inalterado el cron 16:00 y el destino de noviembre ya existente.

**Próxima acción, sin bucle:** corregir permisos de las dos carpetas en Drive con la cuenta propietaria, o adoptar explícitamente la vía OAuth de propietario; después realizar **una sola** prueba de acceso y, si es positiva, una prueba controlada del cierre. Hasta entonces rotación mensual = **BLOQUEADA**, no operativa. El timer habilitado no demuestra traslado correcto.

**Control preventivo:** considerar pausar temporalmente el timer de rotación mientras permanezca el bloqueo, evitando intentos automáticos fallidos. La conciliación sigue separada y octubre permanece íntegro.

## Causa corroborada por metadatos del propietario — 30/10, 20:20 Chile
La lectura directa de metadatos de las carpetas con la cuenta propietaria confirmó:
- `02_Operativo_MER` ID `1m3feqWXUNtur6v17qvhZ9bQrB38-ruVS`: **único permiso explícito: propietario**, carpeta no compartida.
- `01_Historicos_MER` ID `1YC-1MT1QCnAvpKgDACCH-NKnV9caIFyW`: **único permiso explícito: propietario**, carpeta no compartida.
- Cuenta de servicio que ya tiene acceso directo de edición a las hojas: `observatorio-mercadopublico@mercadopublico-inteligencia.iam.gserviceaccount.com`.

**Causa raíz confirmada:** carpetas Drive sin permisos para la cuenta de servicio; su consulta de carpeta devuelve 404 y las hojas devuelven `parents=[]`. La solución es compartir **ambas carpetas** con esa cuenta como **Editor** desde la interfaz de Drive de la persona propietaria. La integración conectada permite consultar metadatos, pero no concede actualmente permisos a carpetas (su acción de compartir admite archivos, no URLs de carpetas). No simular que se corrigió el acceso.

**Después de compartir**, realizar una única verificación de acceso con la misma credencial local en Ubuntu, validar que la cuenta puede trasladar archivos entre estas carpetas y solo entonces ejecutar la rotación con respaldo y evidencia de ETL. Google puede restringir movimientos entre propietarios o carpetas incluso a editores; si ocurre, conservar el bloqueo y ejecutar el traslado con credenciales OAuth de propietario. **No desactivar el control de padres ni intentar más veces sin cambiar permisos**.
