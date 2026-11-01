#!/usr/bin/env python3
"""Fail when hand-written apps/packages files exceed the line budget (ADR-056).

Rules:
  - Budget: 500 physical lines (newline count).
  - Paths on config/file-budget-allowlist.txt may exceed the budget (grandfathered).
  - Fixed exclusions: generated iwxxm_xsd, frontend generated/, shadcn components/ui/,
    build/coverage/vendor trees.

Usage:
  python3 scripts/ci/check_file_budget.py
  python3 scripts/ci/check_file_budget.py --bootstrap  # print sorted oversize paths

[Corpus: adr/ADR-056] [Corpus: product §M5]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = ROOT / "config" / "file-budget-allowlist.txt"
BUDGET = 500
SCAN_ROOTS = ("apps", "packages")
SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".mjs", ".cjs"}
EXCLUDE_DIR_NAMES = {
    "node_modules",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    "target",
    "htmlcov",
    "iwxxm_xsd",
    "generated",
    ".tox",
    "coverage",
    "playwright-report",
}


def load_allowlist(path: Path | None = None) -> set[str]:
    """Load relative POSIX paths from the allowlist file."""
    allow_path = ALLOWLIST_PATH if path is None else path
    if not allow_path.is_file():
        return set()
    out: set[str] = set()
    for raw in allow_path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            out.add(line.replace("\\", "/"))
    return out


def _is_frontend_ui(rel: str) -> bool:
    """Return True for shadcn UI kit paths (permanently excluded)."""
    return rel.startswith("apps/frontend/src/app/components/ui/")


def is_excluded(path: Path, root: Path | None = None) -> bool:
    """Return True when path is outside the hand-written budget scope."""
    base = ROOT if root is None else root
    try:
        rel = path.relative_to(base).as_posix()
    except ValueError:
        return True
    if path.name == "openapi.d.ts":
        return True
    if _is_frontend_ui(rel):
        return True
    return any(part in EXCLUDE_DIR_NAMES for part in path.parts)


def count_physical_lines(path: Path) -> int:
    """Count physical lines (including blanks) via binary newline scan."""
    data = path.read_bytes()
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def iter_source_files(root: Path | None = None) -> list[Path]:
    """List hand-written source files under apps/ and packages/."""
    base_root = ROOT if root is None else root
    files: list[Path] = []
    for base_name in SCAN_ROOTS:
        base = base_root / base_name
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in SUFFIXES:
                continue
            if is_excluded(path, base_root):
                continue
            files.append(path)
    return sorted(files)


def find_oversize(
    root: Path | None = None,
    budget: int = BUDGET,
) -> list[tuple[str, int]]:
    """Return (rel_path, lines) for files over budget."""
    base_root = ROOT if root is None else root
    rows: list[tuple[str, int]] = []
    for path in iter_source_files(base_root):
        lines = count_physical_lines(path)
        if lines > budget:
            rows.append((path.relative_to(base_root).as_posix(), lines))
    rows.sort(key=lambda item: item[0])
    return rows


def check_budget(
    root: Path | None = None,
    allowlist: set[str] | None = None,
    budget: int = BUDGET,
) -> list[str]:
    """Return violation messages for non-allowlisted oversize files."""
    base_root = ROOT if root is None else root
    allow = allowlist if allowlist is not None else load_allowlist()
    violations: list[str] = []
    for rel, lines in find_oversize(base_root, budget=budget):
        if rel in allow:
            continue
        violations.append(f"{rel}: {lines} lines (budget {budget})")
    missing = sorted(p for p in allow if not (base_root / p).is_file())
    violations.extend(
        f"allowlist path missing on disk: {rel}" for rel in missing
    )
    return violations


def main(argv: list[str] | None = None) -> int:
    """CLI entry — exit 1 on budget violations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Print oversize paths (for regenerating the allowlist).",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=BUDGET,
        help="Physical line budget (default 500).",
    )
    args = parser.parse_args(argv)
    if args.bootstrap:
        for rel, lines in find_oversize(budget=args.budget):
            print(f"{rel}  # {lines}")
        return 0
    violations = check_budget(budget=args.budget)
    if violations:
        print("ADR-056 file budget violations:", file=sys.stderr)
        for item in violations:
            print(f"  {item}", file=sys.stderr)
        print(
            "Add splits or AskQuestion before expanding "
            "config/file-budget-allowlist.txt",
            file=sys.stderr,
        )
        return 1
    print("file budget OK (ADR-056)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
