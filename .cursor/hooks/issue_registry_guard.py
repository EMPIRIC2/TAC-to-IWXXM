"""Cursor afterFileEdit hook: flag ad-hoc severity literals in tac-validate rules.

CI/pre-commit hard-fails via ``ISSUE_REGISTRY_GUARD_STRICT=1`` (T2.2a). This hook
still exits 0 so edits are not blocked in-editor, but messages say ERROR.
Skips the registry module itself and tests.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Match severity= / severity : string literals common in Issue(...) construction
_SEVERITY_LIT = re.compile(
    r"""severity\s*=\s*['"](?:error|warning|info)['"]"""
    r"""|severity\s*:\s*['"](?:error|warning|info)['"]""",
    re.IGNORECASE,
)

_SKIP_NAME_PARTS = (
    "issue_registry",
    "registry.py",
    "/tests/",
    "\\tests\\",
    "conftest.py",
    "models.py",  # Issue.severity field type docs / Struct
)


def find_repo_root(start: Path) -> Path | None:
    p = start if start.is_dir() else start.parent
    for candidate in [p, *p.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


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
    if not rel_str.startswith("packages/tac-validate/") or not rel_str.endswith(".py"):
        print("{}")
        return 0

    lower = rel_str.lower()
    if any(part in lower for part in _SKIP_NAME_PARTS):
        print("{}")
        return 0

    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError:
        print("{}")
        return 0

    hits = list(_SEVERITY_LIT.finditer(text))
    if not hits:
        print("{}")
        return 0

    # Show up to 3 line numbers
    lines = text.splitlines()
    line_nos: list[int] = []
    pos = 0
    line_starts = [0]
    for line in lines:
        pos += len(line) + 1
        line_starts.append(pos)

    def offset_to_line(off: int) -> int:
        for i in range(len(line_starts) - 1):
            if line_starts[i] <= off < line_starts[i + 1]:
                return i + 1
        return len(lines)

    for m in hits[:3]:
        line_nos.append(offset_to_line(m.start()))

    context = (
        f"[issue-registry-guard] '{rel_str}' contains severity string literal(s) "
        f"near line(s) {', '.join(map(str, line_nos))}. "
        "Per F15/ADR-028, prefer importing default severity from the tac-validate "
        "issue registry (not ad-hoc severity= in rule bodies). "
        "Registry module and tests are exempt."
    )
    print(json.dumps({"additional_context": context}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
