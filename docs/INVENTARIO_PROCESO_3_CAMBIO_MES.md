# PROCESO 3 — Cambio y rotación mensual del MER

> **Estado: implementado, instalado y rotación octubre → noviembre ejecutada y verificada el 30/10/2026.** La próxima ejecución desatendida aún no está demostrada. **No modificar la línea base protegida de las 16:00 ni la ejecución API manual de 400.**

## Objetivo, disparo y separación
Automatizar, **el último día hábil de Chile**, la transición del mes en curso al histórico operativo y dejar un único MER operativo para el siguiente período. La rotación **no equivale** a la conciliación oficial diferida del proceso 4.

- Temporizador Ubuntu (no GitHub Actions): `deploy/systemd/mercadopublico-rotacion.timer`, `OnCalendar=Mon..Fri *-*-* 19:00:00`, `Persistent=true`; servicio `mercadopublico-rotacion.service`.
- El timer **evalúa** a las 19:00 de lunes a viernes; el código decide si corresponde al último día hábil con `config/feriados_chile_conciliacion.json`. Permite recuperación restringida el primer día hábil posterior antes de las 16:00.
- Dependencia previa: ETL ordinario de las 16:00 concluido y verificado, sin cambios en su configuración.

## Flujo extremo a extremo

| Nº | Etapa | Control o resultado | Ejecutor |
|---|---|---|---|
| 1 | Disparo local y exclusión | Ventana, `flock` de escritura compartida; si otro MER escribe, aplaza | `mercadopublico-rotacion.timer/.service`, `scripts/ubuntu_rotacion_mensual.sh` |
| 2 | Puerta calendario | Último día hábil, hora Santiago y feriados verificados; recuperación acotada | `scripts/rotar_mes_operativo.py` |
| 3 | Verificación del origen y destino | Catálogo, IDs, SCHEMA de seis pestañas, carpeta de Drive, destino siguiente vacío | `scripts/rotar_mes_operativo.py`, `config/catalogo_sheets.json` |
| 4 | Preparación del próximo MER | Reutilizar el ya creado o generar uno nuevo con seis hojas y cabeceras; comprobar permisos | `scripts/rotar_mes_operativo.py`, Google Sheets/Drive |
| 5 | Traslado del mes que termina | Mantener el mismo spreadsheet ID, mover a `01_Historicos_MER` y actualizar nombre | `scripts/rotar_mes_operativo.py`, Drive API |
| 6 | Catálogo y evidencia | Mes previo pasa a `historico` **pendiente de conciliación oficial** y nuevo mes a `operativo`; evidencias de cambio/confirmación | `config/catalogo_sheets.json`, GitHub y estado local |
| 7 | Continuidad de publicación | El siguiente ETL de las 16:00 utiliza el MER del nuevo mes; derivados y V2 se publican mediante la línea base existente | Cron protegido 16:00 y workflows V2 (dependencia, **no componente que deba modificarse**) |

## Inventario técnico
**Scripts principales (2):** `scripts/ubuntu_rotacion_mensual.sh`, `scripts/rotar_mes_operativo.py`.

**Temporizador y servicio (2 unidades):** `deploy/systemd/mercadopublico-rotacion.timer` y `.service`.

**Dependencias:** `config/catalogo_sheets.json`, `config/feriados_chile_conciliacion.json`, seis tablas SCHEMA desde `scripts/importador_historicos_v2.py`, credenciales privadas Ubuntu, Drive/Sheets, acceso a GitHub y candado `logs/.mer_escritura_compartida.lock`.

**Salida:** MER mensual siguiente operativo; anterior conservado con ID estable y estado `cierre_operativo_pendiente_conciliacion_oficial` hasta proceso 4; registro de rotación.

## Validación y límites
- **30/10/2026, ~20:29 Santiago:** `bash scripts/ubuntu_rotacion_mensual.sh` terminó con `ROTACION_OPERATIVA_CONFIRMADA 2026-10 siguiente 2026-11`.
- Drive verificó octubre trasladado a `01_Historicos_MER`, conservando ID; noviembre en `02_Operativo_MER`; catálogo GitHub actualizado.
- **Temporizador documentado como instalado y habilitado**; no confundir prueba manual de rotación con un segundo disparo desatendido exitoso.
- **Pendiente de evidencia:** primer ETL y publicación de noviembre; siguiente cierre ejecutado exclusivamente por timer. Esto no invalida la rotación real ya comprobada.
- **No volver a aplicar** a octubre por rutina. Evitar duplicación, pérdida de hojas o sobreescritura.
- Si falla un paso, registrar el estado y recuperar sin crear dos MER operativos.

## Fronteras protegidas
**Proceso 1:** [cron 16:00 validado](LINEA_BASE_PROTEGIDA_CRON_1600.md).
**Proceso 2:** [API Compra Ágil manual 400](LINEA_BASE_VALIDADA_API_COMPRA_AGIL_400.md).
**Proceso 4:** [consolidación histórica del día 10 hábil](INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md), independiente de esta rotación.

**Gobierno de cambios:** preservar esta implementación ya probada; cualquier intervención requiere justificación, pruebas y respaldo, sin alterar procesos 1 y 2.
