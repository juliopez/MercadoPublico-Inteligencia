#!/usr/bin/env bash
# Instala la version automatica del timer existente SIN ejecutar el cierre.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[[ -x .venv/bin/python ]] || { echo "BLOQUEADO: falta .venv"; exit 1; }
[[ -r "${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}" ]] || {
  echo "BLOQUEADO: faltan credenciales privadas locales de Google"; exit 1;
}
command -v gh >/dev/null
gh auth status >/dev/null
bash -n scripts/ubuntu_preparar_conciliacion_persistente.sh
.venv/bin/python -m py_compile scripts/cierre_mensual_automatico.py scripts/publicar_cierre_historico_v2.py scripts/exportar_mer_historico_conciliado_v2.py
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo "BLOQUEADO: cambios locales rastreados"; exit 1; }
mkdir -p "$HOME/.config/systemd/user"
cp deploy/systemd/mercadopublico-conciliacion.service "$HOME/.config/systemd/user/"
cp deploy/systemd/mercadopublico-conciliacion.timer "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now mercadopublico-conciliacion.timer
systemctl --user is-enabled mercadopublico-conciliacion.timer
systemctl --user is-active mercadopublico-conciliacion.timer
systemctl --user list-timers --all | grep mercadopublico-conciliacion
echo "TIMER_CIERRE_AUTOMATICO_INSTALADO: no se ha ejecutado una consolidacion real"
