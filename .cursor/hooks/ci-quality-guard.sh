#!/usr/bin/env bash
# Cursor beforeShellExecution hook: block git commit/push when CI Quality Gates would fail.
# Matches ci-cd.yml job "quality-gates" (ruff format --check apps packages tests + pnpm format:check).
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

if command -v uv >/dev/null 2>&1 && [[ -f pyproject.toml ]]; then
  if ! uv run ruff format --check apps packages tests >/tmp/ci-quality-guard-ruff.out 2>&1; then
    failures+=("Python: uv run ruff format --check apps packages tests")
    ruff_out="$(head -20 /tmp/ci-quality-guard-ruff.out)"
  fi
else
  failures+=("Python: uv not available — run 'make install' before commit")
fi

if command -v pnpm >/dev/null 2>&1 && [[ -f package.json ]]; then
  if ! pnpm run format:check >/tmp/ci-quality-guard-pnpm.out 2>&1; then
    failures+=("JS/TS: pnpm run format:check")
    pnpm_out="$(head -20 /tmp/ci-quality-guard-pnpm.out)"
  fi
fi

if [[ ${#failures[@]} -eq 0 ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

summary="CI Quality Gates would fail on push to main. Run 'make format-check' (or 'make format' to fix) before commit/push."
detail=""
[[ -n "${ruff_out:-}" ]] && detail="${detail}

Ruff:
${ruff_out}"
[[ -n "${pnpm_out:-}" ]] && detail="${detail}

Prettier:
${pnpm_out}"

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
