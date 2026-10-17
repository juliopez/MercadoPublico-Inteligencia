#!/usr/bin/env bash
# Prueba controlada: una sola petición HTTP a Compra Ágil V2 con curl.
set -euo pipefail
: "${CHILECOMPRA_TICKET:?Primero exporta CHILECOMPRA_TICKET}"
command -v curl >/dev/null || { echo "Instala curl antes de continuar"; exit 1; }
CODE="425-339-COT26"
OUT="diagnostico_curl_v2"
mkdir -p "$OUT"
# Evitar que secretos aparezcan en xtrace.
set +x
umask 077
HEADER_FILE="$(mktemp)"
trap 'rm -f "$HEADER_FILE"' EXIT
printf 'ticket: %s\nAccept: application/json\n' "$CHILECOMPRA_TICKET" > "$HEADER_FILE"
echo "Probando un único proceso: $CODE (sin imprimir credenciales)"
# --http1.1 evita introducir negociación HTTP/2 como variable en esta primera comparación.
set +e
curl --http1.1 --silent --show-error \
  --connect-timeout 10 --max-time 45 \
  --header @"$HEADER_FILE" \
  --output "$OUT/$CODE.json" \
  --write-out 'http=%{http_code} protocolo=%{http_version} dns=%{time_namelookup}s conexion=%{time_connect}s tls=%{time_appconnect}s primer_byte=%{time_starttransfer}s total=%{time_total}s bytes=%{size_download}\n' \
  "https://api2.mercadopublico.cl/v2/compra-agil/$CODE"
exit_code=$?
set -e
echo "curl_exit=$exit_code"
if [[ "$exit_code" -ne 0 ]]; then
  echo "La petición no terminó correctamente. No se analizará el cuerpo."
elif python3 - "$OUT/$CODE.json" <<'PY'
import json,sys
try:
    with open(sys.argv[1],encoding="utf-8") as f:
        data=json.load(f)
    print("json_valido=si tipo_raiz="+type(data).__name__)
except (ValueError,OSError,UnicodeError) as exc:
    print("json_valido=no error="+type(exc).__name__)
    sys.exit(1)
PY
then
  echo "Respuesta JSON conservada localmente en $OUT/$CODE.json"
else
  echo "No se confirmó JSON válido; revisa el código HTTP antes de utilizar el archivo."
fi
echo "No subas el cuerpo descargado ni el ticket a un repositorio público."
