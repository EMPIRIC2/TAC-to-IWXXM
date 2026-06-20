#!/usr/bin/env bash
# Cursor afterFileEdit hook: run formatter in check mode (advisory).
set -euo pipefail

payload="$(cat)"
file_path="$(
  python3 -c "import json,sys; print(json.load(sys.stdin).get('filePath',''))" <<<"$payload"
)"

if [[ -z "$file_path" ]]; then
  echo '{}'
  exit 0
fi

repo_root="$(git -C "$(dirname "$file_path")" rev-parse --show-toplevel 2>/dev/null || pwd)"
rel="${file_path#"$repo_root"/}"
rel="${rel#/}"

run_ruff_format() {
  local target="$1"
  if command -v uv >/dev/null 2>&1 && [[ -f "$repo_root/pyproject.toml" ]]; then
    (cd "$repo_root" && uv run ruff format --check --diff "$target" 2>&1) || true
  elif command -v ruff >/dev/null 2>&1; then
    ruff format --check --diff "$target" 2>&1 || true
  else
    echo "[format] ruff not installed — run 'make install' or 'uv sync' at repo root."
  fi
}

output=""
case "$rel" in
  *.py)
    output="$(run_ruff_format "$file_path")"
    ;;
esac

if [[ -z "$output" ]]; then
  echo '{}'
  exit 0
fi

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.stdin.read()}))" <<<"$output"
exit 0
