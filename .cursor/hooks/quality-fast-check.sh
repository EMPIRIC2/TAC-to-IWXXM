#!/usr/bin/env bash
# Cursor hook: Wave 1 fast quality checks (EV-quality-tooling-suite).
#
# Events (dispatch on hook_event_name, falling back to payload shape):
#   afterFileEdit        - FAST subset only, scoped to the edited file's workspace member:
#                            Python: import-linter (only if a config exists), deptry (member only)
#                            JS/TS : knip / depcruise (only if the binary is installed)
#   beforeShellExecution - advisory message for `make check`, `uv add`, `pnpm add`
#
# Fails OPEN: missing tools, missing config, or any internal error -> allow with no noise.
# Never installs anything. Always exits 0. Output is valid JSON:
#   afterFileEdit        -> {} | {"additional_context": "..."}
#   beforeShellExecution -> {"permission":"allow"[, "agent_message": "..."]}
set -uo pipefail

MAX_LINES="${QUALITY_FAST_CHECK_MAX_LINES:-30}"

payload="$(cat 2>/dev/null || true)"

# Parse stdin once: emit "<event>\x1f<file_path>\x1f<command>" (unit-separator delimited; tabs/newlines flattened).
parsed="$(
  python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
if not isinstance(d, dict):
    d = {}
def flat(v):
    return str(v or "").replace("\t", " ").replace("\n", " ")
ev = d.get("hook_event_name") or ""
fp = d.get("file_path") or d.get("filePath") or ""
cmd = d.get("command") or ""
if not ev:
    ev = "beforeShellExecution" if cmd and not fp else "afterFileEdit"
print("\x1f".join([flat(ev), flat(fp), flat(cmd)]))
' <<<"$payload" 2>/dev/null
)" || parsed=""

IFS=$'\x1f' read -r event file_path command <<<"$parsed" || true

emit_empty() {
  if [[ "$event" == "beforeShellExecution" ]]; then
    echo '{"permission":"allow"}'
  else
    echo '{}'
  fi
  exit 0
}

# json_out <key> <text>
json_out() {
  python3 -c '
import json, sys
key, text = sys.argv[1], sys.stdin.read().rstrip()
out = {"permission": "allow"} if key == "agent_message" else {}
out[key] = text
print(json.dumps(out))
' "$1" <<<"$2" 2>/dev/null || emit_empty
}

# ---------------------------------------------------------------- shell advisory
if [[ "$event" == "beforeShellExecution" ]]; then
  msg=""
  if [[ "$command" =~ (^|[[:space:];\&|])make[[:space:]]+check([[:space:]]|$) ]]; then
    msg="[quality-fast-check] 'make check' runs the full gate. For a quicker loop use 'make validate-fast' (format-check + lint) first."
  elif [[ "$command" =~ (^|[[:space:];\&|])uv[[:space:]]+add([[:space:]]|$) ]]; then
    msg="[quality-fast-check] New Python dependency: back-add it to the dependency inventory and regenerate the SBOM ('make sbom'). Run deptry on the member afterwards if installed."
  elif [[ "$command" =~ (^|[[:space:];\&|])pnpm[[:space:]]+add([[:space:]]|$) ]]; then
    msg="[quality-fast-check] New JS dependency: back-add it to the dependency inventory and regenerate the SBOM ('make sbom'). Run knip on the member afterwards if installed."
  fi
  if [[ -n "$msg" ]]; then
    json_out agent_message "$msg"
    exit 0
  fi
  emit_empty
fi

# ---------------------------------------------------------------- afterFileEdit
[[ -n "$file_path" && -f "$file_path" ]] || emit_empty

repo_root="$(git -C "$(dirname "$file_path")" rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$repo_root" ]] || emit_empty
rel="${file_path#"$repo_root"/}"
rel="${rel#/}"

# Workspace member = first two path segments under apps/ or packages/.
member=""
case "$rel" in
  apps/*/*|packages/*/*)
    member="$(printf '%s' "$rel" | cut -d/ -f1-2)"
    ;;
esac
[[ -n "$member" ]] || emit_empty
member_dir="$repo_root/$member"

# Per-tool time cap (hook timeout is 60s). rc 124 on timeout is treated as "no finding".
TIMEOUT=()
for t in timeout gtimeout; do
  if command -v "$t" >/dev/null 2>&1; then TIMEOUT=("$t" "${QUALITY_FAST_CHECK_TOOL_TIMEOUT:-20}"); break; fi
