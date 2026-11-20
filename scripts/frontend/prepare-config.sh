#!/usr/bin/env sh
# Copy environment config into the static frontend build and inject publishable key.
# Ensures api.baseUrl + Auth bootstrap (supabase.url + publishableKey) for F31.
# POSIX sh — Alpine Compose frontend has no bash unless explicitly installed.
set -eu

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONFIG_ENV="${METAR_CONFIG_ENV:-prod}"
SRC="${CONFIG_SRC:-$ROOT/config/deploy/profiles/${CONFIG_ENV}.json}"
DEST_DIR="${DEST_DIR:-$ROOT/apps/frontend/public}"
DEST="$DEST_DIR/config.json"

[ -f "$SRC" ] || { echo "Missing $SRC" >&2; exit 1; }
mkdir -p "$DEST_DIR"

python3 - <<'PY' "$SRC" "$DEST" "${SUPABASE_PUBLISHABLE_KEY:-${SUPABASE_ANON_KEY:-}}" "$CONFIG_ENV"
import json, sys

src, dest, publishable, config_env = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(src, encoding="utf-8") as f:
    cfg = json.load(f)

api = cfg.get("api")
if not isinstance(api, dict) or not str(api.get("baseUrl") or "").strip():
    raise SystemExit(f"config missing api.baseUrl: {src}")

supabase = cfg.setdefault("supabase", {})
if not isinstance(supabase, dict) or not str(supabase.get("url") or "").strip():
    raise SystemExit(f"config missing supabase.url (Auth bootstrap): {src}")

if publishable:
    supabase["publishableKey"] = publishable
elif not str(supabase.get("publishableKey") or "").strip():
    # Prod/staging must ship Auth bootstrap (F31). Local/e2e may omit until .env
    # is loaded; FE merges bake-time Vite env when /config.json omits the key.
    if config_env in ("prod", "staging"):
        raise SystemExit(
            "config missing supabase.publishableKey — set SUPABASE_PUBLISHABLE_KEY "
            f"(or SUPABASE_ANON_KEY) before prepare-config ({config_env})"
        )

with open(dest, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
print(f"Wrote {dest}")
PY
