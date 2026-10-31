# REGISTRO MAESTRO — Cuatro procesos y política de no modificación

> **REGLA PRIORITARIA DEL OBSERVATORIO:** No modificar por iniciativa propia los cuatro procesos inventariados, sus horarios, ejecutores, temporizadores, workflows, esquemas, contratos de datos, locks o mecanismos de publicación para desarrollar funciones ajenas. Cualquier cambio necesario exige autorización expresa del responsable, análisis de impacto entre procesos, respaldo, pruebas de regresión y reversión documentada. **Una falla no autoriza a reescribir flujos validados.**

## Alcance y nivel real de validación

| Proceso | Documento de referencia | Estado probado | Regla |
|---|---|---|---|
| **1 — ETL diario de las 16:00** | [Línea base protegida del cron 16:00](LINEA_BASE_PROTEGIDA_CRON_1600.md) | Cadena Ubuntu → Sheets → GitHub → Pages validada; operación productiva | **CONGELADO**: no modificar |
| **2 — API Compra Ágil, lote 400** | [Línea base validada API 400](LINEA_BASE_VALIDADA_API_COMPRA_AGIL_400.md) | Una ejecución manual productiva 400/400, persistencia y publicación | **CONGELADA la ejecución manual validada**; programación nocturna aún incompleta |
| **3 — Rotación mensual** | [Inventario proceso 3](INVENTARIO_PROCESO_3_CAMBIO_MES.md) | Rotación octubre → noviembre ejecutada y corroborada; timer instalado | **PRESERVAR implementación y horario**; futura ejecución desatendida aún por verificar |
| **4 — Consolidación del día 10 hábil** | [Inventario proceso 4](INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md) | Código integrado, timer habilitado y activo; primera carga oficial y cierre completo aún no validados | **PROTEGER arquitectura y componentes**, permitir únicamente correcciones justificadas y expresamente autorizadas para completar validación |

## Inventario de disparadores y fronteras

- **Proceso 1:** cron local Ubuntu lunes–viernes a las **16:00 America/Santiago**; cadena de importación, conciliación documental y publicación. No tocar.
- **Proceso 2:** lote API **manual**, capacidad comprobada hasta 400, sin temporizador nocturno aprobado. No confundir con la configuración horaria antigua de la unidad API.
- **Proceso 3:** `mercadopublico-rotacion.timer`, evaluación lunes–viernes **19:00** y ejecución efectiva únicamente cuando corresponde por calendario Chile.
- **Proceso 4:** `mercadopublico-conciliacion.timer`, evaluación diaria **10:00** y al arrancar Ubuntu; operación real solo día 10 o siguiente hábil y en reintentos pendientes.

**Dependencias compartidas que exigen análisis de impacto:** `config/catalogo_sheets.json`, esquema MER de seis tablas, Google Sheets/Drive, bloqueo `logs/.mer_escritura_compartida.lock`, publicación V2, generadores analíticos, workflows GitHub y GitHub Pages. La coexistencia horaria de los procesos 4 y 1 **aún no se ha validado bajo una consolidación de seis horas**; no declarar ausencia de riesgo. Los bloqueos evitan escrituras concurrentes, pero pueden ocasionar omisión de una ejecución si no existe reintento.

## Procedimiento de excepción
Antes de modificar cualquier proceso protegido:
1. Identificar proceso, archivo exacto y motivo comprobable.
2. Registrar dependencias y posible afectación sobre los otros tres.
3. Obtener autorización expresa para la modificación; no inferirla de una aprobación genérica de otro trabajo.
4. Preparar respaldo, pruebas de regresión y procedimiento de reversión.
5. Verificar resultado técnico y operativo, diferenciando `implementado`, `instalado`, `ejecutado` y `validado`.
6. Registrar commit, fecha, pruebas, evidencia y nuevo estado en documentación.

**No eliminar componentes, cancelar timers ni cambiar ventanas por conveniencia durante auditorías o refactorizaciones.** La línea base del proceso 1 y la ejecución manual comprobada del proceso 2 prevalecen frente a nuevas automatizaciones.

## Regla de continuidad
En todo trabajo futuro de este repositorio, empezar por este registro y consultar el inventario del proceso afectado. **Documentar no significa ejecutar cambios**; proteger no significa afirmar validaciones aún pendientes. El proceso 4 requiere una primera ejecución productiva verificada antes de declararse completamente validado.
