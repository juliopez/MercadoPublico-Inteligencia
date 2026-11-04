#!/usr/bin/env bash
# Instala un timer de USUARIO para disparar GitHub Actions a las 22:05 hora Chile.
# No toca crontab ni los timers existentes del Observatorio.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
NAME="mercadopublico-api-github-dispatch"
MODE="${1:---verificar}"
[[ "$MODE" == --verificar || "$MODE" == --instalar ]] || {
  echo "Uso: bash scripts/instalar_disparador_api_github_ubuntu.sh --verificar|--instalar" >&2
  exit 2
}
command -v systemctl >/dev/null || { echo "FALTA_SYSTEMD"; exit 1; }
command -v gh >/dev/null || { echo "FALTA_GH: instalar gh y autenticar con actions:write"; exit 1; }
python3 -m py_compile "$ROOT/scripts/ubuntu_disparar_api_actions.py"
if [[ "$MODE" == --verificar ]]; then
  python3 "$ROOT/scripts/ubuntu_disparar_api_actions.py" --verificar
  systemctl --user list-timers --all --no-pager 2>/dev/null | grep -F "$NAME" || true
  echo "VERIFICACION_SIN_MODIFICAR_TIMERS"
  exit 0
fi
# Las rutas del repositorio pueden contener espacios (por ejemplo, "Julio Lopez").
# systemd admite comillas en los argumentos ExecStart; no usar escape de shell.
# Evitar comillas literales en el directorio, que requieren escapado adicional.
if [[ "$ROOT" == *'"'* ]]; then
  echo "Ruta con comillas no compatible: $ROOT" >&2
  exit 2
fi
mkdir -p "$UNIT_DIR"
cat >"$UNIT_DIR/$NAME.service" <<UNIT
[Unit]
Description=Solicitar ejecución nocturna API Compra Agil desde Ubuntu a GitHub Actions
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 "$ROOT/scripts/ubuntu_disparar_api_actions.py" --ejecutar
TimeoutStartSec=180
UNIT
cat >"$UNIT_DIR/$NAME.timer" <<UNIT
[Unit]
Description=Disparar GitHub Actions Compra Agil a las 22:05 de Santiago (lun-vie)

[Timer]
OnCalendar=Mon..Fri *-*-* 22:05:00 America/Santiago
Persistent=true
Unit=$NAME.service

[Install]
WantedBy=timers.target
UNIT
systemctl --user daemon-reload
systemctl --user enable --now "$NAME.timer"
systemctl --user status "$NAME.timer" --no-pager || true
systemctl --user list-timers --all --no-pager | grep -F "$NAME" || true
echo "TIMER_USUARIO_INSTALADO: $NAME.timer"
echo "IMPORTANTE: sin sesión de usuario, habilitar linger una vez: sudo loginctl enable-linger $(id -un)"
echo "SIN_CAMBIOS_AL_CRON_1600"
\\n'* ]] || {
  echo "Ruta con comillas o saltos de línea no compatible: $ROOT" >&2
  exit 2
}
mkdir -p "$UNIT_DIR"
cat >"$UNIT_DIR/$NAME.service" <<UNIT
[Unit]
Description=Solicitar ejecución nocturna API Compra Agil desde Ubuntu a GitHub Actions
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 $ROOT/scripts/ubuntu_disparar_api_actions.py --ejecutar
TimeoutStartSec=180
UNIT
cat >"$UNIT_DIR/$NAME.timer" <<UNIT
[Unit]
Description=Disparar GitHub Actions Compra Agil a las 22:05 de Santiago (lun-vie)

[Timer]
OnCalendar=Mon..Fri *-*-* 22:05:00 America/Santiago
Persistent=true
Unit=$NAME.service

[Install]
WantedBy=timers.target
UNIT
systemctl --user daemon-reload
systemctl --user enable --now "$NAME.timer"
systemctl --user status "$NAME.timer" --no-pager || true
systemctl --user list-timers --all --no-pager | grep -F "$NAME" || true
echo "TIMER_USUARIO_INSTALADO: $NAME.timer"
echo "IMPORTANTE: sin sesión de usuario, habilitar linger una vez: sudo loginctl enable-linger $(id -un)"
echo "SIN_CAMBIOS_AL_CRON_1600"
