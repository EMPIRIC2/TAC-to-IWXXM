#!/usr/bin/env bash
# sessionEnd — sync git/corpus + record session (F71). Fail-open.
set -euo pipefail

input=$(cat)
MH="${MH:-$HOME/.cursor/skills/bin/memory-hook}"
if [[ ! -x "$MH" ]]; then
  MH=".cursor/bin/memory-hook"
fi
ROOT="${CURSOR_PROJECT_DIR:-${PWD}}"

CONV=$(printf '%s' "$input" | python3 -c '
import hashlib
import json
import sys

raw = sys.stdin.read()
data = json.loads(raw) if raw.strip() else {}
for key in ("conversation_id", "conversationId", "session_id", "sessionId"):
    val = data.get(key)
    if isinstance(val, str) and val.strip():
        print(val.strip())
        raise SystemExit(0)
print(hashlib.sha256(raw.encode("utf-8") if raw else b"").hexdigest()[:16])
')

exec "$MH" cursor-session-end --conversation-id "$CONV" --workspace-root "$ROOT"
