#!/usr/bin/env python3
r"""Fail when *new* test modules use planning-id filename stems.

Preferred pattern: ``test_<subject>_<scenario>.py``. Cite EV/TC/M only in
docstrings, markers, or comments — never as the file stem.

Banned for **new** files (basename):

- ``test_ev*.py`` planning dumps (``test_ev_``, ``test_ev040_``, ...) — not
  product names such as ``test_evaluation_*.py``
- ``test_tc_ev*.py``
- ``test_m\d+_*.py`` milestone detector-routing stems

Carve-outs:

- Historical files already on the base branch (allowlist via git)
- WMO AHL ``fc_*`` bulletin fixtures (TTAAii ``FC`` designator) — never banned
- Unrelated stems that merely contain the letters (for example
  ``test_evaluation_``, ``metar_*_m_prefix*``)

[Corpus: tests]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Planning-id stems only. ``test_evaluation_`` does not match (next char is
# a letter after ``test_ev``, not end / underscore / digit).
_BANNED_STEMS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^test_ev(?:$|_|[0-9])", re.IGNORECASE),
    re.compile(r"^test_tc_ev", re.IGNORECASE),
    re.compile(r"^test_m\d+_", re.IGNORECASE),
)

# WMO TTAAii FC designator fixtures (AHL) — always allowed.
_AHL_FC_FIXTURE = re.compile(r"^fc_[A-Za-z0-9._-]+\.(txt|tac|raw)$", re.IGNORECASE)


@dataclass(frozen=True)
class PolicyVerdict:
    """Result of classifying one relative path."""

    path: str
    allowed: bool
    reason: str


def basename_stem_and_suffix(rel_path: str) -> tuple[str, str]:
    """
    Return ``(stem, suffix)`` for the final path component.

    Parameters
    ----------
    rel_path:
        Repository-relative path using ``/`` separators.
    """
    name = Path(rel_path).name
    suffix = Path(name).suffix.lower()
    stem = Path(name).stem
    return stem, suffix


def is_ahl_fc_fixture(rel_path: str) -> bool:
    """Return True when the basename is a WMO AHL ``fc_*`` fixture."""
    return bool(_AHL_FC_FIXTURE.match(Path(rel_path).name))


def matches_banned_planning_stem(stem: str) -> bool:
    """Return True when a file stem matches a banned planning-id pattern."""
    return any(pat.search(stem) for pat in _BANNED_STEMS)


def classify_path(
    rel_path: str,
    *,
    is_new: bool,
    historical_allowlist: frozenset[str] | set[str] | None = None,
) -> PolicyVerdict:
    """
    Classify a repository-relative path against the naming policy.

    Parameters
    ----------
    rel_path:
        Path relative to the repository root (POSIX style preferred).
    is_new:
        True when the path is newly added versus the comparison base.
    historical_allowlist:
        Paths that already existed on the base branch (normalized).
    """
    normalized = rel_path.replace("\\", "/").lstrip("./")
    allow = frozenset(historical_allowlist or ())

    if is_ahl_fc_fixture(normalized):
        return PolicyVerdict(normalized, True, "ahl_fc_fixture")

    stem, suffix = basename_stem_and_suffix(normalized)
    if suffix != ".py":
        return PolicyVerdict(normalized, True, "non_python")

    if not matches_banned_planning_stem(stem):
        return PolicyVerdict(normalized, True, "behavior_named_or_unrelated")

    if not is_new:
        return PolicyVerdict(normalized, True, "historical_existing")

    if normalized in allow:
        return PolicyVerdict(normalized, True, "historical_allowlist")

    return PolicyVerdict(
        normalized,
        False,
        "banned_planning_id_stem_on_new_file",
    )


def _git_output(repo_root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stderr=subprocess.DEVNULL,
    )


def list_new_paths(repo_root: Path, base_ref: str) -> list[str]:
    """Return paths added on HEAD relative to ``base_ref`` (three-dot)."""
    try:
        merge_base = _git_output(repo_root, "merge-base", base_ref, "HEAD").strip()
    except subprocess.CalledProcessError:
        merge_base = base_ref
    try:
        out = _git_output(
            repo_root,
            "diff",
            "--name-only",
            "--diff-filter=A",
            f"{merge_base}...HEAD",
        )
    except subprocess.CalledProcessError:
        return []
    return [
        line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()
    ]


def list_base_paths(repo_root: Path, base_ref: str) -> frozenset[str]:
    """Return tracked paths on ``base_ref`` for historical allowlisting."""
    try:
        out = _git_output(repo_root, "ls-tree", "-r", "--name-only", base_ref)
    except subprocess.CalledProcessError:
        return frozenset()
    return frozenset(
        line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()
    )


def findings_for_new_paths(
    new_paths: list[str],
    *,
    historical_allowlist: frozenset[str] | set[str] | None = None,
) -> list[PolicyVerdict]:
    """Return policy failures for newly added paths."""
    failed: list[PolicyVerdict] = []
    for path in new_paths:
        verdict = classify_path(
            path,
            is_new=True,
            historical_allowlist=historical_allowlist,
        )
        if not verdict.allowed:
            failed.append(verdict)
    return failed


def main(argv: list[str] | None = None) -> int:
    """
    Exit 1 when newly added files violate the planning-id naming ban.

    Parameters
    ----------
    argv:
        CLI arguments. ``argv[0]`` is the program name when present.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed when new test modules use planning-id filename stems "
            "(test_ev*, test_tc_ev*, test_mN_*)."
        )
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Repository root (default: cwd)",
    )
    parser.add_argument(
        "--base",
        default="origin/stage",
        help="Git ref for historical allowlist and new-file diff (default: origin/stage)",
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        dest="extra_paths",
        help="Treat PATH as a newly added file (repeatable; for local checks)",
    )
    args = parser.parse_args(list(argv[1:] if argv is not None else sys.argv[1:]))
    repo_root = Path(args.repo_root).resolve()

    historical = list_base_paths(repo_root, args.base)
    new_paths = list(args.extra_paths)
    if not new_paths:
        new_paths = list_new_paths(repo_root, args.base)

    failed = findings_for_new_paths(new_paths, historical_allowlist=historical)
    if failed:
        print(
            "FAIL: new file(s) use banned planning-id test filename stems. "
            "Prefer test_<subject>_<scenario>.py; cite EV/TC/M in docstrings "
            "or markers only. WMO AHL fc_* fixtures stay allowed.",
            file=sys.stderr,
        )
        for item in failed:
            print(f"  {item.path}: {item.reason}", file=sys.stderr)
        return 1

    print(
        f"OK: no banned planning-id stems in {len(new_paths)} new path(s) "
        f"(base={args.base})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
