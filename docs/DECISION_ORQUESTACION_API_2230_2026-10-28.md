# Decisión aprobada — Orquestación diaria API (Fase 2)
**Aprobación del responsable:** 28-10-2026. **Estado:** diseño aprobado, programación nocturna NO activada todavía.

## Responsabilidades
- **16:00 America/Santiago, lunes a viernes:** mantener SIN CAMBIOS el cron Ubuntu validado, encargado de fuentes históricas, Procesos, OrdenesCompra y relaciones que ya calcula.
- **17:00 o primera ventana disponible:** conservar generación y publicación habitual de catálogo, índices, perfiles y analítica, conforme al workflow vigente.
- **22:30 America/Santiago, lunes a viernes:** nueva sincronización **exclusivamente complementaria** de API ChileCompra, para campos de Ofertas y Resultados que no entrega el ETL y que no pueden derivarse internamente. Nunca reimportar históricos ni reemplazar fuentes consolidadas.
- **Tras sincronización API exitosa con cambios:** segunda publicación de solo entidades/derivados afectados. Sin cambios, ninguna nueva publicación.
- Las 22:30 son una elección operativa dentro del horario nocturno recomendado, no hora de actualización oficial garantizada por ChileCompra.

## Condiciones de seguridad
1. Utilizar códigos ya existentes en MER como universo; seleccionar únicamente los que precisen datos oficiales no derivados. Respetar período de pertenencia: el piloto `839-4-COT26` corresponde a **julio**, no octubre.
2. Deduplicar por `(codigo,id_cotizacion)` en Ofertas y `(codigo,id_cotizacion_ganadora)` en Resultados. No sobrescribir valores validados ni inferir CLP, adjudicación o identidad.
3. Conservar JSON bruto privado y hash; no subirlo a repositorio ni Pages.
4. Respetar cuotas y HTTP 429 mediante límites conservadores, backoff y checkpoints de recuperación. Nunca ejecutar consultas masivas sin establecer presupuesto.
5. Coordinar la escritura con el lock compartido del MER y no iniciar en caso de ETL inconsistente. Fallos API no deben invalidar publicación vespertina.
6. Publicar cuando termine la API correctamente, no por una hora fija; reflejar última sincronización API por separado de la fecha ETL.
7. Cierre mensual: conservar pertenencia histórica del proceso y seguir resultados pendientes sin moverlo de mes.

## Dependencias antes de habilitar 22:30
- Completar matriz campo→origen: ETL, cálculo interno o API.
- Ampliar exportación y derivados operativos para Ofertas/Resultados sin modificar ruta de Procesos/OC.
- Validar escritura automática segura, lock, checkpoints y recuperación bajo una identidad autorizada en infraestructura elegida; ChatGPT conectado no transfiere credenciales a Actions.
- Ejecutar ensayo sin consultas API en copia MER y despliegue aislado, luego activar programación bajo límites.
- Elegir un solo responsable de ejecución nocturna (GitHub Actions o cron Ubuntu); **no activar ambos**.

## Evidencia
Primer piloto de 1 proceso, 15 cotizaciones y 1 selección, escrito y re-leído en copia Sheets: `docs/PILOTO_REAL_API_COT_839-4-COT26_2026-10-28.md`.
PR en desarrollo: https://github.com/juliopez/MercadoPublico-Inteligencia/pull/1


## Regla aprobada: selección diaria de procesos para consulta API

La sincronización complementaria de las 22:30 opera con **tres grupos** y no recorre diariamente todo el histórico:

1. **Nuevos del día (PENDIENTE):** códigos incorporados o identificados durante el último ciclo ETL que requieran campos API no recuperables del ETL o de cálculos internos. Consultar solo si no existe respuesta vigente válida en caché.
2. **Fallidos anteriores (ERROR):** códigos registrados en la pestaña de fallos o registro de control con un fallo de API, transformación o escritura. Reintentar únicamente cuando venza `proximo_intento`, con presupuesto y backoff; un intento fallido no debe borrar datos ya validados.
3. **Seguimiento (EN_SEGUIMIENTO / SIN_DATOS):** códigos cuya API respondió pero todavía pueden recibir cotizaciones o una selección posterior. Consultar solo cuando alcance `proxima_revision`; una consulta HTTP exitosa por sí sola no cierra un proceso.

**Orden inicial:** nuevos del día → errores vencidos → seguimiento vencido; aplicar presupuesto máximo por ejecución y reservar capacidad para los grupos 2 y 3 a fin de evitar inanición. Deduplicar códigos *entre grupos antes de consultar*, priorizar caché antes de red, usar bloqueo compartido para escritura y checkpoint después de cada operación confirmada.

**Estados del registro de control:** `PENDIENTE`, `ERROR`, `EN_SEGUIMIENTO`, `SIN_DATOS`, `COMPLETO`. Campos mínimos: `codigo`, `periodo_origen`, `estado`, `ultimo_intento`, `ultima_consulta_exitosa`, `proximo_intento`, `proxima_revision`, `intentos`, `tipo_error`, `hash_respuesta`, `ultima_escritura_mer`. Es preferible separar seguimiento y fallos de las pestañas públicas del MER; si ya existe pestaña de fallidos, reutilizarla o migrar sin perder su historia, sin crear un duplicado operativo.

**Cierre:** marcar `COMPLETO` solo cuando se verifique que la información requerida está definitivamente resuelta conforme a reglas oficiales y a las vinculaciones internas. No considerar `seleccionado=1` equivalente a adjudicación formal; un `COMPLETO` no impide reabrir el caso si el ETL detecta un cambio oficial posterior.

**Política inicial sugerida (parámetros configurables, aún no activados):** para `ERROR`, reintentos progresivos en las siguientes noches hábiles (p. ej. 1, 2 y 4 noches) con límite de intentos y derivación a revisión; para `EN_SEGUIMIENTO`, revisión cada 2 noches hábiles durante los primeros 14 días y semanal después; para `SIN_DATOS`, comprobación más espaciada y revisión al cumplirse un umbral. Estas frecuencias deberán contrastarse con tasas observadas y límites documentados de ChileCompra antes de activarlas.

**Alcance:** solo Compra Ágil / campos de Ofertas y Resultados que el cron no obtiene ni el MER calcula. Preservar mes de origen de cada proceso incluso si su resultado llega en otro mes. Si el ETL de las 16:00 no cerró correctamente, no agregar nuevos códigos del día a la cola; registrar incidencia y procesar reintentos solo si la integridad de datos de referencia puede garantizarse.

**Publicación:** sin cambios escritos, no disparar publicación. Si cambia Ofertas/Resultados, exportar únicamente las entidades afectadas y usar los generadores de derivados existentes. Mantener log de consultas, resultados, cuotas y duración; no incluir tokens ni RUT en logs.

**Estado de la presente regla:** APROBADA COMO DISEÑO. No existe evidencia de que esta cola y sus calendarios estén implementados o activados. No modificar el cron actual hasta completar su implementación y ensayos.
