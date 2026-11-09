# Punto de recuperación operativa — Observatorio de Mercado Público

**Última revisión documental:** 2026-11-09 (Chile). **Repositorio:** `juliopez/MercadoPublico-Inteligencia`, rama principal `main`.

> **Empezar aquí al abrir un nuevo chat.** Esta carpeta es el índice de continuidad; no reemplaza el código, los logs Ubuntu, los resultados de GitHub Actions ni la documentación protegida. Las afirmaciones de ejecución requieren evidencia reciente.

## Lectura obligatoria y orden

1. [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md): qué sabemos, qué está pendiente y qué no se debe afirmar.
2. [INVENTARIO_PROCESOS.md](INVENTARIO_PROCESOS.md): disparadores, archivos, dependencias, controles y runbooks.
3. [AUDITORIA_OPERATIVA.md](AUDITORIA_OPERATIVA.md): evidencia documentada y protocolo de auditoría.
4. [INCIDENCIAS_PENDIENTES.md](INCIDENCIAS_PENDIENTES.md): riesgos abiertos y criterios de cierre.
5. [HISTORIAL_CAMBIOS.md](HISTORIAL_CAMBIOS.md): decisiones, cambios relevantes y referencias.
6. [Política maestra de protección](../POLITICA_PROTECCION_CUATRO_PROCESOS.md): **prevalece ante cualquier resumen**.

## Hito operativo: cron de licitaciones API 16:15 (2026-11-09)

**Evidencia:** salida de terminal Ubuntu aportada el 9 de noviembre de 2026: `git pull --ff-only origin main` completado hasta `e643fa688`; `bash scripts/instalar_cron_licitaciones_1615.sh` informó `CRON_INSTALADO`; `crontab -l | grep MER_LICITACIONES_API_1615` confirmó la entrada `15 16 * * 1-5`. Huso horario local validado por el instalador: `America/Santiago`.

**Estado:** código actualizado, cron **instalado y programado**; **sin evidencia todavía de ejecución productiva, carga MER ni publicación V2**. Primera ejecución prevista: **martes 10 de noviembre de 2026, 16:15 (Chile)**.

**Contrato aprobado:** consultar el listado API del **día de ejecución** y recuperar **todos** sus códigos, incluso cuando la publicación original corresponda a octubre u otro mes. Sin cuota diaria de 400. Procesar en lotes de 200 detalles, con pausa API, reintentos y checkpoint SQLite. Cargar registros nuevos en **Procesos del MER operativo vigente**, sin alterar los MER históricos y conservando fecha original. Respaldar/verificar la escritura y publicar V2 después de cada lote. La tarea es independiente de cron 16:00 y Compra Ágil nocturna.

**Archivos:** `scripts/ubuntu_recuperar_licitaciones_1615.sh`, `scripts/recuperar_licitaciones_api.py`, `scripts/cargar_licitaciones_api_mer.py`, `scripts/instalar_cron_licitaciones_1615.sh`, `deploy/cron/licitaciones-api-1615.example`.

**Primera auditoría (10/11):** contrastar listado y códigos únicos del día, detalles recuperados/fallidos, checkpoint, respaldo y lectura posterior MER, resultado de publicación, duración, locks y convivencia con otros procesos. Consultar `logs/licitaciones_api_1615.log` en Ubuntu. No confundir instalación exitosa con ejecución exitosa.

## Cómo reanudar una auditoría

1. Leer estos documentos y la política maestra.
2. Inspeccionar el **estado real** de `main`, workflows, últimos runs, scripts, catálogo y artefactos públicos.
3. Solicitar o revisar evidencia de Ubuntu cuando no esté disponible desde GitHub (timers, `journalctl`, cron, logs, checkpoints). **No inferir el estado de Ubuntu a partir del código**.
4. Distinguir `documentado`, `implementado`, `instalado`, `ejecutado`, `validado` y `pendiente`.
5. Auditar en orden: cron 16:00 → disparador/API nocturna → rotación → conciliación → publicación → índices → frontend.
6. Proponer correcciones solo ante problemas verificados. **No modificar** ETL, API, timers, locks, workflows productivos ni contratos sin autorización expresa y análisis de impacto.
7. Al finalizar, actualizar estado, auditoría, incidencias e historial **solo con evidencia obtenida**, incluyendo fecha, commit y resultados.

## Prompt para una conversación nueva

> Continuemos la auditoría operativa del Observatorio de Mercado Público, repositorio `juliopez/MercadoPublico-Inteligencia`. Lee primero `docs/continuidad/README.md`, sus cinco documentos vinculados y `docs/POLITICA_PROTECCION_CUATRO_PROCESOS.md`. Contrasta el estado documentado con el código y las últimas ejecuciones de GitHub Actions; para Ubuntu, identifica qué evidencia local falta. Audita cron, API nocturna, rotación, conciliación, publicación e índices. No modifiques procesos protegidos sin mi aprobación expresa. Al cerrar, actualiza la documentación de continuidad.

## Documentación pública y técnica

- [README principal](../../README.md) · [Arquitectura](../ARQUITECTURA.md) · [Modelo de datos](../MODELO_DATOS.md).
- [Operación](../OPERACION.md) · [Automatización](../AUTOMATIZACION.md) · [Índice documental completo](../INDICE_DOCUMENTACION.md).
- [Mapa de workflows](../GITHUB_ACTIONS_MANTENIMIENTO.md).

**Nota de alcance:** esta carpeta está en un repositorio público. No incluir secretos, tokens, rutas locales sensibles, identificadores privados ni logs con datos personales.
