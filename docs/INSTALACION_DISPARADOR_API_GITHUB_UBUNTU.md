# Disparador Ubuntu → GitHub Actions para Compra Ágil

Fecha: 2026-11-04. Proceso protegido: **2, API Compra Ágil**.

## Objetivo y alcance

GitHub Actions con `schedule` puede iniciar con horas de retraso. El nuevo timer de usuario Ubuntu **solicita** una ejecución `workflow_dispatch` a las **22:05 de Chile de lunes a viernes**. GitHub sigue ejecutando la API con sus credenciales, lotes, controles y publicación existentes; el cron Ubuntu de las 16:00, sus scripts y timers de rotación/conciliación **no se modifican**.

Archivos nuevos:

- `scripts/ubuntu_disparar_api_actions.py`: CLI independiente con `--verificar` y `--ejecutar`. Consulta hasta 40 ejecuciones recientes del workflow; si alguna está activa o ya existe una ejecución de la misma jornada nocturna, omite despachar otra. Utiliza `flock` local.
- `scripts/instalar_disparador_api_github_ubuntu.sh`: instala únicamente las unidades de usuario `mercadopublico-api-github-dispatch.service` y `.timer`; no modifica `crontab`.
- `tests/test_ubuntu_disparador_api_actions.py`: pruebas de fecha, horario Chile, cambio de mes, fines de semana y prevención de duplicados.
- `.github/workflows/validar-disparador-api-ubuntu.yml`: CI de solo lectura; jamás dispara la API.

La programación previa de GitHub `schedule` **se conserva como respaldo**. `concurrency: mer-api-actions-unica` ya impide ejecuciones paralelas dentro del workflow y los checkpoints evitan repetir detalles confirmados.

## Activación ÚNICA en el Ubuntu real (necesaria)

**Los commits no instalan unidades systemd en un equipo remoto.** Efectuar una sola vez bajo el usuario habitual que tiene acceso al repositorio:

```bash
cd ~/MercadoPublico-Inteligencia
git pull --ff-only origin main
gh auth status
bash scripts/instalar_disparador_api_github_ubuntu.sh --verificar
bash scripts/instalar_disparador_api_github_ubuntu.sh --instalar
systemctl --user list-timers --all | grep mercadopublico-api-github-dispatch
```

Los requisitos son Ubuntu encendido, `python3`, `gh` GitHub CLI autenticado con permisos **Actions: write** del repositorio y `systemd --user` disponible. Si `gh auth status` falla, autenticar `gh auth login` **en el equipo**, sin poner tokens en el repositorio. Para permitir timers de usuario aun con la sesión cerrada, si corresponde habilitar una vez: `sudo loginctl enable-linger "$(id -un)"`. Si el equipo se suspende o se apaga, no hay garantía de inicio a las 22:05; `Persistent=true` habilita un intento al volver a encenderse, condicionado a la ventana chilena y a la jornada laboral. Si persiste suspensión nocturna, se requerirá un ejecutor siempre encendido.

## Comprobar una ejecución

```bash
systemctl --user status mercadopublico-api-github-dispatch.timer --no-pager
journalctl --user -u mercadopublico-api-github-dispatch.service -n 70 --no-pager
gh run list --repo juliopez/MercadoPublico-Inteligencia --workflow api-compra-agil-400-actions.yml --limit 10
```

La línea `WORKFLOW_DISPATCH_SOLICITADO` solo confirma que GitHub aceptó la solicitud; **no acredita que haya comenzado la consulta ni que se haya publicado**. Para certificar la jornada, revisar los pasos de la ejecución API, checkpoint, Google Sheets y Pages. La línea `OMITIDA_SIN_DUPLICADOS` es normal cuando el workflow ya estaba activo.

## Reversión sin afectar procesos protegidos

```bash
systemctl --user disable --now mercadopublico-api-github-dispatch.timer
rm -f ~/.config/systemd/user/mercadopublico-api-github-dispatch.timer ~/.config/systemd/user/mercadopublico-api-github-dispatch.service
systemctl --user daemon-reload
```

Esto deja el `schedule` nocturno anterior como respaldo y **no toca** el cron Ubuntu de las 16:00, el ETL, Google Sheets, los cierres ni los datos.

## Limitaciones explícitas

1. La hora solicitada por Ubuntu no obliga a GitHub a asignar inmediatamente un runner: reduce la dependencia del `schedule`, no elimina los posibles retrasos de inicio de GitHub.
2. El disparador es **una solicitud diaria**, no una cola histórica de jornadas. La recuperación de días perdidos y mayor capacidad nocturna quedan fuera del alcance aprobado para esta etapa.
3. Los workflows `schedule` y `workflow_dispatch` pueden coincidir en una noche: el disparador minimiza duplicados y los checkpoints del motor son la protección final. Verificar empíricamente convivencia la primera noche.
4. El estado real solo puede declararse `instalado` después de realizar el comando en el Ubuntu del usuario.

## Corrección de publicación parcial — 17/11/2026

Auditoría de la jornada 16/11: Actions [43992911275](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/43992911275) se canceló alrededor de las 04:06 Chile tras cuatro lotes confirmados de 400 (1.600 consultas); el quinto quedó interrumpido. El artifact `api-dia-43992911275` preservó el estado. Los pasos de exportación y Pages quedaron omitidos. La causa externa de la cancelación no quedó demostrada.

Mitigación en `.github/workflows/api-compra-agil-400-actions.yml`: el ciclo de lotes deja de iniciar nuevos lotes después de 4 horas transcurridas desde el comienzo de la etapa; se reserva tiempo del runner para exportación, derivados y Pages. Si la etapa de lotes falla, se intenta exportar igualmente desde el MER, **sin volver a consultar la API ni asumir que el último lote incompleto se guardó**. Si la exportación tiene éxito, se intenta desplegar y verificar Pages. Se preservan los checkpoints y la ventana nocturna, sin alterar el tamaño de lote (400), el intervalo de 10 s ni las pausas por 429.

**Límite:** una cancelación externa/global puede impedir ejecutar cualquier paso posterior; esta mitigación reduce ese riesgo, pero no constituye una garantía absoluta. La jornada puede quedar incompleta y debe continuar desde checkpoint en ejecuciones posteriores. Validar en Actions la ejecución de los pasos `Exportar e indexar el mes operativo` y `Desplegar y verificar Pages`, además de los conteos visibles en Pages. No reejecutar lotes solo para reparar una publicación.
