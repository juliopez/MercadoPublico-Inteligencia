# Cron integrado Ubuntu — 22 de octubre de 2026

## Objetivo
Integrar la conciliación documental COT–OC al ETL diario existente.

## Ejecución
- Lunes a viernes, 16:00, America/Santiago.
- Cron horario con control de día y hora.
- Orquestador: scripts/ubuntu_cron_integrado.sh.
- ETL principal: scripts/ubuntu_etl_dos_fuentes.sh.
- Conciliador: scripts/etl_conciliacion_cot_oc.py.
- Descarga incremental OC: scripts/descargar_oc_incremental.py.

## Fuentes
- Licitaciones: ZIP oficial diario.
- Órdenes de compra: ZIP oficial diario.
- Compra Ágil: no se exige ZIP diario.
- Los datos existentes de Compra Ágil se preservan.
- La recuperación futura mediante API es independiente.

## Conciliación
- Extraer referencias desde Descripcion/Obervaciones.
- Contrastar COT en MER históricos y operativo.
- Reconocer vínculos entre diferentes meses.
- Excluir duplicados y casos ambiguos.
- Escribir únicamente en VinculosCOT_OC.
- Mantener respaldos y bloqueo compartido.

## Pruebas del 22/10/2026
- OC examinadas: 302727.
- Referencias documentales: 8723.
- Vínculos existentes inicialmente: 861.
- Referencias sin COT en MER: 5339.
- Vínculos nuevos insertados y verificados: 2523.
- Casos ambiguos excluidos: 8.
- Segunda simulación: cero vínculos pendientes.
- Verificación de prerrequisitos del integrador: aprobada.

## Estado
Cron integrado instalado en Ubuntu.
Primera ejecución automática integral: pendiente de verificación.

## Seguridad
No publicar credenciales, respaldos, ZIP originales,
logs operativos ni información privada de Google Sheets.
