#!/usr/bin/env python3
"""Fail if workflows dual-specify pnpm version alongside packageManager.

Guards EV-096 / #1096: pnpm/action-setup with ``with.version`` while root
``package.json`` has ``packageManager`` causes Multiple versions / ERR_PNPM_BAD_PM_VERSION.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ACTION = re.compile(r"uses:\s*pnpm/action-setup@[^\n]+", re.IGNORECASE)
# ``version:`` only within the same step. Refuse any continuation line that is a new
# YAML list item (``- ``), including when indent whitespace would otherwise backtrack.
_VERSION_IN_STEP = re.compile(
    r"uses:\s*pnpm/action-setup@[^\n]+\n"
    r"(?:(?![ \t]*-\s)[ \t]+[^\n]*\n)*?"
    r"[ \t]+version:\s*['\"]?[\d.]+",
    re.IGNORECASE,
)


def _package_manager_pin(repo_root: Path) -> str | None:
    pkg = repo_root / "package.json"
    if not pkg.is_file():
        return None
    data = json.loads(pkg.read_text(encoding="utf-8"))
    pm = data.get("packageManager")
    return pm if isinstance(pm, str) and pm.strip() else None


def _workflow_files(repo_root: Path) -> list[Path]:
    workflows = repo_root / ".github" / "workflows"
    if not workflows.is_dir():
        return []
    return sorted(workflows.glob("*.yml")) + sorted(workflows.glob("*.yaml"))


def find_dual_specs(repo_root: Path) -> list[str]:
    """Return human-readable violations (empty if OK)."""
    pin = _package_manager_pin(repo_root)
    if not pin:
        return []
    hits: list[str] = []
    for path in _workflow_files(repo_root):
        text = path.read_text(encoding="utf-8")
        if not _ACTION.search(text):
            continue
        if _VERSION_IN_STEP.search(text):
            rel = path.relative_to(repo_root).as_posix()
            hits.append(
                f"{rel}: pnpm/action-setup has with.version while packageManager={pin}"
            )
    return hits


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    root = Path(args[1] if len(args) > 1 else ".").resolve()
    hits = find_dual_specs(root)
    if not hits:
        return 0
    print(
        "FAIL: pnpm dual-spec (packageManager + action-setup version) — "
        "remove with.version from pnpm/action-setup; keep root packageManager only.",
        file=sys.stderr,
    )
    for line in hits:
        print(f"  {line}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
