# Implementación inicial de cola de consultas API MER — Fase 2

## Alcance y evidencia
- Se revisó mediante Google Sheets la metadata del MER operativo 2026-10: seis pestañas `Procesos`, `Proveedores`, `Ofertas`, `OrdenesCompra`, `VinculosCOT_OC`, `Resultados`. **No hay pestaña literal «registros fallidos» en este MER**. No agregarle una pestaña por conjetura.
- Se agregó `scripts/cola_consultas_api_mer.py`: selección local y determinista sobre snapshot `Procesos` y JSON técnico de estado (sin red, sin API ni escritura Sheets).
- Se agregaron pruebas `tests/test_cola_consultas_api_mer.py` y CI `.github/workflows/pruebas-escritor-api-mer.yml`.
- La cola sigue la regla aprobada: `PENDIENTE` nuevo del día, `ERROR` con reintento vencido, `EN_SEGUIMIENTO`/`SIN_DATOS` con revisión vencida; `COMPLETO` excluido. Se consideran solo códigos Compra Ágil.
- Controla códigos duplicados, cupos y presupuesto máximo configurables, reserva/reasignación entre los tres grupos. `--etl-fallido` bloquea los nuevos sin impedir examinar fallos/seguimiento ya conocidos.
- Función `checkpoint()` propone cambios de estado y próxima consulta, pero **no persiste automáticamente resultados de una ejecución API ni la enlaza al escritor**. Es una pieza para integrar, no un servicio programado.
- No se invocó ChileCompra ni se cambió el cron o la publicación de Pages.

## Limitaciones pendientes de resolver antes de activar producción
1. El criterio inicial para nuevos es `fecha_publicacion` igual al día de la ejecución. Para identificar *todos* los recién incorporados por ETL, incluso si se publicaron antes, el integrador debe usar la diferencia real de códigos entre snapshots o alta reciente, no solo la fecha de publicación.
2. Persistir el estado y checkpoint privados de forma atómica con lock; conectar a API, caché, escritor y validación de MER; registrar límites/429.
3. Definir los criterios oficiales de `COMPLETO`, verificando el estado real del proceso sin confundir selección con adjudicación.
4. No existe todavía un cron/API productivo a las 22:30. No activar hasta test integrado y prevención de carreras de escritura.
5. Los días hábiles de la regla de negocio aún deben normalizarse. Los intervalos de la implementación son días calendario, todavía no ajustados a feriados/días hábiles.
6. Revisar de dónde procede la «pestaña de fallidos» mencionada por el usuario: puede estar en un libro auxiliar diferente. No crear un segundo control si existe otro registro ya operativo.

## Ejemplo offline
```bash
python scripts/cola_consultas_api_mer.py \
  --procesos-json /ruta/privada/procesos.json \
  --estado-json /ruta/privada/cola.json \
  --fecha 2026-10-28 --presupuesto 120 \
  --salida /ruta/privada/plan.json
```

El archivo `procesos.json` debe ser una matriz con la cabecera exacta de `Procesos`; `cola.json` es un objeto JSON cuyas claves son códigos de proceso. El selector no realiza llamadas API.

## Estado
**Selector y pruebas implementados en rama de PR #1; fase 2 nocturna pendiente de integración.**
