#!/usr/bin/env bash
# workspaceOpen — bootstrap Neo4j + engineering-memory health (F71). Fail-open.
set -euo pipefail

MH="${MH:-$HOME/.cursor/skills/bin/memory-hook}"
if [[ ! -x "$MH" ]]; then
  MH=".cursor/bin/memory-hook"
fi
ROOT="${CURSOR_PROJECT_DIR:-${PWD}}"
exec "$MH" bootstrap --workspace-root "$ROOT"
