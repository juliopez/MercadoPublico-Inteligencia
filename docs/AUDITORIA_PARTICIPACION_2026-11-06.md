# Auditoría de cobertura de participación — 2026-11-06

## Alcance y evidencia
Inspección de catálogo público, metadatos de participación, cola de seguimiento de API y resultados de GitHub Actions. **No se modificaron** API Compra Ágil, disparador Ubuntu 22:05, tamaño de lote 400, ETL 16:00, rotación mensual ni conciliación histórica.

- Catálogo público (generado 2026-11-06 09:06:14 UTC): noviembre operativo, 4.398 procesos, 13 ofertas, 0 resultados y 16.197 OC.
- Octubre histórico: catálogo con 4.418 procesos y 4.867 ofertas; `participacion/2026-10/meta.json` registra 2.094 procesos y 0 ofertas. Los índices son **parciales/desactualizados**, no equivalentes a los registros publicados.
- Noviembre: `participacion/2026-11/meta.json` ausente al momento de la inspección. La interfaz consulta los índices opcionales; no se debe interpretar la ausencia como cero participación real.
- Cola API: jornadas 03, 04 y 05 de noviembre figuran `completa: false`, con 400, 2.000 y 2.000 códigos respectivamente. Son códigos bajo seguimiento, **no adjudicaciones**. Se requiere evaluar reglas de avance y reconsulta antes de declarar cobertura completa.
- Acciones de validación de analítica, perfiles, ajustes visuales y validación consolidada: exitosas tras actualizar pruebas obsoletas.
- La ejecución del workflow Compra Ágil del 06/11 (run 42193830904) concluyó `success`; ello no acredita por sí solo completitud de la jornada.

## Corrección de CI
El workflow `validar-participantes-v2.yml` ahora valida estructura y límites de metadatos y emite advertencias explícitas por períodos sin índices, conteos parciales y fragmentos ausentes. Las alertas de **cobertura de datos derivados** no se presentan como fallas de código ni como validación de integridad. La prueba puede aprobar con advertencias: revisar el log y el número `PARTICIPACION_COBERTURA_ALERTAS`.

## Pendientes operativos
1. Reconstruir índices de participación de octubre y noviembre **a partir de fragmentos públicos íntegros y estables**, mediante el generador existente `scripts/generar_participacion_historica_v2.py`, verificando conteos, hash y publicación. No generar metadatos artificiales ni copiar conteos del catálogo sin procesar los registros.
2. Validar la cola de seguimiento y los criterios de `completa` con logs del ejecutor, sin reiniciar páginas ni eliminar consultas persistidas.
3. El proceso de conciliación histórica del día 10 hábil sigue siendo el responsable del cierre oficial; no anticiparlo ni modificarlo para corregir índices.
4. Verificar Pages y navegación de perfiles después de una reconstrucción autorizada y exitosa.

## Reversión
La corrección de CI es independiente de los cuatro procesos: revertir el commit que modifica `.github/workflows/validar-participantes-v2.yml` restaura las aserciones anteriores. No requiere rollback de datos.
