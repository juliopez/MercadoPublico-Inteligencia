# Bitácora operativa — 10 de noviembre de 2026

> Registro de continuidad basado en capturas de terminal aportadas durante la auditoría. No sustituye la inspección de los artefactos locales ni autoriza operaciones productivas.

## 1. Incidencias y recuperación (mañana 10/11, Chile)

- 08:19:45: se activó `mercadopublico-conciliacion.service`, que invoca `scripts/ubuntu_preparar_conciliacion_persistente.sh`.
- 09:27:10: constancia local `~/.local/share/mercadopublico/cierres/2026-10/constancia_carga_real.json` con `estado=CARGA_VERIFICADA`, `traslado_autorizado=false`, respaldo con archivo, bytes, SHA-256 y registros de las seis tablas: Procesos, Ofertas, Resultados, OrdenesCompra, Proveedores y VinculosCOT_OC.
- 09:28:16: exportación MER V2 verificada.
- 09:31:33: falla del servicio al publicar por `git push origin main` rechazado (rama remota avanzó). No es evidencia de fallo de carga MER. El servicio terminó con código 1.
- 09:41: el operador detuvo `mercadopublico-conciliacion.timer` para evitar reiteraciones mientras se recuperaba el repositorio. Comprobación posterior: `inactive`.
- 09:44: sincronización manual de Git local con remoto; merge `5e71dee1`, sin conflictos reportados. Se verificó que las modificaciones locales y remotas no compartían archivos en el diagnóstico mostrado (1 archivo local y 823 remotos en ese corte).
- 09:50: ejecución manual de `scripts/publicar_cierre_historico_v2.py --periodo 2026-10` falla inicialmente por ausencia de variable de credencial Google en la terminal. Se verificó que el archivo `~/.config/mercadopublico/servicio-google.json` existe, sin exponer su contenido.
- 09:52–09:56: con `GOOGLE_APPLICATION_CREDENTIALS` configurada en la sesión, publicación manual exitosa. `EXPORTACION_V2_VERIFICADA`, generación de índices de búsqueda/perfiles/analítica, commit `77df3d0d`, push a `main` y `PAGES_HISTORICO_VERIFICADO 2026-10`, `estado=PUBLICACION_HISTORICA_VERIFICADA`.
- Conteos del histórico exportado: Procesos 91.925; Ofertas 470.841; Resultados 56.813; ÓrdenesCompra 167.042. Son totales del histórico, **no** nuevos registros del día.
- 09:56: `estado_cierre.json` indica `LISTO_PARA_CONCILIAR`; `resumen_diagnostico_cierre.json` indica `DIAGNOSTICO_OFICIAL_MENSUAL_LISTO_PENDIENTE_CARGA` y `traslado_autorizado=false`. No consta autorización de traslado definitivo en Drive. No equiparar publicación en Pages con cierre administrativo en Drive.

## 2. Temporizadores y riesgo inmediato

- `mercadopublico-conciliacion.timer`: `inactive` tras detención manual; no se ejecutará a las 10:00 mientras siga así. Su servicio llama al script de conciliación persistente y, en la ejecución del día, intentó cierre histórico. **No reiniciar sin verificar idempotencia y alcance**.
- `mercadopublico-rotacion.timer`: siguiente 19:00 Chile.
- `mercadopublico-api-github-dispatch.timer`: siguiente 22:05 Chile.
- No se ha acreditado que exista un segundo timer separado de las 10:00: la hora y función deben verificarse con `systemctl --user cat mercadopublico-conciliacion.timer mercadopublico-conciliacion.service` y los scripts invocados.
- Para preservar la ejecución prevista, **no iniciar manualmente el servicio a ciegas**. Verificar primero si la tarea de las 10:00 era una repetición del cierre, una comprobación o un trabajo diferente. Si el disparo se pierde, registrar ejecución manual controlada después de validar condiciones.

## 3. Plan de carga oficial: bloqueos legítimos

Archivo local `~/.local/share/mercadopublico/cierres/2026-10/plan_carga_cierre.json`:
- `autorizado_para_escribir=false`; `autorizado_para_mover=false`.
- Ofertas: 46.974 candidatos a insertar; Resultados: 56.163 candidatos y 650 actualizaciones sujetas a revisión; OrdenesCompra: 24.861 candidatos y 36.245 revisiones; Proveedores: 8.689 candidatos y 13.315 revisiones; VinculosCOT_OC: 58.569 candidatos.
- Registros solo operativos no deben eliminarse por ausencia en ZIP: Ofertas 4.867; OrdenesCompra 2.859; Proveedores 46; VinculosCOT_OC 2.676. Requieren políticas de preservación.
- Las cifras son candidatos del plan, no escrituras ejecutadas; las diferencias requieren revisión campo a campo. La constancia `CARGA_VERIFICADA` y el diagnóstico `PENDIENTE_CARGA` representan etapas distintas; investigar antes de cambiar flags.

## 4. Ruta B Compra Ágil — Tordo (trabajo paralelo)

- Rama de prueba `feature/compra-agil-tordo-ruta-b`, clon independiente `~/Descargas/mercado-publico-tordo-prueba`.
- Cuatro pruebas unitarias del script `tests/test_compra_agil_tordo_ruta_b.py` superadas.
- `scripts/compra_agil_tordo_ruta_b.py --fecha 2026-11-09` devolvió 0 procesos, 100 registros examinados, última fecha publicada 2026-11-06, atraso de 4 días; `estado=REVISAR_NO_APTO`, `escritura_mer=false`, `cobertura_oficial_demostrada=false`.
- Pruebas exploratorias previas Tordo: 05/11, 514 procesos únicos; 06/11, 585; 09/11, 0 en la ventana observada. Estas cifras no demuestran cobertura oficial ni actualidad diaria.
- **No habilitar Ruta B en MER productivo** hasta contrastar cobertura, latencia, identificadores y deduplicación con fuente oficial independiente.

## 5. Pendientes y próxima acción segura

1. Inspeccionar unidad `systemd` y script invocado para identificar exactamente la operación de las 10:00; distinguirla del cierre histórico ya publicado.
2. Inspeccionar estado del proceso manual y el resultado de Pages (ya verificado en terminal); no repetir exportación.
3. Verificar condiciones de autorización y evidencia de traslado en Drive; no inferir autorización a partir de `None`.
4. Solo después decidir recuperación puntual de la tarea perdida y reactivación del temporizador; evitar carreras de Git y escrituras duplicadas.
5. Continuar evaluación de Tordo como alternativa B **aislada de producción**.

## 6. Comandos de diagnóstico (solo lectura)

```bash
systemctl --user cat mercadopublico-conciliacion.timer mercadopublico-conciliacion.service
systemctl --user list-timers --all --no-pager | grep -E 'mercadopublico|NEXT'
systemctl --user is-active mercadopublico-conciliacion.timer
journalctl --user -u mercadopublico-conciliacion.service --since '2026-11-10 08:00:00' --no-pager -n 80
```

**No registrar ni subir credenciales, tokens o contenido de archivos de servicio Google.**
