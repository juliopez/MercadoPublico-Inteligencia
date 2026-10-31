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
