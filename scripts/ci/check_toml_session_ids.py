#!/usr/bin/env python3
"""Fail when tracked ``*.toml`` files embed session-style ``S###`` planning ids.

Banned token shape: word-boundary ``S`` + three or more digits (``S000``,
``S008``, ``S014``, …), including inside compound tokens such as
``D-S014-…``. Prefer plain-language descriptions and comments.

[Corpus: tests]
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Session / planning ids: S + ≥3 digits (zero-padded forms included).
SESSION_ID_RE = re.compile(r"\bS\d{3,}\b")


@dataclass(frozen=True)
class Hit:
    """One banned token occurrence in a TOML file."""

    path: str
    line: int
    token: str
    text: str


@dataclass(frozen=True)
class ScanResult:
    """Aggregate scan of one or more TOML paths."""

    hits: tuple[Hit, ...]

    @property
    def ok(self) -> bool:
        """True when no banned tokens were found."""
        return not self.hits


def find_session_ids(text: str) -> tuple[str, ...]:
    """Return distinct banned ``S###`` tokens found in ``text``."""
    return tuple(sorted(set(SESSION_ID_RE.findall(text))))


def scan_toml_text(path: str, text: str) -> tuple[Hit, ...]:
    """Scan one TOML body; return ordered hits."""
    hits: list[Hit] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        hits.extend(
            Hit(path=path, line=lineno, token=match.group(0), text=line.rstrip())
            for match in SESSION_ID_RE.finditer(line)
        )
    return tuple(hits)


def scan_toml_path(path: Path, *, rel: str | None = None) -> tuple[Hit, ...]:
    """Read and scan a TOML file on disk."""
    label = rel if rel is not None else str(path)
    return scan_toml_text(label, path.read_text(encoding="utf-8"))


def tracked_toml_files(repo_root: Path) -> tuple[Path, ...]:
    """List tracked ``*.toml`` paths under ``repo_root`` via git."""
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "*.toml"],
        check=True,
        capture_output=True,
        text=True,
    )
    rels = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return tuple(repo_root / rel for rel in rels)


def scan_tracked_tomls(repo_root: Path) -> ScanResult:
    """Scan every tracked TOML under the repo root."""
    hits: list[Hit] = []
    for path in tracked_toml_files(repo_root):
        rel = str(path.relative_to(repo_root))
        hits.extend(scan_toml_path(path, rel=rel))
    return ScanResult(hits=tuple(hits))


def main(argv: list[str] | None = None) -> int:
    """CLI entry: exit 1 when any tracked TOML embeds ``S###``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: cwd)",
    )
    args = parser.parse_args(argv)
    result = scan_tracked_tomls(args.root.resolve())
    if result.ok:
        print("ok: no S### session ids in tracked *.toml")
        return 0
    for hit in result.hits:
        print(f"{hit.path}:{hit.line}: banned session id {hit.token!r}: {hit.text}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())