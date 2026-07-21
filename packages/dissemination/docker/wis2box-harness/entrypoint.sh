#!/usr/bin/env bash
# Start MQTT broker + HTTP dataset store for the F17 wis2box Compose harness.
set -euo pipefail

STORAGE="${WIS2BOX_DATASET_DIR:-/var/lib/wis2box-harness/datasets}"
HTTP_PORT="${WIS2BOX_HTTP_PORT:-8080}"
mkdir -p "${STORAGE}"

mosquitto -c /etc/mosquitto/mosquitto.conf &
MQTT_PID=$!

python3 /opt/wis2box-harness/dataset_server.py \
  --host 0.0.0.0 \
  --port "${HTTP_PORT}" \
  --storage "${STORAGE}" &
HTTP_PID=$!

cleanup() {
  kill "${MQTT_PID}" "${HTTP_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Fail the container if either child exits.
while kill -0 "${MQTT_PID}" 2>/dev/null && kill -0 "${HTTP_PID}" 2>/dev/null; do
  sleep 2
done
echo "[wis2box-harness] child process exited unexpectedly" >&2
exit 1
