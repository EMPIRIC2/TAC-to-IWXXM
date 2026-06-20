#!/usr/bin/env bash
# Cursor afterFileEdit hook: run typechecker on edited source files (advisory).
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

run_basedpyright() {
  local target="$1"
  if command -v uv >/dev/null 2>&1 && [[ -f "$repo_root/pyproject.toml" ]]; then
    (cd "$repo_root" && uv run basedpyright "$target" 2>&1) || true
  elif command -v basedpyright >/dev/null 2>&1; then
    basedpyright "$target" 2>&1 || true
  else
    echo "[typecheck] basedpyright not installed — run 'uv sync' at repo root."
  fi
}

run_tsc() {
  local pkg_dir="$1"
  if [[ -f "$pkg_dir/tsconfig.json" ]] && command -v pnpm >/dev/null 2>&1; then
    (cd "$pkg_dir" && pnpm exec tsc --noEmit 2>&1) || true
  elif [[ -f "$pkg_dir/tsconfig.json" ]] && command -v npm >/dev/null 2>&1; then
    (cd "$pkg_dir" && npx tsc --noEmit 2>&1) || true
  fi
}

output=""
case "$rel" in
  *.py)
    output="$(run_basedpyright "$file_path")"
    ;;
  *.ts|*.tsx)
    if [[ "$rel" == apps/frontend/* ]]; then
      output="$(run_tsc "$repo_root/apps/frontend")"
    elif [[ "$rel" == frontend/* ]]; then
      output="$(run_tsc "$repo_root/frontend")"
    fi
    ;;
esac

if [[ -z "$output" ]]; then
  echo '{}'
  exit 0
fi

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.stdin.read()}))" <<<"$output"
exit 0
