# Procedimiento de cierre mensual — MER v2

**Estado:** diseño operativo aprobado como documento técnico, **sin ejecución**. La hoja operativa del mes en curso contiene seis entidades MER v2 y es alimentada por la API. El histórico mensual definitivo se materializa **días después del cierre**, una vez disponibles los archivos oficiales.

## Ciclo mensual
1. **Operación diaria:** escribir exclusivamente en `MER_AAAA_MM_OPERATIVO` mediante ETL API, con inserción idempotente por PK, logs, reintentos limitados y auditoría de errores. No modificar históricos cerrados.
2. **Corte:** transcurridos los últimos días del mes, fijar fecha/hora del cierre lógico; pausar escrituras de ese período y crear respaldo integral de la hoja operativa.
3. **Fuentes oficiales:** obtener ZIP oficiales del mes para licitaciones, Compra Ágil y OC; comprobar correspondencia del período y completar manifiesto con nombres, tamaño, SHA-256 y fecha de obtención. No inferir que una OC se corresponde temporalmente con el mes de publicación del proceso.
4. **Preparar:** ejecutar el importador generalizado para producir seis CSV MER v2 con informe y auditoría. No escribir directamente el paquete hasta revisar discrepancias, especialmente proveedores, selección de ofertas y OC.
5. **Conciliar:** comparar API operativa y fuente oficial por claves; priorizar las fuentes oficiales para valores históricos, preservar registros que todavía carezcan de resolución y registrar diferencias/duplicados. Las 8.275 OC fuera de corte observadas en septiembre muestran que un enlace COT–OC fuera del mismo mes es legítimo y **no se debe forzar**.
6. **Materializar histórico:** crear nueva hoja `MER_AAAA_MM` en `01_Historicos_MER`; completar y verificar las seis entidades mediante carga autorizada, respaldada y recuperable.
7. **Auditoría bloqueante:** confirmar encabezados, conteos, PK, FK a Procesos/Ofertas/Proveedores, consistencia oferta–resultado, unicidad de pares COT–OC, estados de OC y origen por período; separar errores de observaciones aceptadas.
8. **Publicación:** registrar el Sheet ID histórico en catálogo; actualizar exclusivamente los JSON compatibles con contrato del frontend mediante consolidador, validar sitio y despliegue por etapas.
9. **Rotación:** tras aprobación del histórico y su publicación, reemplazar referencia del ETL a un **nuevo archivo operativo** del mes siguiente. No borrar el archivo operativo anterior hasta verificar el histórico y su respaldo.
10. **Trazabilidad:** documentar respaldo, paquetes y hashes, resultados de auditoría, conflictos, commit GitHub y responsables/fechas.

## Reglas obligatorias

- Los históricos son inmutables tras el cierre, salvo proceso de corrección auditado y respaldado.
- Una selección marcada en histórico COT no es necesariamente una adjudicación jurídica; nunca forzar `validado=true`.
- No eliminar archivos ni alterar ETL productivos o frontend sin validación específica.
- Evitar cargas simultáneas al mismo destino y escrituras sobre rangos que puedan contener registros anteriores.
- Nunca trasladar automáticamente la Google Sheets operativa «tal cual» sin confrontar con el histórico oficial.
- No asumir que Google Sheets de un mes entero cabrá: comprobar el límite de 10 millones de celdas **por archivo** y bloquear sobrepasos.
- Meses extraordinarios a cargar inicialmente: junio, julio y agosto de 2026; septiembre ya cerrado. Octubre y sucesivos siguen el ciclo operativo descrito.

## Pendientes técnicos para automatización real
1. Conectar API ChileCompra al MER operativo, sin tocar ETL de producción actual.
2. Diseñar conciliador oficial/API y cargador con resolución de colisiones y datos actualizados.
3. Implementar disparador de cierre sujeto a disponibilidad de históricos y auditorías; **no** cierre ciego el día primero.
4. Implementar consolidador y publicación transaccional JSON; pruebas integrales antes de activar.
