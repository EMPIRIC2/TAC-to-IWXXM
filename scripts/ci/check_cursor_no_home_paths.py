#!/usr/bin/env python3
"""Fail if tracked .cursor files embed machine-local home absolute paths.

Guards EV-095 / #1095: committed /Users/... or /home/<user>/... break team/CI
engineering-memory plugin + MCP registration.

Allowed portable forms include $HOME, ${userHome}, $EM_ENGINEERING_MEMORY_ROOT,
and relative .cursor/ paths — those are not matched.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Match /Users/<name>/... or /home/<name>/... (not /Users alone or $HOME expansions).
_HOME_ABS = (
    r"/Users/[A-Za-z0-9._-]+/",
    r"/home/[A-Za-z0-9._-]+/",
)

_SKIP_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
}


def _tracked_cursor_files(repo_root: Path) -> list[Path]:
    out = subprocess.check_output(
        ["git", "ls-files", "-z", "--", ".cursor"],
        cwd=repo_root,
        text=False,
    )
    paths: list[Path] = []
    for raw in out.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="replace")
        path = repo_root / rel
        if path.suffix.lower() in _SKIP_SUFFIXES:
            continue
        if not path.is_file():
            continue
        paths.append(path)
    return paths


def _findings(repo_root: Path) -> list[str]:
    import re

    patterns = [re.compile(p) for p in _HOME_ABS]
    hits: list[str] = []
    for path in _tracked_cursor_files(repo_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for pat in patterns:
                if pat.search(line):
                    rel = path.relative_to(repo_root)
                    hits.append(f"{rel}:{i}: {line.strip()[:160]}")
                    break
    return hits


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    hits = _findings(repo_root)
    if hits:
        print(
            "FAIL: tracked .cursor/ contains machine-local home absolute paths "
            "(EV-095 / #1095):",
            file=sys.stderr,
        )
        for h in hits:
            print(f"  {h}", file=sys.stderr)
        print(
            "Use EM_ENGINEERING_MEMORY_ROOT / ${userHome} / runtime resolve; "
            "re-run install-workspace.sh.",
            file=sys.stderr,
        )
        return 1
    print("OK: no machine-local home paths in tracked .cursor/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
