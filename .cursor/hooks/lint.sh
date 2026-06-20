#!/usr/bin/env bash
# Cursor afterFileEdit hook: run linter on edited source files (advisory).
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

run_ruff() {
  local target="$1"
  if command -v uv >/dev/null 2>&1 && [[ -f "$repo_root/pyproject.toml" ]]; then
    (cd "$repo_root" && uv run ruff check "$target" 2>&1) || true
  elif command -v ruff >/dev/null 2>&1; then
    ruff check "$target" 2>&1 || true
  else
    echo "[lint] ruff not installed — run 'make install' or 'uv sync' at repo root."
  fi
}

run_eslint() {
  local target="$1"
  local pkg_dir="$2"
  if [[ -f "$pkg_dir/package.json" ]] && command -v pnpm >/dev/null 2>&1; then
    (cd "$pkg_dir" && pnpm exec eslint "$target" 2>&1) || true
  elif [[ -f "$pkg_dir/package.json" ]] && command -v npm >/dev/null 2>&1; then
    (cd "$pkg_dir" && npx eslint "$target" 2>&1) || true
  else
    echo "[lint] eslint not available in $pkg_dir"
  fi
}

output=""
case "$rel" in
  *.py)
    output="$(run_ruff "$file_path")"
    ;;
  *.ts|*.tsx|*.js|*.jsx)
    if [[ "$rel" == apps/frontend/* ]]; then
      output="$(run_eslint "$file_path" "$repo_root/apps/frontend")"
    elif [[ "$rel" == frontend/* ]]; then
      output="$(run_eslint "$file_path" "$repo_root/frontend")"
    elif [[ "$rel" == apps/e2e/* ]]; then
      output="$(run_eslint "$file_path" "$repo_root/apps/e2e")"
    fi
    ;;
esac

if [[ -z "$output" ]]; then
  echo '{}'
  exit 0
fi

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.stdin.read()}))" <<<"$output"
exit 0
