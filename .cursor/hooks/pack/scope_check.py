#!/usr/bin/env python3
"""Cursor preToolUse hook: advisory scope check via project-local prefix map.

Config: `.cursor/hooks/config/scope-map.json`
Pack template — installed to `.cursor/hooks/pack/scope_check.py`.
Advisory only — always exits 0.

[Corpus: cross-repo-tooling] [Corpus: hook-contract]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _lib in (_HERE / "lib", _HERE.parent / "lib"):
    if _lib.is_dir() and str(_lib) not in sys.path:
        sys.path.insert(0, str(_lib))
        break

from prefix_map import (  # noqa: E402
    find_repo_root,
    load_hook_config,
    match_longest_prefix,
    resolve_config,
)

DEFAULT_UNMAPPED = (
    "does not map to any approved component. Verify scope or raise [Scope Drift]."
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}")
        return 0

    raw = payload.get("filePath") or payload.get("file_path") or ""
    if not raw:
        print("{}")
        return 0

    file_path = Path(raw)
    repo = find_repo_root(file_path)
    if repo is None:
        print("{}")
        return 0

    try:
        rel = file_path.resolve().relative_to(repo.resolve())
    except ValueError:
        print("{}")
        return 0

    rel_str = str(rel).replace("\\", "/")
    scope_map, options = load_hook_config(resolve_config(repo, "scope-map.json"))
    component = match_longest_prefix(rel_str, scope_map)
    tag = options.get("context_tag", "scope-check")

    if component:
        result = {"additional_context": f"[{tag}] File maps to: {component}"}
    elif scope_map:
        unmapped = options.get("unmapped_message", DEFAULT_UNMAPPED)
        result = {
            "additional_context": f"[{tag}] WARNING: '{rel_str}' {unmapped}"
        }
    else:
        result = {
            "additional_context": (
                f"[{tag}] No scope-map.json configured — add "
                ".cursor/hooks/config/scope-map.json (see cursor-plugin/hooks/config/examples/)."
            )
        }

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
