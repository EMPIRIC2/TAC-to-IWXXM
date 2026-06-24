#!/usr/bin/env bash
# Copy environment config into the static frontend build and inject publishable key.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG_ENV="${METAR_CONFIG_ENV:-prod}"
SRC="$ROOT/config/${CONFIG_ENV}.json"
DEST_DIR="${DEST_DIR:-$ROOT/apps/frontend/public}"
DEST="$DEST_DIR/config.json"

[[ -f "$SRC" ]] || { echo "Missing $SRC" >&2; exit 1; }
mkdir -p "$DEST_DIR"

python3 - <<'PY' "$SRC" "$DEST" "${SUPABASE_PUBLISHABLE_KEY:-${SUPABASE_ANON_KEY:-}}"
import json, os, sys
src, dest, publishable = sys.argv[1], sys.argv[2], sys.argv[3]
with open(src, encoding="utf-8") as f:
    cfg = json.load(f)
if publishable:
    cfg.setdefault("supabase", {})["publishableKey"] = publishable
with open(dest, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
print(f"Wrote {dest}")
PY
