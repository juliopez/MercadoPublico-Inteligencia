# Preparación de traslado AUX-1615 a GitHub Actions — 12/11/2026

**Estado: PILOTO NO ACTIVADO.** Se mantiene intacto el cron local de las 16:15 y su script Ubuntu. No ejecutar simultáneamente piloto y cron local sobre el MER.

## Alcance del prototipo
Workflow `.github/workflows/licitaciones-api-1615-actions.yml` en rama de preparación, con activación manual, lotes de 200, pausa 10 s, escritura MER y exportación. Reutiliza las credenciales GitHub Actions existentes. La ejecución se realiza en runner remoto, no en Ubuntu.

## Condiciones obligatorias antes de activar el cron de mañana
1. Revisar y resolver persistencia/reanudación de checkpoint SQLite entre ejecuciones (actualmente solo se adjunta como artifact de la ejecución). Una ejecución interrumpida no se reanuda automáticamente.
2. Asegurar que el runner remoto publique todas las entidades y derivados requeridos, incluyendo vínculos documentales y Pages, con verificación HTTP del catálogo. El prototipo aún no replica íntegramente `ubuntu_publicar_v2_post_etl.sh`.
3. Coordinar exclusión mutua entre el cron local AUX-1615, la conciliación P7 y otros escritores MER; `concurrency` de Actions no bloquea Ubuntu ni otros workflows.
4. Probar una jornada en modo controlado, comprobar filas MER, checkpoints, índices y frontend.
5. Solo entonces reemplazar el cron Ubuntu de las 16:15 por un disparador remoto, conservando respaldo y reversión. No dejar ambos procesando en paralelo.

## Protección
No activar automáticamente el piloto ni modificar cron productivo mientras falten estos controles. El objetivo de mañana es efectuar el cambio **solo si** se verifican los requisitos; de lo contrario se conserva el proceso probado en Ubuntu.
