# Incidente y recuperación supervisada — cierre histórico 2026-10

**Fecha de operación:** 2026-11-10, America/Santiago. **Fuente:** capturas de terminal Ubuntu aportadas por el responsable durante la sesión. **Alcance:** P4, publicación histórica y temporizador systemd. No contiene credenciales.

## Resumen ejecutivo

El cierre mensual de octubre fue preparado y cargado con respaldo verificado, pero una ejecución automática de publicación terminó con error al intentar `git push origin main` mientras la rama remota avanzaba por otros procesos. Se completó una publicación manual supervisada y se comprobó GitHub Pages. Posteriormente se recuperó el estado de cierre local **sin repetir carga MER ni publicación**. La puerta de calendario devolvió `COMPLETADO` y `accion: NINGUNA`.

**Actualización posterior:** prueba del temporizador a las 10:15 confirmada por captura de `journalctl` aportada por el responsable. Inicio y finalización a las 10:15:54 Chile; puerta `COMPLETADO` / `NINGUNA`.

## Secuencia observada

1. Servicio `mercadopublico-conciliacion.service` falló a las **09:31:33** tras ~1 h 11 min de ejecución. El registro identificó `subprocess.CalledProcessError` en `scripts/publicar_cierre_historico_v2.py`, por `git push origin main` rechazado; no se debe interpretar como error de carga MER.
2. Repositorio local tenía cambios de datos e índices y divergencia con `origin/main`; se creó la rama de resguardo `respaldo-conciliacion-20261110`. Se informó ausencia de archivos modificados simultáneamente entre ambas ramas (comparación de nombres), lo que **no** equivale a una prueba general de integridad de contenido.
3. Se publicó el histórico mediante `.venv/bin/python scripts/publicar_cierre_historico_v2.py --periodo 2026-10` con `GOOGLE_APPLICATION_CREDENTIALS` apuntando al archivo local habitual. La salida mostró `EXPORTACION_V2_VERIFICADA`, generación de índices, push a `main` y `PAGES_HISTORICO_VERIFICADO`; commit de publicación **`77df3d30d`**. Conteos declarados: **91.925 procesos, 470.841 ofertas, 56.813 resultados y 167.042 órdenes de compra** para 2026-10. Son conteos de exportación del histórico, no cifras del mes operativo aislado.
4. La constancia local `constancia_carga_real.json` declaró `CARGA_VERIFICADA`, período `2026-10`, seis tablas, respaldo ZIP y SHA256. Se comprobó existencia del ZIP, tamaño **5.735.999 bytes** y coincidencia efectiva del SHA256. El estado de cierre seguía en `LISTO_PARA_CONCILIAR` pese a la publicación verificada.
5. Se ejecutó recuperación supervisada con comprobaciones previas de identidad MER, catálogo histórico, seis tablas, respaldo SHA256, informe oficial y catálogo servido por Pages. Se preservó copia de `estado_cierre.json` en `estado_cierre.antes_recuperacion.json` y se escribió `CONCILIACION_HISTORICA_VERIFICADA`, `recuperacion_supervisada: true`, `cierre_automatico: false`. La puerta `scripts/verificar_ventana_conciliacion.py --fecha 2026-11-10` respondió `COMPLETADO`, `accion: NINGUNA`.
6. Se cambió localmente `~/.config/systemd/user/mercadopublico-conciliacion.timer` de `OnCalendar=*-*-* 10:00:00` a **`OnCalendar=*-*-* 10:15:00`**; se recargó systemd y se habilitó el timer. `list-timers` mostró siguiente disparo **2026-11-10 10:15:00 -03**. La ejecución observada a **10:06:06** terminó `status=0/SUCCESS` con `COMPLETADO`/`NINGUNA`. **Validado posteriormente:** ejecución automática a las 10:15:54, con resultado `COMPLETADO` / `NINGUNA`.
7. La captura de `systemctl --user cat` mostró `Persistent=true`, `OnBootSec=10min`, `TimeoutStartSec=6h`; el temporizador se había detenido durante la recuperación y fue reactivado después.

## Diagnóstico y solución

- **Fallo confirmado:** conflicto de publicación Git al hacer push en un repositorio con actualizaciones concurrentes; estado de cierre local no quedó finalizado pese a publicación exitosa posterior.
- **Solución aplicada:** resguardo de rama, conciliación de cambios Git, publicación histórica verificada, recuperación del marcador local **sin nueva carga ni nuevo push**, reactivación del timer.
- **No confundir:** `COMPLETADO` demuestra que la puerta no debe reejecutar octubre; no demuestra por sí solo que un cierre mensual futuro se complete sin supervisión.
- **Credenciales:** el primer intento manual falló por ausencia de `GOOGLE_APPLICATION_CREDENTIALS` en la sesión de terminal; la credencial existía en la ruta local habitual y el intento posterior la utilizó. No publicar contenido de credenciales.

## Comprobación de las 10:15 (confirmada)

```bash
journalctl --user -u mercadopublico-conciliacion.service --since "2026-11-10 10:14:00" --no-pager
systemctl --user list-timers --all --no-pager | grep mercadopublico-conciliacion
```

**Evidencia aportada:** `nov 10 10:15:54` inicio del servicio; salida JSON `{ "estado": "COMPLETADO", "fecha": "2026-11-10", "habil_desde": "2026-11-10", "periodo": "2026-10", "accion": "NINGUNA" }`; `nov 10 10:15:54` finalización del servicio. Se acredita disparo automático y ausencia de nueva carga; el próximo disparo del 11/11 aún no se ha comprobado mediante `list-timers`.

## Riesgos y mejoras pendientes

- El horario **10:15** fue cambiado en systemd **local**, no se ha comprobado su persistencia en instaladores o plantillas versionadas. Comparar con `deploy/systemd/` y runbooks antes de reinstalar.
- `scripts/ubuntu_preparar_conciliacion_persistente.sh` utiliza `flock -n` y sale con código 0 cuando MER está ocupado; verificar que haya una próxima oportunidad de reintento y que no se confunda con conciliación completada.
- Revisar manejo de `git push` concurrente y checkpoints de publicación para evitar recuperación manual; cualquier modificación productiva requiere autorización.
- No borrar el respaldo, constancias ni rama de recuperación hasta finalizar auditoría.
- Actualizar documentación de P4 y registrar cada ejecución futura con fecha, disparador, duración, registros, errores, respaldo, commit Pages y estado final.

## Procesos relacionados (no equivalentes)

- P1: ETL ZIP licitaciones/OC, Ubuntu lun-vie 16:00.
- P2: Compra Ágil nocturna 22:05, GitHub Actions, lotes 400.
- P3: rotación de mes, timer 19:00 con puerta de último día hábil.
- P4: cierre oficial del mes vencido, timer diario **10:15** y puerta día 10 o hábil siguiente; evita repetir un mes completado.
- P7: conciliación cronológica de registros por fecha propia, cron lun-vie 09:00; distinta de P4.
- Recuperación API licitaciones 16:15, cron separado, primera ejecución por auditar.

**Estado del incidente:** recuperación y publicación de octubre **verificadas**; **prueba de disparo automático 10:15 superada**; prevención definitiva de concurrencia Git pendiente de diseño y autorización.
