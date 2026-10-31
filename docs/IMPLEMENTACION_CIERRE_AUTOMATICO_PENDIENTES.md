# Cierre histórico autónomo — requerimiento obligatorio y estado real

**Decisión del usuario:** las dos etapas finales del día 10 hábil (**aplicación a Google Sheets y validación final**) deben ser automáticas. No pedir aprobaciones humanas recurrentes.

## Avance de implementación
- Nuevo módulo `scripts/cierre_mensual_automatico.py`: controla ventana habilitada, mes archivado/mes operativo, descarga y validación de tres fuentes, diagnóstico, política de precedencia, motor existente de carga con respaldo, lectura posterior de seis tablas y persistencia de constancias. **No está instalado ni invocado todavía por timer**, no se ha probado con Google Sheets productivo.
- `scripts/exportar_operativo_sqlite.py` y `scripts/conciliar_cierre_mensual.py`: admiten el mes anterior ya rotado a histórico, conservando las restricciones del período.
- `scripts/diagnosticar_cierre_integrado.py`: corregida escritura de JSON de política.
- El módulo **no declara cierre definitivo** tras cargar: marca `CARGA_HISTORICA_VERIFICADA_PENDIENTE_PUBLICACION`.

## Bloqueos técnicos que impiden declarar implementación completa
1. Falta encadenar con seguridad la **exportación del período histórico**, regeneración de índices/analítica del mes cerrado, verificación del despliegue Pages y emisión del estado terminal `CONCILIACION_HISTORICA_VERIFICADA`.
2. Los workflows de publicación existentes están condicionados al mes calendario operativo; adaptarlos directamente pondría en riesgo la línea base protegida de las 16:00. Diseñar ruta independiente para republicar histórico.
3. La operación real de Google Sheets debe contar con pruebas de integración: respaldo válido, política de precedencia, reanudación sin duplicados ante caídas y resultados verificables de las seis tablas.
4. La preparación del cierre puede encontrarse con fuentes oficiales todavía incompletas o no disponibles; el diseño debe evitar consolidar un mes con datos incompletos y no etiquetar un error como cierre.
5. No cambiar el servicio/timer instalado hasta que toda la cadena funcione y se compruebe; instalar código no significa activarlo.

## Regla operativa
El objetivo es **cierre desatendido**, pero ante fallo de integridad debe quedar bloqueado con alarma y reintento seguro, no manipular datos a ciegas. El cron 16:00 y API 400 permanecen protegidos. Cualquier actualización posterior debe registrar evidencia de pruebas y hora de instalación del timer. No afirmar automatización completa antes de verificarlas.

## Avance posterior: cadena completa desarrollada en GitHub

Se implementaron `scripts/exportar_mer_historico_conciliado_v2.py` (exportador exclusivo del mes anterior), `scripts/publicar_cierre_historico_v2.py` (exportación de cuatro entidades, regeneración de índices y perfiles, push, verificación de workflow Pages y comprobación HTTP del catálogo y analítica públicos) y el enlace desde `scripts/cierre_mensual_automatico.py`. Solo después de confirmar publicación se actualiza el estado del catálogo privado y se guarda `CONCILIACION_HISTORICA_VERIFICADA` localmente; las fallas conservan el estado recuperable. El servicio ya apunta a la cadena completa mediante `scripts/ubuntu_preparar_conciliacion_persistente.sh`. El timer original de las 10:00 y arranque sigue sin cambiar.

**Instalación en Ubuntu pendiente de ejecución verificable**: el repositorio no instala ni sustituye unidades systemd locales por sí solo. Se incluyó `scripts/instalar_cierre_mensual_automatico_ubuntu.sh` como instalador único con comprobaciones. En Ubuntu ejecutar desde el repositorio actualizado:
```bash
git pull --ff-only origin main
bash scripts/instalar_cierre_mensual_automatico_ubuntu.sh
systemctl --user list-timers --all | grep mercadopublico-conciliacion
```
Verificar `journalctl --user -u mercadopublico-conciliacion.service -n 100 --no-pager` después del primer ciclo. No confundir unidad instalada con carga/conciliación mensual ejecutada. El día 10/11/2026 es el primer ciclo oficial elegible para octubre.

**Verificación CI**: `.github/workflows/validar-cierre-historico-automatico.yml` valida sintaxis y conexión estructural sin Google Sheets. Un resultado `success` de CI **no equivale** a confirmar escritura productiva, recuperación tras fallas ni cierre real. El alcance automático solo procede con ZIP oficiales íntegros; ante problema se bloquea y reintenta, sin falsos cierres.

**Líneas base protegidas**: ninguna modificación al cron 16:00 ni al runner manual API 400. La publicación histórica usa módulos nuevos, sin debilitar el exportador diario.
