#!/usr/bin/env bash
# workspaceOpen — load engineering-memory plugin for this workspace only.
# Resolves plugin path at runtime (no machine-local absolute paths).
# [Corpus: skill-integration] [Corpus: hook-contract] [Corpus: deploy]
# Refs: BUG-2026-08-31 / joseph-c-mcguire/spec-dev-knowledge-graph#106
set -euo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$HOOKS_DIR/../.." && pwd)"

resolve_plugin_dir() {
  local root=""
  if [[ -n "${EM_ENGINEERING_MEMORY_ROOT:-}" ]]; then
    root="$EM_ENGINEERING_MEMORY_ROOT"
  elif [[ -f "$WORKSPACE_ROOT/cursor-plugin/.cursor-plugin/plugin.json" ]]; then
    printf '%s\n' "$WORKSPACE_ROOT/cursor-plugin"
    return 0
  elif [[ -f "$WORKSPACE_ROOT/packages/engineering-memory/pyproject.toml" ]]; then
    root="$WORKSPACE_ROOT"
  else
    local sibling
    sibling="$(cd "$WORKSPACE_ROOT/.." && pwd)/spec-dev-knowledge-graph"
    if [[ -d "$sibling/cursor-plugin" ]]; then
      root="$sibling"
    else
      # Last-resort convention only — prefer EM_ENGINEERING_MEMORY_ROOT (#106).
      root="${HOME}/Documents/GitHub/spec-dev-knowledge-graph"
    fi
  fi
  printf '%s\n' "$root/cursor-plugin"
}

PLUGIN_DIR="$(resolve_plugin_dir)"
if [[ -d "$PLUGIN_DIR" ]]; then
  PLUGIN_DIR="$(cd "$PLUGIN_DIR" && pwd)"
fi

if [[ ! -f "$PLUGIN_DIR/.cursor-plugin/plugin.json" ]]; then
  echo "register-workspace-plugins: plugin not found at $PLUGIN_DIR (set EM_ENGINEERING_MEMORY_ROOT)" >&2
  python3 -c 'import json; print(json.dumps({"pluginPaths": []}))'
  exit 0
fi

python3 -c 'import json, sys; print(json.dumps({"pluginPaths": [sys.argv[1]]}))' "$PLUGIN_DIR"
