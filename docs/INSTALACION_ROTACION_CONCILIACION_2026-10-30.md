# Instalación única en Ubuntu — rotación MER y conciliación diferida

**Estado (30/10/2026):** código subido a `main`; servicios y timers NO instalados en Ubuntu desde esta sesión. No se modificó el cron productivo de las 16:00 ni se movieron archivos reales de Drive.

## Contrato operativo
- Diario **16:00**: cron Ubuntu existente, intacto, escribe en el MER del mes calculado por fecha de Santiago.
- Último día hábil chileno, **19:00**: `mercadopublico-rotacion.timer` → `scripts/ubuntu_rotacion_mensual.sh` → `scripts/rotar_mes_operativo.py`. Comprueba estado exitoso de ETL 16:00, seis tablas del archivo actual, destino siguiente vacío; crea el destino si falta usando credenciales y permisos de Drive; mueve el archivo anterior conservando ID; actualiza catálogo GitHub. Emplea candado MER. Si no hay permisos/credenciales o falta el ETL validado, bloquea y deja constancia en journal (NO declara éxito).
- Desde **día 10 o hábil siguiente**, revisión diaria y en arranque de Ubuntu: `mercadopublico-conciliacion.timer` prepara tres ZIP históricos con hash. **No ejecuta automáticamente la conciliación definitiva** ni escribe resultados a históricos; se requiere contraste y aprobación. Las fuentes pueden no estar disponibles el día 10.
- Feriados: `config/feriados_chile_conciliacion.json`; año 2026 cargado; **es obligatorio cargar y validar 2027 y siguientes** antes de diciembre de cada año para garantizar rotación futura. No se presumen feriados regionales.
- Estado de rotación: `~/.local/share/mercadopublico/rotaciones/AAAA-MM.json`. Estado preparación: `~/.local/share/mercadopublico/cierres/AAAA-MM`.
- IMPORTANTE: el cierre del día 10 debe permitir trabajar con octubre ya archivado. El script de cierre supervisado acepta ahora tipo `historico` para preflight; sólo se aplica tras diagnóstico y aprobación.

## Instalación después de git pull
```bash
cd "$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia"
git pull --ff-only origin main
bash -n scripts/ubuntu_rotacion_mensual.sh
bash -n scripts/ubuntu_preparar_conciliacion_persistente.sh
.venv/bin/python -m py_compile scripts/rotar_mes_operativo.py scripts/orquestar_cierre_mensual.py
.venv/bin/python scripts/rotar_mes_operativo.py
.venv/bin/python scripts/verificar_ventana_conciliacion.py --fecha 2026-11-10
gh auth status
```

Para instalar ambos temporizadores de usuario (revisar ruta local primero):
```bash
mkdir -p "$HOME/.config/systemd/user"
cp deploy/systemd/mercadopublico-{rotacion,conciliacion}.{service,timer} "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now mercadopublico-rotacion.timer mercadopublico-conciliacion.timer
systemctl --user list-timers
```

Si Ubuntu no conserva una sesión de usuario, configurar linger conscientemente para servicio de usuario con el equipo encendido. `Persistent=true` recupera eventos perdidos en un apagado, **y el script permite recuperar la rotación en el primer día hábil siguiente, antes de las 16:00**, siempre que exista constancia del ETL exitoso del último día hábil. Si el equipo vuelve a encenderse después de esa ventana, el proceso bloquea la rotación automática y requiere intervención supervisada. No confundir con la recuperación de conciliación, que sí permite días posteriores al 10.

## Verificación y limitaciones reales
- `journalctl --user -u mercadopublico-rotacion.service -n 100 --no-pager`
- `journalctl --user -u mercadopublico-conciliacion.service -n 100 --no-pager`
- `git pull --ff-only origin main` antes de correr preparación de cierre diferido si cambió catálogo remoto.
- `gh auth status` debe autorizar escritura de contenidos en GitHub; Drive debe permitir creación/movimiento. Servicio de Google con permiso `writer` sobre Sheets **no garantiza** capacidad de mover a carpetas de otro propietario ni crear hojas por su cuota. Cualquier rechazo detiene la rotación sin atribuirle éxito.
- Noviembre **ya existe y tiene seis encabezados verificados**; la rotación octubre→noviembre lo reutiliza y no genera duplicados.
- Para confirmar operatividad real se requiere instalación, ejecutar en Ubuntu las verificaciones y comprobar logs. Las pruebas GitHub CI son sólo sintaxis/calendario; no comprueban Google Drive real.
