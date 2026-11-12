#!/usr/bin/env python3
"""Cursor afterFileEdit hook: advisory feature context via project-local prefix map.

Config: `.cursor/hooks/config/feature-map.json`
Pack template — installed to `.cursor/hooks/pack/feature_drift.py`.
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
    suffix_allowed,
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

    feature_map, options = load_hook_config(resolve_config(repo, "feature-map.json"))
    if not suffix_allowed(file_path, options):
        print("{}")
        return 0

    try:
        rel = file_path.resolve().relative_to(repo.resolve())
    except ValueError:
        print("{}")
        return 0

    rel_str = str(rel).replace("\\", "/")
    feature = match_longest_prefix(rel_str, feature_map)
    tag = options.get("context_tag", "feature-drift")
    emit_unmapped = options.get("emit_when_unmapped", True)

    if feature:
        if tag == "feature-context":
            context = f"[{tag}] {feature}"
        else:
            context = (
                f"[{tag}] Edit in '{rel_str}' → likely feature: {feature}. "
                "Confirm task maps to docs/feature-list.md and active execution plan."
            )
        print(json.dumps({"additional_context": context}))
    elif feature_map and emit_unmapped:
        context = (
            f"[{tag}] Edit in '{rel_str}' — no automatic feature mapping. "
            "Verify against docs/feature-list.md."
        )
        print(json.dumps({"additional_context": context}))
    else:
        print("{}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
