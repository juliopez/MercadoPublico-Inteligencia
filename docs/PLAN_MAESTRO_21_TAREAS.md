# Plan maestro definitivo — Plataforma Mercado Público

**Fecha de fijación:** 2026-10-20. **Alcance:** exactamente las 21 tareas aprobadas, preservadas en el orden original. No eliminar ni renumerar tareas; registrar avances y decisiones por separado.

## Arquitectura aprobada

- Google Sheets es el repositorio exclusivo de datos: **un archivo MER v2 por mes histórico** y **uno operativo para el mes en curso**, alimentado por API ChileCompra.
- Días después del cierre del mes, conciliar el mes operativo con los históricos oficiales y archivarlo como mes histórico.
- Carga extraordinaria acotada a **junio, julio y agosto de 2026**; septiembre 2026 ya cargado y auditado. No cargar otros meses pasados sin nuevo acuerdo.
- Frontend público en GitHub Pages; conservar su contrato de datos, con consolidación de múltiples Google Sheets.
- No borrar archivos sin inventario, identificación inequívoca, respaldo y aprobación explícita. No ejecutar escritura o despliegue en producción sin controles previos.

## Tareas invariables

| Nº | Tarea | Estado inicial |
|---:|---|---|
| 1 | Inventariar todas las Google Sheets existentes del proyecto | Avance sustantivo: activos, respaldos y staging identificados; requiere verificar dependencias para declarar exhaustivo |
| 2 | Crear un directorio único en Google Drive para la plataforma | Completada: carpeta principal y cuatro subcarpetas |
| 3 | Organizar las Google Sheets y eliminar las versiones obsoletas, previa revisión y respaldo | Parcial: documentos identificados organizados sin borrar; depuración exige lista exacta y autorización |
| 4 | Estandarizar los nombres de archivos: MER_2026_06, MER_2026_07, etc. | **Completada**: MER_2026_06 a MER_2026_09 y MER_2026_10_OPERATIVO |
| 5 | Validar septiembre de 2026 como primer histórico definitivo | Completada (auditoría de septiembre) |
| 6 | Crear las Google Sheets históricas de junio, julio y agosto de 2026 | Completada: tres archivos creados, seis pestañas y encabezados validados |
| 7 | Cargar y auditar los históricos de junio, julio y agosto de 2026 | **Completada**: junio, julio y agosto cargados y auditados; septiembre ya cerrado |
| 8 | Crear la Google Sheets operativa del mes en curso con el MER de seis tablas | Completada: MER_2026_10_OPERATIVO vacía y ubicada en 02_Operativo_MER |
| 9 | Adaptar los ETL de las API ChileCompra para alimentar la hoja operativa | Pendiente |
| 10 | Implementar actualización incremental diaria y control de errores de API | Pendiente |
| 11 | Diseñar el procedimiento de cierre mensual y consolidación con históricos oficiales | Completada: documento técnico de cierre y conciliación |
| 12 | Automatizar el traspaso del mes cerrado a una Google Sheets histórica | Pendiente |
| 13 | Implementar un catálogo central de Google Sheets y períodos disponibles | **Completada como registro central**: config/catalogo_sheets.json; integración de consumidores corresponde a tareas 9 y 14 |
| 14 | Desarrollar el consolidador Python de datos históricos y operativos | Pendiente |
| 15 | Adaptar la publicación de JSON al contrato de datos del frontend | Pendiente |
| 16 | Integrar y validar la consulta de múltiples períodos desde el frontend | Pendiente |
| 17 | Optimizar búsquedas, filtros, paginación y rendimiento | Pendiente |
| 18 | Implementar controles de integridad y auditoría de las cargas mensuales | Pendiente |
| 19 | Ejecutar pruebas integrales: API → Sheets → JSON → Frontend | Pendiente |
| 20 | Actualizar README, documentación técnica y procedimientos operativos | Pendiente |
| 21 | Realizar despliegue final y verificar GitHub Pages | Pendiente |

## Método de seguimiento

Cada tarea debe registrar fecha, evidencia (enlace al commit, Sheet o auditoría), responsable de la ejecución, resultado y pendientes. Evitar marcar «completado» por la mera publicación de código cuando falte una prueba real o validación de datos.


## Ejecución inicial — 20 de octubre de 2026

- Carpeta central Drive y cuatro subcarpetas creadas. Ver [catálogo](CATALOGO_SHEETS_Y_PERIODOS.md).
- Archivo auditado de septiembre **movido** a Históricos y **renombrado** como `MER_2026_09`, **sin cambiar el identificador** `1lnMVUZ_pn_HkwEvI90yYz5GOMSYzuX-FbcbMR71-oDA`.
- Producción, clon y respaldos existentes **sin cambios**. Ningún archivo eliminado.
- La tarea 1 sigue en curso porque el inventario de dependencias y copias debe completarse antes de una depuración.

