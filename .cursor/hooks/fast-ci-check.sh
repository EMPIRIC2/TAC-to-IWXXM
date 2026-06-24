#!/usr/bin/env bash
# Cursor afterFileEdit hook: fast CI parity on edited files (format fix + lint fix + verify).
# Mirrors make validate-fast checks scoped to the edited file (format-check + lint).
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

output=""

append_output() {
  local section="$1"
  local text="$2"
  if [[ -n "$text" ]]; then
    output+="${section}
${text}

"
  fi
}

in_python_tree() {
  case "$rel" in
    apps/*|packages/*|tests/*) return 0 ;;
    *) return 1 ;;
  esac
}

run_python_fast_ci() {
  local target="$1"
  local format_out lint_fix_out format_check_out lint_check_out

  if ! command -v uv >/dev/null 2>&1 || [[ ! -f "$repo_root/pyproject.toml" ]]; then
    if command -v ruff >/dev/null 2>&1; then
      format_out="$(ruff format "$target" 2>&1 || true)"
      lint_fix_out="$(ruff check --fix "$target" 2>&1 || true)"
      format_check_out="$(ruff format --check "$target" 2>&1 || true)"
      lint_check_out="$(ruff check "$target" 2>&1 || true)"
    else
      append_output "[fast-ci] Python" "ruff not installed — run 'make install' or 'uv sync' at repo root."
      return
    fi
  else
    format_out="$(cd "$repo_root" && uv run ruff format "$target" 2>&1 || true)"
    lint_fix_out="$(cd "$repo_root" && uv run ruff check --fix "$target" 2>&1 || true)"
    format_check_out="$(cd "$repo_root" && uv run ruff format --check "$target" 2>&1 || true)"
    lint_check_out="$(cd "$repo_root" && uv run ruff check "$target" 2>&1 || true)"
  fi

  append_output "[fast-ci] ruff format" "$format_out"
  append_output "[fast-ci] ruff check --fix" "$lint_fix_out"
  append_output "[fast-ci] ruff format --check" "$format_check_out"
  append_output "[fast-ci] ruff check" "$lint_check_out"
}

run_js_fast_ci() {
  local target="$1"
  local pkg_dir="$2"
  local prettier_out eslint_fix_out prettier_check_out eslint_check_out

  if [[ ! -f "$pkg_dir/package.json" ]]; then
    return
  fi

  if command -v pnpm >/dev/null 2>&1; then
    prettier_out="$(cd "$repo_root" && pnpm exec prettier --write "$target" 2>&1 || true)"
    eslint_fix_out="$(cd "$repo_root" && pnpm exec eslint "$target" --fix 2>&1 || true)"
    prettier_check_out="$(cd "$repo_root" && pnpm exec prettier --check "$target" 2>&1 || true)"
    eslint_check_out="$(cd "$repo_root" && pnpm exec eslint "$target" 2>&1 || true)"
  elif command -v npx >/dev/null 2>&1; then
    prettier_out="$(cd "$repo_root" && npx prettier --write "$target" 2>&1 || true)"
    eslint_fix_out="$(cd "$repo_root" && npx eslint "$target" --fix 2>&1 || true)"
    prettier_check_out="$(cd "$repo_root" && npx prettier --check "$target" 2>&1 || true)"
    eslint_check_out="$(cd "$repo_root" && npx eslint "$target" 2>&1 || true)"
  else
    append_output "[fast-ci] JS/TS" "pnpm/npx not available — run 'make install' at repo root."
    return
  fi

  append_output "[fast-ci] prettier --write" "$prettier_out"
  append_output "[fast-ci] eslint --fix" "$eslint_fix_out"
  append_output "[fast-ci] prettier --check" "$prettier_check_out"
  append_output "[fast-ci] eslint" "$eslint_check_out"
}

case "$rel" in
  *.py)
    if in_python_tree; then
      run_python_fast_ci "$file_path"
    fi
    ;;
  *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.md)
    if [[ "$rel" == apps/frontend/* ]]; then
      run_js_fast_ci "$file_path" "$repo_root/apps/frontend"
    elif [[ "$rel" == frontend/* ]]; then
      run_js_fast_ci "$file_path" "$repo_root/frontend"
    elif [[ "$rel" == apps/e2e/* ]]; then
      run_js_fast_ci "$file_path" "$repo_root/apps/e2e"
    elif [[ "$rel" == packages/shared/* ]]; then
      run_js_fast_ci "$file_path" "$repo_root/packages/shared"
    elif [[ "$rel" == packages/* ]]; then
      run_js_fast_ci "$file_path" "$repo_root"
    elif [[ "$rel" == apps/* ]]; then
      run_js_fast_ci "$file_path" "$repo_root"
    fi
    ;;
esac

if [[ -z "$output" ]]; then
  echo '{}'
  exit 0
fi

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.stdin.read()}))" <<<"$output"
exit 0
