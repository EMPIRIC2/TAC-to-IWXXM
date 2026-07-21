#!/usr/bin/env bash
# T6.6 mock BYOC smoke (S019 / EV-014) — no live destination credentials.
# Uses gitignored .env mock placeholders + committed fixtures + unit/mocks.
# Optional: when Docker is available, also runs wis2box harness + Testcontainers.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source <(python3 - <<'PY'
from pathlib import Path
for line in Path(".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        print(f"export {k}={v!r}")
PY
)
  set +a
fi

export DISSEMINATION_EGRESS_ALLOWLIST="${DISSEMINATION_EGRESS_ALLOWLIST:-wis2box,127.0.0.1,127.0.0.0/8,localhost}"

echo "==> Mock BYOC unit suite (SQLite stand-in + WIS2 mocks + EDIS mocks + API)"
uv run pytest \
  packages/dissemination/tests/test_mock_byoc_close_gate.py \
  packages/dissemination/tests/test_wis2_sink.py \
  packages/dissemination/tests/test_wis2_transports.py \
  packages/dissemination/tests/test_edis_format.py \
  packages/dissemination/tests/test_edis_preflight.py \
  packages/dissemination/tests/test_f19_staging_path.py \
  packages/dissemination/tests/test_f19_sink_stubs.py \
  packages/dissemination/tests/test_db_preflight_handles.py \
  packages/dissemination/tests/test_writer_contract.py \
  packages/dissemination/tests/test_allowlist.py \
  apps/backend/tests/unit/test_dissemination_api.py \
  -v --tb=short --no-cov

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  echo "==> Docker available — wis2box harness + integration (Testcontainers)"
  bash scripts/ci/run_wis2box_harness.sh || true
  uv run pytest packages/dissemination/tests -m integration -v --tb=short --no-cov
else
  echo "==> Docker unavailable — skipped Compose wis2box / Testcontainers PG+MySQL"
  echo "    (SQLite stand-in + transport mocks already covered above)"
fi

echo "==> Mock BYOC smoke PASS"
