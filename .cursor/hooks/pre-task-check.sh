#!/usr/bin/env bash
# Cursor preToolUse hook: remind agent to read spec source before Write (advisory).
set -euo pipefail

payload="$(cat)"
file_path="$(
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('filePath') or d.get('file_path') or '')" <<<"$payload"
)"

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
plan="$repo_root/.cursor/artifacts/execution-plan-monorepo.md"

if [[ ! -f "$plan" ]]; then
  echo '{}'
  exit 0
fi

context="[pre-task-check] Before implementing, read the task Spec Source column in .cursor/artifacts/execution-plan-monorepo.md and set the task to in_progress."

if [[ -n "$file_path" ]]; then
  rel="${file_path#"$repo_root"/}"
  rel="${rel#/}"
  case "$rel" in
    src/*|apps/*|packages/*|backend/*|frontend/*|GIFTs/*|auth/*|tests/*)
      context="$context Edited path: $rel — confirm active phase/milestone in execution plan Current State table."
      ;;
  esac
fi

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.argv[1]}))" "$context"
exit 0
