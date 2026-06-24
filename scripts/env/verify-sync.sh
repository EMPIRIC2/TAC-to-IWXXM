#!/usr/bin/env bash
# Validate canonical env names + config JSON (local/Render parity gate).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

LIVE="${LIVE:-0}"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"
CONFIG_ENV="${METAR_CONFIG_ENV:-local}"

warn() { echo "WARN: $*" >&2; }
fail() { echo "ERROR: $*" >&2; exit 1; }

# --- config JSON ---
CONFIG_PATH="$ROOT/config/${CONFIG_ENV}.json"
[[ -f "$CONFIG_PATH" ]] || fail "Missing config file: $CONFIG_PATH"

python3 - <<'PY' "$CONFIG_PATH"
import json, sys
path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    cfg = json.load(f)
for key in ("environment", "api", "supabase"):
    if key not in cfg:
        raise SystemExit(f"config missing top-level key: {key}")
if not cfg["supabase"].get("url"):
    raise SystemExit("config.supabase.url is required")
if not cfg["api"].get("baseUrl"):
    raise SystemExit("config.api.baseUrl is required")
print(f"OK config: {path}")
PY

# --- optional .env (secrets) ---
if [[ -f "$ENV_FILE" ]]; then
  set -a
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%$'\r'}"
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    [[ "$line" != *=* ]] && continue
    export "$line"
  done < "$ENV_FILE"
  set +a
else
  warn "No $ENV_FILE — skipping secret presence checks"
fi

canonical_publishable="${SUPABASE_PUBLISHABLE_KEY:-}"
canonical_secret="${SUPABASE_SECRET_KEY:-}"
legacy_publishable="${SUPABASE_ANON_KEY:-}"
legacy_secret="${SUPABASE_SERVICE_ROLE_KEY:-}"

if [[ -n "$legacy_publishable" && -z "$canonical_publishable" ]]; then
  warn "SUPABASE_ANON_KEY set without SUPABASE_PUBLISHABLE_KEY — migrate to canonical name"
fi
if [[ -n "$legacy_secret" && -z "$canonical_secret" ]]; then
  warn "SUPABASE_SERVICE_ROLE_KEY set without SUPABASE_SECRET_KEY — migrate to canonical name"
fi

if [[ -f "$ENV_FILE" ]]; then
  if [[ -z "${canonical_publishable}${legacy_publishable}" ]]; then
    fail "Set SUPABASE_PUBLISHABLE_KEY in $ENV_FILE"
  fi
  if [[ -z "${canonical_secret}${legacy_secret}" ]]; then
    warn "SUPABASE_SECRET_KEY not set (required for create_admin_user.py only)"
  fi
  if [[ -z "${DATABASE_URL:-}" ]]; then
    warn "DATABASE_URL not set (required for evaluation jobs + statistics)"
  fi
fi

# --- optional live probes ---
if [[ "$LIVE" == "1" ]]; then
  API_URL="$(python3 -c "import json; print(json.load(open('$CONFIG_PATH'))['api']['baseUrl'])")"
  SB_URL="$(python3 -c "import json; print(json.load(open('$CONFIG_PATH'))['supabase']['url'])")"
  curl -fsS "$API_URL/health" >/dev/null || fail "API health check failed: $API_URL/health"
  curl -fsS "$SB_URL/auth/v1/health" >/dev/null || fail "Supabase auth health failed: $SB_URL/auth/v1/health"
  echo "OK live probes"
fi

echo "env-check passed (METAR_CONFIG_ENV=$CONFIG_ENV)"
