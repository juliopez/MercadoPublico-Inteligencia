# Automatización y operación desatendida

## Principio

Cada proceso debe tener disparador, entrada, salida, verificación, reintentos y recuperación. Un workflow marcado como `success` **no acredita por sí solo cobertura completa** de datos.

| Cadena | Entrada | Resultado esperado | Control |
|---|---|---|---|
| ETL diario | ZIP licitaciones y OC | MER y extractos actualizados | Logs, conteos, publicación |
| API incremental | Códigos Compra Ágil | Procesos nuevos y checkpoint | Exclusión de repetidos, límites y reintentos |
| Rotación mensual | Cambio de período | Nuevo operativo e histórico anterior | Catálogo y permisos |
| Conciliación | ZIP oficiales del mes vencido | Ajuste histórico auditado | Respaldos, diferencias, verificaciones |
| Índices derivados | Cambios en catálogo y fragmentos | Búsqueda, relaciones y participación sincronizadas | Conteos y pruebas CI |

## Estados de validación

- **Implementado:** código y configuración presentes.
- **Probado en CI:** workflow ejecutado correctamente en GitHub.
- **Probado en producción:** ejecución real con datos y salida verificadas.
- **Ciclo integral comprobado:** rotación, conciliación, recuperación y publicación completadas sin intervención.

A noviembre de 2026, los procesos diarios y la regeneración de índices cuentan con ejecuciones satisfactorias; **la rotación siguiente y la primera conciliación histórica integral aún requieren validación**.

## Documentos operativos originales

- [Política de protección de procesos](POLITICA_PROTECCION_CUATRO_PROCESOS.md)
- [ETL diario](LINEA_BASE_PROTEGIDA_CRON_1600.md)
- [API Compra Ágil](LINEA_BASE_VALIDADA_API_COMPRA_AGIL_400.md)
- [Cambio de mes](INVENTARIO_PROCESO_3_CAMBIO_MES.md)
- [Conciliación histórica](INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md)
- [Auditoría de participación](AUDITORIA_PARTICIPACION_2026-11-06.md)

No cambiar procesos productivos para ajustar documentación.