## Segunda etapa — 20 de octubre de 2026

Tarea 6 completada. Bases mensuales 2026-06, 2026-07 y 2026-08 creadas vacías y organizadas en carpeta de históricos. Véase [catálogo](CATALOGO_SHEETS_Y_PERIODOS.md). La tarea 7 (carga y auditoría de históricos) permanece pendiente. Sin eliminación de documentos ni cambios a ETL, frontend o producción.

## Tercera etapa — 20 de octubre de 2026

- Tarea 8 completada: [MER_2026_10_OPERATIVO](https://docs.google.com/spreadsheets/d/1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4/edit) creado vacío con seis entidades. La tarea 9, conexión a API, queda pendiente.
- Inventario de hojas y respaldos ampliado; tarea 1 todavía parcial. Ninguna depuración destructiva ejecutada.

- Tarea 11 completada como **diseño**: [procedimiento de cierre mensual](PROCEDIMIENTO_CIERRE_MENSUAL.md). No se ha desarrollado ni activado el disparador automático de la tarea 12.

## Cierre de la tarea 7 — 20 de octubre de 2026

**Completada:** cuatro Google Sheets independientes `MER_2026_06`, `MER_2026_07`, `MER_2026_08` y `MER_2026_09`, con sus seis entidades; todos con auditoría estructural/referencial independiente satisfactoria con observaciones. Totales de filas de las seis entidades por archivo: junio 798.094; julio 810.333; agosto 834.370; septiembre 754.318. **Total acumulado de filas mensuales**: 3.197.115 (no equivale a identidades o procesos únicos entre meses). Detalles en [catálogo](CATALOGO_SHEETS_Y_PERIODOS.md). OC fuera de corte, resultados no verificados e identidad de proveedores son salvedades documentadas. No se modifica producción ni frontend.

## Organización y catálogo — 20 de octubre de 2026

- Los cuatro históricos y la hoja operativa presentan nombres normalizados y ubicación por categoría. Tarea 4 completada.
- Se publicó [catálogo central JSON](../config/catalogo_sheets.json) para uso posterior por ETL y consolidador. Tarea 13 completada **como registro versionado**, sin afirmar que los consumidores actuales lo utilicen.
- Se organizaron respaldos, archivos de staging y hojas auxiliares identificados en Drive, conservando los IDs. Producción antigua y clon permanecen fuera de la migración. Ver [inventario](CATALOGO_SHEETS_Y_PERIODOS.md).
- **No se ejecutó eliminación** de documentos. Tarea 3 continúa parcial. Tarea 1 sigue pendiente de auditoría final de dependencias/alcance de búsqueda para cerrarla sin afirmar exhaustividad no acreditada.

## Decisión arquitectónica posterior — 20 de octubre de 2026: sin API

**Esta decisión sustituye la alimentación mediante API, sin cambiar la numeración de las 21 tareas.** Junio–septiembre de 2026 permanecen históricos cerrados y auditados. El mes en curso usa descargas masivas mensuales oficiales, actualizadas periódicamente, y Google Sheets MER operativo. No se actualizan retrospectivamente meses históricos anteriores.

- **9 (redefinición):** adaptar el ETL de descargas masivas de licitaciones, Compra Ágil y OC del mes corriente a MER operativo, no utilizar API ChileCompra.
- **10 (redefinición):** programar descarga periódica, validación y actualización de la instantánea del mes actual; registrar fecha/hora y origen; reintentar sin borrar datos válidos ante fallas.
- **11 (ajuste del diseño ya completado):** conservar cierre mensual y conciliación con descargas oficiales; eliminar dependencia obligatoria de API.
- **12 (ajuste):** archivar al cierre del mes la copia operativa conciliada, manteniendo MER histórico.
- **13–19:** consolidador y publicación deben mostrar última sincronización exitosa y aviso explícito de posible desfase frente al portal, sin afirmar tiempo real.
- **Criterio horario inicial propuesto:** después de las 14:00 de Chile continental, por ejemplo 16:00; confirmar acceso directo, integridad y formato de las tres fuentes antes de activar el programa.
- **Advertencia:** la documentación oficial indica actualización diaria de las descargas masivas y desfase de un día, pero no certifica que los tres archivos tengan siempre idéntica cobertura u hora de disponibilidad. No registrar una sincronización como exitosa hasta verificar las fuentes pertinentes y publicar la instantánea atómicamente.
- **Estado:** cambio de arquitectura acordado; automatización todavía **no implementada ni activada**. No tocar históricos cerrados, frontend ni producción antigua durante la transición.