done

output=""
# append <title> <text>: truncate to MAX_LINES; skip blank text.
append() {
  local text
  text="$(printf '%s\n' "$2" | head -n "$MAX_LINES")"
  if printf '%s' "$text" | grep -q '[^[:space:]]'; then
    output+="$1
$text

"
  fi
  return 0
}

# find_bin <name>: repo venv, then PATH. Prints path or nothing. Never installs.
find_py_bin() {
  if [[ -x "$repo_root/.venv/bin/$1" ]]; then
    echo "$repo_root/.venv/bin/$1"
  elif command -v "$1" >/dev/null 2>&1; then
    command -v "$1"
  fi
}

# find_node_bin <name>: member then root node_modules/.bin (so pnpm exec resolves it).
has_node_bin() {
  [[ -x "$member_dir/node_modules/.bin/$1" || -x "$repo_root/node_modules/.bin/$1" ]]
}

run_py() {
  # import-linter: only with an explicit contract config at the repo root.
  local lint_imports
  lint_imports="$(find_py_bin lint-imports)"
  if [[ -n "$lint_imports" ]] \
    && { [[ -f "$repo_root/config/tooling/importlinter.ini" ]] \
      || [[ -f "$repo_root/.importlinter" ]] \
      || grep -qs '^\[tool\.importlinter\]' "$repo_root/pyproject.toml"; }; then
    local out rc
    local il_cfg=()
    if [[ -f "$repo_root/config/tooling/importlinter.ini" ]]; then
      il_cfg=(--config "$repo_root/config/tooling/importlinter.ini")
    fi
    out="$(cd "$repo_root" && ${TIMEOUT[@]+"${TIMEOUT[@]}"} "$lint_imports" "${il_cfg[@]}" 2>&1)"; rc=$?
    if [[ $rc -ne 0 && $rc -ne 124 ]]; then
      append "[quality] import-linter contracts FAILED" "$out"
    fi
  fi

  # deptry: changed member only, only if the member declares its deps.
  local deptry
  deptry="$(find_py_bin deptry)"
  if [[ -n "$deptry" && -f "$member_dir/pyproject.toml" ]]; then
    local out rc
    out="$(cd "$member_dir" && ${TIMEOUT[@]+"${TIMEOUT[@]}"} "$deptry" . 2>&1)"; rc=$?
    if [[ $rc -ne 0 && $rc -ne 124 ]]; then
      append "[quality] deptry ($member) reported dependency issues" "$out"
    fi
  fi
}

run_js() {
  command -v pnpm >/dev/null 2>&1 || return 0
  [[ -f "$member_dir/package.json" ]] || return 0

  if has_node_bin knip; then
    local out rc
    # Knip is project-wide; report only findings that mention the edited file.
    local file_in_member="${rel#"$member"/}"
    out="$(cd "$member_dir" && ${TIMEOUT[@]+"${TIMEOUT[@]}"} pnpm exec knip --no-progress 2>&1)"; rc=$?
    if [[ $rc -ne 0 && $rc -ne 124 ]]; then
      out="$(printf '%s\n' "$out" | grep -F -- "$file_in_member" || true)"
      append "[quality] knip ($member) findings for $file_in_member" "$out"
    fi
  fi

  if has_node_bin depcruise; then
    local cfg=""
    for c in .dependency-cruiser.cjs .dependency-cruiser.js .dependency-cruiser.mjs; do
      if [[ -f "$member_dir/$c" ]]; then cfg="$member_dir/$c"; break; fi
      if [[ -f "$repo_root/config/tooling/$c" ]]; then cfg="$repo_root/config/tooling/$c"; break; fi
      if [[ -f "$repo_root/$c" ]]; then cfg="$repo_root/$c"; break; fi
    done
    if [[ -n "$cfg" ]]; then
      local out rc
      out="$(cd "$member_dir" && ${TIMEOUT[@]+"${TIMEOUT[@]}"} pnpm exec depcruise --config "$cfg" "$file_path" 2>&1)"; rc=$?
      if [[ $rc -ne 0 && $rc -ne 124 ]]; then
        append "[quality] dependency-cruiser ($rel) violations" "$out"
      fi
    fi
  fi
}

case "$rel" in
  *.py) run_py ;;
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs) run_js ;;
esac

if [[ -z "$output" ]]; then
  emit_empty
fi
json_out additional_context "$output"
exit 0
