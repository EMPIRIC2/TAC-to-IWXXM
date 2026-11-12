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

context="[pr-checklist] Before push: (1) make format-check green (CI Quality Gates: ruff format apps packages tests + pnpm format:check), (2) lint + typecheck + full test suite green, (3) atomic commit with [T{id}] prefix, (4) after push watch ci-cd.yml per ci-after-push.mdc (gh run watch)."

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.argv[1]}))" "$context"
exit 0
