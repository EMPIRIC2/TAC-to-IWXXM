#!/usr/bin/env python3
"""Strip placeholder ``>>> 1 + 1`` docstring smoke Examples blocks.

Removes NumPy ``Examples`` sections whose only doctest is trivial arithmetic
left by :mod:`scripts.docs.backfill_py_docs`. Real Examples are left alone.

[Corpus: doc-standards] [Corpus: tests] TC-EVDOC-002 / TC-EVDOC-004
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SMOKE_EXAMPLES_BLOCK = re.compile(
    r"\n(?P<indent>[ \t]*)Examples\n"
    r"(?P=indent)-{3,}\n"
    r"(?P=indent)>>> 1 \+ 1(?:[ \t]+#[^\n]*)?\n"
    r"(?P=indent)2"
)

BARE_SMOKE_LINE = re.compile(r"(?m)^[ \t]*>>> 1 \+ 1(?:[ \t]+#[^\n]*)?\n(?:[ \t]*2\n)?")

SKIP_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "vendor",
    ".venv",
    "dist",
    "build",
    "target",
    "iwxxm_xsd",
    "generated",
}


def strip_smoke_examples(src: str) -> str:
    """Return ``src`` with placeholder smoke Examples blocks removed."""
    updated = SMOKE_EXAMPLES_BLOCK.sub("", src)
    updated = BARE_SMOKE_LINE.sub("", updated)
    if updated == src:
        return src
    # Only when a smoke stub was removed: drop one leftover blank line
    # immediately before a closing triple-quote (keeps --check idempotent).
    updated = re.sub(r"\n[ \t]*\n([ \t]*)" + '"""', r"\n\1" + '"""', updated)
    return updated


def _should_skip(path: Path) -> bool:
    """Skip generated / vendor trees."""
    return any(name in path.parts for name in SKIP_DIR_NAMES)


def iter_py_files(root: Path) -> list[Path]:
    """List ``.py`` files under ``root`` excluding skip dirs."""
    return sorted(path for path in root.rglob("*.py") if not _should_skip(path))


def main(argv: list[str] | None = None) -> int:
    """Strip smoke Examples; print counts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    changed = 0
    remaining = 0
    for path in iter_py_files(root):
        original = path.read_text(encoding="utf-8")
        updated = strip_smoke_examples(original)
        if SMOKE_EXAMPLES_BLOCK.search(updated) or BARE_SMOKE_LINE.search(updated):
            remaining += 1
        if updated == original:
            continue
        if args.check:
            changed += 1
            continue
        path.write_text(updated, encoding="utf-8")
        changed += 1
    verb = "changed_would" if args.check else "changed_files"
    print(f"strip_doctest_smokes {verb}={changed} remaining_1_plus_1={remaining}")
    if args.check:
        return 1 if changed or remaining else 0
    return 1 if remaining else 0


if __name__ == "__main__":
    raise SystemExit(main())
