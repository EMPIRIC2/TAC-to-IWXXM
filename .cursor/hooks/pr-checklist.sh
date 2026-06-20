#!/usr/bin/env bash
# Cursor preToolUse hook: PR/push checklist reminder (advisory).
set -euo pipefail

payload="$(cat)"
command_line="$(
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('command') or d.get('commandLine') or '')" <<<"$payload"
)"

if [[ -z "$command_line" ]]; then
  echo '{}'
  exit 0
fi

if ! [[ "$command_line" =~ git[[:space:]]+push ]]; then
  echo '{}'
  exit 0
fi

context="[pr-checklist] Before push: (1) lint + typecheck + full test suite green, (2) atomic commit with [T{id}] prefix, (3) milestone tasks completed in execution plan, (4) after push run bash scripts/ci/watch_github_ci.sh per ci-after-push.mdc."

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.argv[1]}))" "$context"
exit 0
