#!/usr/bin/env bash
# Cursor afterShellExecution hook: remind to sync execution plan after test runs (advisory).
set -euo pipefail

payload="$(cat)"
command_line="$(
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('command') or d.get('commandLine') or '')" <<<"$payload"
)"

if [[ -z "$command_line" ]]; then
  echo '{}'
  exit 0
fi

if ! [[ "$command_line" =~ (pytest|make test|pnpm test|vitest|npm test) ]]; then
  echo '{}'
  exit 0
fi

context="[post-test-sync] Tests ran. If completing a build task, mark it completed in .cursor/artifacts/execution-plan-monorepo.md only after lint, typecheck, and full suite pass (build-execution.mdc)."

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.argv[1]}))" "$context"
exit 0
