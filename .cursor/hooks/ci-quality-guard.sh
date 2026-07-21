#!/usr/bin/env bash
# Cursor beforeShellExecution hook: block git commit/push when local CI gates would fail.
# pre-commit → make validate-fast pieces; pre-push → make validate-ci (see .pre-commit-config.yaml).
set -euo pipefail

payload="$(cat)"
command_line="$(
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('command') or d.get('commandLine') or '')" <<<"$payload"
)"

if [[ -z "$command_line" ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

# Only gate git commit / push (not amend-only status checks).
if ! [[ "$command_line" =~ git[[:space:]]+(commit|push) ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

# Allow bypass only when user explicitly passes --no-verify (they accept CI risk).
if [[ "$command_line" =~ (--no-verify|-n) ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

failures=()
detail=""

run_check() {
  local label="$1"
  shift
  local out
  out="$(mktemp)"
  if ! "$@" >"$out" 2>&1; then
    failures+=("$label")
    detail="${detail}

${label}:
$(head -40 "$out")"
  fi
  rm -f "$out"
}

if ! command -v uv >/dev/null 2>&1 || [[ ! -f pyproject.toml ]]; then
  failures+=("Python: uv not available — run 'make install' before commit")
else
  # Match Makefile validate-fast / CI validate job entry points.
  if [[ "$command_line" =~ git[[:space:]]+push ]]; then
    run_check "make validate-ci" make validate-ci
  else
    run_check "make format-check" make format-check
    run_check "make lint" make lint
    run_check "make typecheck" make typecheck
    run_check "make secrets-check" make secrets-check
    run_check "make validate-yaml" make validate-yaml
    run_check "make catalog-check" make catalog-check
    run_check "make issue-registry-guard" make issue-registry-guard
  fi
fi

if [[ ${#failures[@]} -eq 0 ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

if [[ "$command_line" =~ git[[:space:]]+push ]]; then
  summary="CI validate gates would fail on push. Run 'make validate-ci' (and 'make ci-prepush' before push) before retrying."
else
  summary="CI Quality Gates would fail on commit. Run 'make validate-fast' (or 'make format' to fix) before commit."
fi

agent_msg="${summary}

Failed checks:
$(printf '  - %s\n' "${failures[@]}")${detail}"

python3 -c "
import json, sys
print(json.dumps({
    'permission': 'deny',
    'user_message': sys.argv[1],
    'agent_message': sys.argv[2],
}))
" "$summary" "$agent_msg"

exit 0
