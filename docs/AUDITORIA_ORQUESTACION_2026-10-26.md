# Auditoría de orquestación — lunes 26 de octubre de 2026

## Alcance y evidencias
Verificación del cron integrado Ubuntu 16:00 (hora Santiago), extracción y actualización del MER, conciliación documental, exportación pública, derivados de GitHub Actions y despliegue V2. No se repitieron descargas ni escrituras en Google Sheets durante esta recuperación.

## Ubuntu (evidencia de terminal del operador)
- Crontab: `0 * * * * /bin/bash ".../scripts/ubuntu_cron_integrado.sh" --cron`. El script aplica internamente guardia de lunes a viernes, hora 16.
- Logs `arranque_integrado_20261026_160001.log` y `orquestador_integrado_20261026_160001.log`: inicio 16:00:01; finalización `ORQUESTADOR OK` 16:05:52 Chile.
- `estado_sincronizacion.json`: ejecución 16:03:28 Chile, estado EXITOSA, código 0. Cambios informados: Procesos 298 nuevos y 131 modificados; OC 8599 nuevas y 7923 modificadas; Proveedores 775 nuevos.
- `estado_conciliacion.json`: `CONCILIACION_VERIFICADA` y motivo conciliación y lectura posterior verificadas.
- Publicador: `PUBLICACION_V2_OK_O_SIN_CAMBIOS`. Commit `29f02ea` a las 16:05:47 Chile. Esta evidencia certifica el estado informado por el ETL local, no una inspección independiente de cada fila de Sheets.

## GitHub y corrección
- Catálogo publicado el 26/10 a las 16:05:35 Chile: octubre 2619 procesos y 125133 OC, Ofertas y Resultados 0.
- El flujo `preview-frontend-v2.yml` de las 16:05 completó despliegue exitoso, pero las analíticas seguían con 2321 procesos y 116534 OC. Inconsistencia detectada.
- El workflow de derivados de las 17:00 no figuraba ejecutado el 26/10, ni el de supervisión de las 18:12, en los runs consultados. Causa de ausencia del schedule no demostrada.
- Corrección mínima `c2b25a4`: `publicacion-v2-post-etl.yml` se ejecuta además por `push` del catálogo público (y del propio workflow), manteniendo `schedule` como respaldo. No se cambió ETL ni MER.
- Recuperación Actions run `40418233121` terminó `success`, incluyendo generación, validación y publicación de derivados. Commit de derivados `f5898161`.
- Analítica del repositorio comprobada después: octubre Procesos=2619, OC=125133. Despliegue Pages posterior: run `40418302462` (verificar estado final por separado).
- La API Compra Ágil no se intervino.

## Pendientes de certificación
- Confirmar fin del despliegue `40418302462` y consultar archivos servidos por GitHub Pages para diferenciar repositorio de publicación HTTP real.
- El workflow de supervisión a las 18:12 no registró corrida del 26/10; investigar estado de disparadores programados y monitoreo de ausencia de ejecución, sin declarar resuelto el problema del scheduler.
- El informe local no incluye prueba externa independiente del contenido de Sheets; si se requiere auditoría exhaustiva, hacer contraste de claves/filas, sin reejecutar cargas.

## Protección
No se repitieron ETL ni cargas históricas, no se modificaron las seis tablas MER, no se publicaron credenciales o logs privados, y no se activaron cierres mensuales. 

## Seguimiento y supervisión (segunda intervención)
- Despliegue Pages de recuperación, run `40418302462`: **success** en `Desplegar preview v2 manteniendo raíz v1`. Eso acredita despliegue en GitHub Pages; la respuesta HTTP del JSON publicado aún no fue comprobable independientemente desde este entorno.
- Ausencia de `schedule` del supervisor el 26/10: confirmado en los últimos runs. Causa exacta del disparador no demostrada, por lo que no se presenta como solucionado.
- Cambio `c9474802`: workflow `verificar-publicacion-diaria-v2.yml` escucha adicionalmente `workflow_run` completado de `Publicacion V2 posterior al ETL Ubuntu`; conserva `schedule` y `workflow_dispatch`. La guardia de hora 18:00 rige solo para `schedule`, de manera que el nuevo evento sí ejecuta los controles tras publicar derivados. Un workflow de origen fallido no inicia esta comprobación por la condición del job; sigue visible como fallo en Actions.
- Limitación persistente: si ni Ubuntu publica ni GitHub ejecuta el cron del supervisor, un sistema puramente activado por estos eventos no puede detectar su propia ausencia. Se recomienda monitor externo independiente para alerta de silencio y verificar los próximos runs automáticos antes de certificar autonomía integral.
- No se activaron ETL, escrituras en Sheets ni cierres mensuales.
