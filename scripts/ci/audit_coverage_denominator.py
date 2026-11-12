#!/usr/bin/env python3
r"""Audit that the coverage denominator contains every expected source tree.

``fail_under = 100`` is only meaningful when the denominator is complete. An
empty report, a missing workspace member, or a hand-written file hidden by a
whole-file ``omit`` all make ``fail_under`` pass without measuring the code.
This script fails closed on each of those cases.

[Corpus: tests] [Corpus: tech-spec]

Checks
------
1. Every ``--artifact`` JSON has at least one file and at least one statement.
2. Every expected member (default: all ``[tool.uv.workspace] members`` that have
   a Python ``src`` tree) has an artifact, and that artifact measures it.
3. Every hand-written ``*.py`` file under the member's coverage ``source`` tree
   appears in the report (files hidden by ``omit`` are listed as missing).
4. ``[tool.coverage.*] omit`` entries in member ``pyproject.toml`` files only use
   allowed patterns (tests, ``__main__``, generated ``iwxxm_xsd/v*``). Any other
   whole-file omit of hand-written code fails.

Usage
-----
Produce one JSON per member, with the same coverage config the gate uses::

    cd apps/backend && uv run pytest tests/unit \
        --cov=src --cov-config=pyproject.toml --cov-report=json:coverage.json

Then audit (``MEMBER_DIR=JSON``; JSON paths resolve relative to the member dir)::

    python scripts/ci/audit_coverage_denominator.py \
        --artifact apps/backend=apps/backend/coverage.json \
        --artifact packages/auth=packages/auth/coverage.json

    # Audit only omit policy + on-disk trees (no artifacts), e.g. in pre-commit:
    python scripts/ci/audit_coverage_denominator.py --omits-only

Use ``--member packages/auth --member apps/backend`` to restrict the expected set.
Use ``--known-gap apps/backend/src/<path>.py`` only to accept a tracked, explicit gap.
Exit status is 0 when all checks pass, 1 on any failure, 2 on usage errors.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

# Whole-file omit patterns that are allowed (generated code and test files only).
# ADR-027: generated xsdata trees under iwxxm_xsd/v*.
ALLOWED_OMIT_MARKERS = (
    "iwxxm_xsd/v",
    "tests/",
    "/tests",
    "test_*.py",
    "__main__.py",
    "conftest.py",
)


@dataclass
class Finding:
    """One audit failure."""

    member: str
    message: str


@dataclass
class Audit:
    """Accumulated audit result."""

    findings: list[Finding] = field(default_factory=list)

    def fail(self, member: str, message: str) -> None:
        """Record a failure for ``member``."""
        self.findings.append(Finding(member, message))

    @property
    def ok(self) -> bool:
        """Return True when no failure has been recorded."""
        return not self.findings


def load_toml(path: Path) -> dict[str, Any]:
    """Return parsed TOML from ``path``."""
    with path.open("rb") as handle:
        return tomllib.load(handle)


def workspace_members(root: Path = ROOT) -> list[str]:
    """Return workspace member dirs (posix, relative to ``root``) with Python src."""
    data = load_toml(root / "pyproject.toml")
    members = data.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])
    return [
        m
        for m in members
        if (root / m / "pyproject.toml").is_file() and (root / m / "src").is_dir()
    ]


def coverage_section(member_toml: dict[str, Any], key: str) -> dict[str, Any]:
    """Return ``[tool.coverage.<key>]`` from a parsed member pyproject."""
    section: dict[str, Any] = (
        member_toml.get("tool", {}).get("coverage", {}).get(key, {})
    )
    return section


def omit_patterns(member_toml: dict[str, Any]) -> list[str]:
    """Return omit patterns from both ``coverage.run`` and ``coverage.report``."""
    patterns: list[str] = []
    for key in ("run", "report"):
        patterns.extend(
            str(p) for p in coverage_section(member_toml, key).get("omit", [])
        )
    return patterns


def is_allowed_omit(pattern: str) -> bool:
    """Return True if ``pattern`` only hides generated or test files."""
    return any(marker in pattern for marker in ALLOWED_OMIT_MARKERS)


def check_omit_policy(member: str, member_toml: dict[str, Any], audit: Audit) -> None:
    """Fail on whole-file omits of hand-written code."""
    for pattern in omit_patterns(member_toml):
        if not is_allowed_omit(pattern):
            audit.fail(member, f"hand-written whole-file omit not allowed: {pattern!r}")


def source_dirs(member_dir: Path, member_toml: dict[str, Any]) -> list[Path]:
    """Return on-disk dirs named by ``[tool.coverage.run] source`` (else ``src``)."""
    run = coverage_section(member_toml, "run")
    entries = [str(s) for s in run.get("source", [])] or ["src"]
    pkgs = [str(s) for s in run.get("source_pkgs", [])]
    dirs = [member_dir / e for e in entries if (member_dir / e).is_dir()]
    for pkg in pkgs:
        dirs.extend(
            p for p in (member_dir / "src").glob(pkg.replace(".", "/")) if p.is_dir()
        )
    return dirs


def expected_files(member_dir: Path, member_toml: dict[str, Any]) -> set[str]:
    """Return posix paths (relative to ``member_dir``) of measurable source files."""
    patterns = omit_patterns(member_toml)
    result: set[str] = set()
    for src in source_dirs(member_dir, member_toml):
        for path in src.rglob("*.py"):
            rel = path.relative_to(member_dir).as_posix()
            if "__pycache__" in rel or ".egg-info" in rel:
                continue
            if any(
                fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(f"/{rel}", p)
                for p in patterns
            ):
                continue
            result.add(rel)
    return result


def measured_files(report: dict[str, Any], member_dir: Path) -> set[str]:
    """Return posix paths of files in a coverage JSON report, relative to ``member_dir``."""
    out: set[str] = set()
    for raw in report.get("files", {}):
        path = Path(raw)
        if path.is_absolute():
            try:
                path = path.relative_to(member_dir.resolve())
            except ValueError:
                continue
        out.add(path.as_posix())
    return out


def check_report(
    member: str,
    report: dict[str, Any],
    member_dir: Path,
    audit: Audit,
    known_gaps: frozenset[str] = frozenset(),
) -> None:
    """Check one coverage JSON report against its member tree."""
    files = report.get("files", {})
    if not files:
        audit.fail(member, "coverage report has no files (empty denominator)")
        return
    statements = int(report.get("totals", {}).get("num_statements") or 0)
    if statements <= 0:
        audit.fail(
            member,
            "coverage report has zero statements (fail_under would pass vacuously)",
        )
        return
    member_toml = load_toml(member_dir / "pyproject.toml")
    missing = sorted(
        expected_files(member_dir, member_toml) - measured_files(report, member_dir)
    )
    for rel in missing:
        if f"{member}/{rel}" in known_gaps:
            continue
        audit.fail(member, f"source file missing from denominator: {rel}")


def parse_artifact(spec: str) -> tuple[str, Path]:
    """Split ``MEMBER_DIR=JSON`` into a member key and a JSON path."""
    member, sep, json_path = spec.partition("=")
    if not sep or not member or not json_path:
        msg = f"--artifact expects MEMBER_DIR=JSON_PATH, got {spec!r}"
        raise ValueError(msg)
    return member.strip("/"), Path(json_path)


def run_audit(
    artifacts: list[str],
    members: list[str] | None,
    *,
    omits_only: bool,
    known_gaps: frozenset[str] = frozenset(),
    root: Path = ROOT,
) -> Audit:
    """Run all checks and return the accumulated audit."""
    audit = Audit()
    expected = members or workspace_members(root)
    for member in expected:
        check_omit_policy(member, load_toml(root / member / "pyproject.toml"), audit)
    if omits_only:
        return audit

    seen: set[str] = set()
    for spec in artifacts:
        member, json_path = parse_artifact(spec)
        seen.add(member)
        if not json_path.is_file():
            audit.fail(member, f"coverage artifact not found: {json_path}")
            continue
        report = json.loads(json_path.read_text(encoding="utf-8"))
        check_report(member, report, root / member, audit, known_gaps)
    for member in expected:
        if member not in seen:
            audit.fail(member, "no coverage artifact supplied for expected member")
    return audit


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return the process exit status."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--artifact", action="append", default=[], metavar="MEMBER_DIR=JSON"
    )
    parser.add_argument(
        "--member",
        action="append",
        default=None,
        help="restrict the expected member set",
    )
    parser.add_argument(
        "--known-gap",
        action="append",
        default=[],
        metavar="REPO_PATH",
        help="explicitly accepted missing file (repo-relative); must be tracked in an issue",
    )
    parser.add_argument(
        "--omits-only", action="store_true", help="only audit omit policy"
    )
    args = parser.parse_args(argv)
    if not args.omits_only and not args.artifact:
        parser.error("supply --artifact MEMBER_DIR=JSON (or --omits-only)")
    try:
        audit = run_audit(
            args.artifact,
            args.member,
            omits_only=args.omits_only,
            known_gaps=frozenset(args.known_gap),
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for finding in audit.findings:
        print(f"FAIL [{finding.member}] {finding.message}", file=sys.stderr)
    if audit.ok:
        print("coverage denominator audit PASS")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
