#!/usr/bin/env bash
# Verify ALL dissemination drawer sinks against local mock BYOC environments.
# Requires: make compose-mock-byoc-all-up
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export DISSEMINATION_EGRESS_ALLOWLIST="${DISSEMINATION_EGRESS_ALLOWLIST:-wis2box,127.0.0.1,127.0.0.0/8,localhost}"

echo "==> Waiting for mock destination ports"
python3 - <<'PY'
import socket, time, sys
ports = {
    "postgres": 25432,
    "mysql": 13306,
    "sqlserver": 11433,
    "mailhog": 11025,
    "f19": 19099,
    "wis2_http": 9080,
    "wis2_mqtt": 1883,
}
deadline = time.time() + 180
pending = set(ports)
while pending and time.time() < deadline:
    done = set()
    for name in pending:
        p = ports[name]
        s = socket.socket()
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", p))
            done.add(name)
        except OSError:
            pass
        finally:
            s.close()
    pending -= done
    if pending:
        time.sleep(1)
if pending:
    print("ports not ready:", sorted(pending), file=sys.stderr)
    sys.exit(1)
print("ports ready:", ", ".join(f"{k}={v}" for k, v in sorted(ports.items(), key=lambda x: x[1])))
PY

echo "==> All-sinks verification"
uv run python scripts/deploy/verify_mock_byoc_all_sinks.py
echo "==> Mock BYOC all-sinks PASS"
