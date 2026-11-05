#!/usr/bin/env python3
"""Fail if user-docs cross-page links are not GitHub Wiki URLs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

WIKI_PREFIX = "https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki"
DOCS = Path(__file__).resolve().parents[1] / "docs"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    bad: list[str] = []
    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if target.startswith("#"):
                continue
            # External non-doc hosts are allowed (PyPI, app, API).
            if target.startswith("http://") or target.startswith("https://"):
                if (
                    "/EMPIRIC2/TAC-to-IWXXM/wiki" not in target
                    and "pypi.org" not in target
                    and "tac-to-iwxxm.com" not in target
                    and "localhost" not in target
                    and "127.0.0.1" not in target
                ):
                    # Other https links: allow but do not require wiki.
                    continue
                if target.endswith(".md") or ".md#" in target:
                    bad.append(f"{path}: still points at .md via URL: {target}")
                continue
            if target.endswith(".md") or ".md#" in target or target.endswith(".mdx"):
                bad.append(f"{path}: relative doc link {target!r} — use {WIKI_PREFIX}/…")
    if bad:
        print("Wiki link check FAILED:", file=sys.stderr)
        for line in bad:
            print(f"  {line}", file=sys.stderr)
        return 1
    print(f"Wiki link check PASS ({DOCS})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
