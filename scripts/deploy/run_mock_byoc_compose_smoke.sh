#!/usr/bin/env bash
# Preflight smoke against docker-compose.mock-byoc.yml destinations (local API or package engines).
# Requires: make compose-mock-byoc-up (and optionally compose-wis2box-up).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export DISSEMINATION_EGRESS_ALLOWLIST="${DISSEMINATION_EGRESS_ALLOWLIST:-wis2box,127.0.0.1,127.0.0.0/8,localhost}"

FIXTURES="$ROOT/docs/sessions/S019-dissemination-upload/fixtures/mock-byoc-destinations.json"
CANDIDATES="$ROOT/docs/sessions/S019-dissemination-upload/fixtures/byoc-test-candidates"

echo "==> Waiting for mock BYOC ports"
python3 - <<'PY'
import socket, time, sys
ports = [25432, 13306, 11025]
deadline = time.time() + 90
pending = set(ports)
while pending and time.time() < deadline:
    done = set()
    for p in pending:
        s = socket.socket()
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", p))
            done.add(p)
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
print("ports ready:", ports)
PY

echo "==> Package-level DB preflight against compose Postgres + MySQL"
uv run python - <<'PY'
import asyncio
import json
from pathlib import Path

from dissemination.db_preflight import run_db_preflight
from dissemination.models import PreflightRequest

fixtures = json.loads(
    Path("docs/sessions/S019-dissemination-upload/fixtures/mock-byoc-destinations.json").read_text()
)


async def main() -> None:
    for key in ("postgres_compose", "mysql_compose"):
        row = fixtures[key]
        resp = await run_db_preflight(
            PreflightRequest(
                sink_type=row["sink_type"],
                uri=row["uri"],
                ddl=bool(row.get("ddl")),
                product=row.get("product") or "metar",
            )
        )
        assert resp.ok and resp.connectivity_ok, (key, resp)
        print(f"OK {key} handle={resp.handle}")


asyncio.run(main())
PY

echo "==> Candidate payloads present"
test -f "$CANDIDATES/sample-metar.tac"
test -f "$CANDIDATES/sample-metar.iwxxm.xml"
test -f "$FIXTURES"

echo "==> Mock BYOC compose smoke PASS"
