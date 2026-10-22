# Plan de continuidad — cron diario de las 16:00 (Santiago)

**Cierre de jornada: 21–22 de octubre de 2026. Estado: plan de mejora, NO implementado en cron.**

## Línea base protegida

- La operación vigente ejecuta `scripts/ubuntu_cron_etl.sh`, `scripts/ubuntu_etl_dos_fuentes.sh` y el ETL de **licitaciones y órdenes de compra** mediante ZIP oficiales; no asimilarla al importador histórico, al cierre mensual ni al enriquecimiento COT–OC.
- Horario lógico: lunes a viernes a las **16:00, America/Santiago**, disparado por cron horario del equipo. Requiere Ubuntu encendido, credenciales locales y libro del mes aprovisionado. Verificar la instalación y el último éxito desde `crontab -l`, `salida_operativa/estado_sincronizacion.json` y los logs; la documentación anterior contenía estados de instalación distintos, **no afirmar que se ejecuta sin evidencia local**.
- No modificar V1, ZIP originales, MER histórico, `config/catalogo_sheets.json` ni los flujos operativos antes de respaldo, evaluación de impacto y autorización. Mantener bloqueo compartido de escritura e idempotencia por PK.

## Hallazgos reutilizables de la jornada

1. **Fuente estructurada COT:** `CodigoCotizacion` + `CodigoOC` de los ZIP de Compra Ágil aportaron 240.649 pares explícitos presentes en MER junio–septiembre; no reinsertarlos.
2. **Fuente descriptiva OC:** el campo original `Descripcion/Obervaciones` de los ZIP OC contiene referencias de Compra Ágil que NO se conservan en el esquema público reducido. En una carga puntual supervisada se insertaron y verificaron **1.411** vínculos nuevos (20, 44, 1.222, 125 por mes) y se separaron **54** casos para revisión. No confundir extracción validada con inferencia estadística.
3. **Conciliación multientidad:** el motor de agosto cruza Procesos, Ofertas seleccionadas, Resultados y OC entre períodos; los candidatos por organismo/proveedor no prueban vínculo. Junio, julio y septiembre tienen script/workflow parametrizados, pero la ejecución y los conteos aún exigen evidencia verificable.
4. **Permisos y reversibilidad:** la cuenta de servicio histórica estaba como lector (error 403), posteriormente autorizada como editor; previo a escribir, verificar capacidad real por destino, candado y respaldo. Un error parcial no autoriza reiniciar inserciones sin reconciliar PK.
5. **Publicación V2:** JSON documentales y los índices públicos se consultan desde GitHub Pages; el último registro `vinculos-oc-verificados.json` tenía **1.412** entradas (incluido el caso inicial). Mejoras de UI permiten separación por certeza y búsqueda transversal, pero publicación en `main` NO equivale a CI, despliegue y prueba visual completos.
6. **Seguimiento de cron:** `salida_operativa/estado_sincronizacion.json` y `historial_sincronizacion.jsonl` registran último éxito y fallos; no reemplazar esos registros ni alterar su semántica. Una ejecución diaria no debe declararse actualización de Compra Ágil si solo procesa licitaciones y OC.

## Diseño propuesto (NO activado)

**Etapa A, auditoría sin escritura.** Observar `crontab -l`, wrapper, ETL, locks, logs, última sincronización verificada, permisos y controles existentes. Trazar mapa fuente→MER→JSON→Pages y matriz de fallos/reintentos. Corregir contradicciones documentales con evidencia.

**Etapa B, enriquecimiento incremental separado.** Diseñar tarea idempotente que recupere en lote referencias COT desde el ZIP COT y `Descripcion/Obervaciones` de ZIP OC oficiales cuando correspondan al período; clasificar `explicito/documental/candidato/ambiguo`; insertar solo vínculos expresos no presentes, con evidencia de origen (archivo, campo, mes), PK determinística y verificación. Los ZIP mensuales pueden llegar con retrasos; los vínculos entre meses deben buscarse en el universo publicado, sin alterar filas originales. No prometer que todas las candidatas quedarán acreditadas.

**Etapa C, orquestación con salvaguardas.** Mantener cron 16:00 sin cambios mientras se prueba la extensión separada. Proponer dependencia tras `CARGA_VERIFICADA`, lock global, reintento acotado, bitácora por etapa, manejo de meses sin archivo nuevo y fallos sin corromper marcas de éxito. No volver a descargar ZIP históricos ni recorrer todos los meses cada día: detectar fuentes nuevas o cambiadas con hash/fecha y hacer reconciliación incremental.

**Etapa D, publicación y observabilidad.** Exportar solo datos públicos necesarios; actualizar catálogos, índices, relaciones y JSON documental en orden transaccional lógico, validando conteos. Publicar GitHub Pages sin credenciales, verificar respuesta HTTP y caso funcional por mes; mostrar fecha/alcance de última actualización por fuente (licitaciones, OC y COT), evitando afirmar frescura de Compra Ágil si no se ejecutó.

**Etapa E, habilitación.** Revisión de diferencias en entorno de prueba/mes cerrado, regresión de componentes V2, respaldo/rollback y autorización explícita antes de modificar cron o el ETL. El cierre mensual del 10/11 es independiente y manual hasta autorización posterior.

## Lista de pendientes operativos para la siguiente sesión

1. Contrastar cron real y último `CARGA_VERIFICADA` en Ubuntu (no ejecución adicional).
2. Auditar qué campos ya extrae `etl_zip_dos_fuentes.py` y si se puede preservar solo la referencia derivada sin cambiar los registros originales.
3. Reutilizar el importador histórico y el conciliador multimes, evitar código duplicado.
4. Confirmar resultado de Actions para junio/julio/septiembre y comprobaciones de Pages/«Ver detalle» recientes.
5. Diseñar un flujo incremental sin escrituras al principio; presupuestar volumen, cuotas, tiempo, locks y recuperación.
6. Solo entonces solicitar aprobación del cambio operativo, mantener el ETL de las 16:00 intacto hasta ese hito.

**Jerarquía de evidencias:** documentado ≠ implementado ≠ CI aprobada ≠ publicado en Pages ≠ prueba visual ≠ ejecución operativa.
