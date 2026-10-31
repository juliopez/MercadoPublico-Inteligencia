# Auditoría de la primera prueba productiva API Compra Ágil 400 en GitHub Actions — 31/10/2026

## Dictamen

**Motor de recuperación validado en runner de GitHub Actions: 400/400 detalles consultados, 0 errores finales. Workflow completo: FALLIDO durante la validación posterior, sin publicación de cola/índices/Pages.** No atribuir al flujo integral un éxito que GitHub no registró.

- Ejecución: [Actions #41165067142](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41165067142), intento 1; job 124430738681.
- 31/10/2026 00:35:55 Santiago (03:35:55 UTC), término 01:51:35 Santiago (04:51:35 UTC): **75 min 40 s aproximadamente**.
- Resultado registrado por el motor en logs: `{"id_ejecucion":"gha-41165067142-1","periodo":"2026-10","fecha":"2026-10-31","consultados":400,"procesos":400,"ofertas":1839,"resultados":279,"errores":0,"pagina":51}`.
- Cinco reintentos temporales HTTP 429 en los logs; ninguno dejó error final.
- El paso **Preflight** aprobó; instalación de dependencias y autenticación necesarias permitieron avanzar y completar la recuperación. Por tanto hubo conexión operativa real con la API y Sheets.
- El paso **Ejecutar recuperación incremental** termina `exit code 1` **después** de emitir el reporte, por `BLOQUEO: periodo de informe incompatible`.
- Los pasos de exportación posterior, regeneración de índices, publicación de estado mediante git y despacho de Pages **no se ejecutaron**. El archivo `control/ultimo_reporte_api_mer.json` de main continuó mostrando el lote Ubuntu del 30/10 (400, 2.178 ofertas, 288 resultados, página 11), no este lote Actions.

## Causa raíz comprobada

El disparo puntual se realizó con evento `push`, no `workflow_dispatch`. En el preflight se había usado `inputs.periodo || '2026-10'`, pero el paso posterior usó `inputs.periodo` sin respaldo. Los registros del job muestran `PERIODO_SOLICITADO:` vacío; el motor reportó correctamente `periodo: 2026-10` y el chequeo posterior lo rechazó.

**Corrección acotada aplicada al wrapper Actions**: declarar `PERIODO_SOLICITADO` una sola vez en `jobs.lote-api.env` con `inputs.periodo || '2026-10'` y eliminar sobrescrituras locales vacías. Commit `bb1aad8187c75889b0609fa8658b637afe7a057b`. **No afecta el motor `scripts/mer_api_incremental_10.py` ni la línea base Ubuntu de 400**.

## Consecuencia de persistencia: atención antes de la segunda ejecución

El motor interactuó con Google Sheets antes del fallo. Los datos **pudieron quedar escritos**, pero esta revisión no contrastó aquí conteos finales directos en las seis pestañas, de modo que no debe afirmarse que cada escritura quedó consolidada y completa. La cola incremental actualizada por Actions **no fue incorporada a `main`** debido al fallo, y tampoco el reporte ni los derivados públicos.

**PROHIBIDO reejecutar a ciegas el lote de 400 con la cola anterior:** el motor volvería a seleccionar códigos de las mismas páginas; deduplicación de MER podría evitar filas duplicadas, pero produciría consultas innecesarias y desalineamiento temporal. Recuperar primero la cola del intento 1 mediante respaldo del runner (si existe), o reconstruir/reconciliar contra las hojas MER y listado oficial; verificar los 400 códigos y los conteos reales antes de un nuevo disparo. No etiquetar como '400 adicionales incorporados' sin comprobar identificadores y unicidad.

## Comparación de rendimiento

| Ejecución | Consultados | Ofertas procesadas | Resultados procesados | Duración | Final |
|---|---:|---:|---:|---|---|
| Ubuntu 30/10 | 400 | 2.178 | 288 | 78m36s | Validada y publicada |
| GitHub Actions 31/10 | 400 | 1.839 | 279 | ~75m40s | Recuperación sí; workflow y publicación no |

Las ofertas/resultados varían por códigos del lote; no es evidencia de pérdida de datos. La diferencia de duración ~2m56s no permite concluir que GitHub es intrínsecamente más rápido: tienen contenidos y respuestas API distintos.

## Pendientes de cierre

1. Conciliar contra Google Sheets los códigos recuperados y la ausencia de duplicados.
2. Reconstruir y preservar la posición de `fecha_cursor`, `pagina` y el estado por código del intento 1 antes de ejecutar otro lote.
3. Validar que la etapa de exportación, derivados, commit/push y Pages opere en una futura prueba, con controles de seguridad y sin interferir con ETL 16h.
4. El modo nocturno recurrente **no ha sido activado**; mes histórico fuera de ventana sigue restringido.
5. No modificar sin autorización los cuatro procesos protegidos; la corrección anterior es exclusiva del nuevo wrapper Actions y no altera timers ni motor Ubuntu.

**Fuentes de evidencia**: metadatos GitHub Actions, pasos y logs descargados del job, `control/ultimo_reporte_api_mer.json` de main, archivo del workflow, commit de corrección. Auditoría realizada 31/10/2026.
