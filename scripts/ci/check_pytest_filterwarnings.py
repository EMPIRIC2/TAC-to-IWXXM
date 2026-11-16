#!/usr/bin/env python3
"""Fail closed when pytest configs tolerate warnings.

 TC-EVDOC-007: every ``pyproject.toml`` that defines
``[tool.pytest.ini_options]`` (or owns a ``tests/`` tree under ``apps/`` /
``packages/`` / repo root) must set ``filterwarnings`` to treat warnings as
errors. Broad ``ignore`` filters are rejected. Mutation-only ``-W`` overrides
live in ``scripts/ci/run_mutation_python.sh`` and are out of scope here.

[Corpus: tech-spec] [Corpus: tests]
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_PYTEST_SECTION = "[tool.pytest.ini_options]"
_FILTERWARNINGS_RE = re.compile(
    r"filterwarnings\s*=\s*\[(?P<body>.*?)\]",
    re.DOTALL,
)


@dataclass(frozen=True)
class Finding:
    """One policy violation."""

    path: Path
    code: str
    message: str


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def iter_candidate_pyprojects(root: Path = ROOT) -> list[Path]:
    """Return root + apps/*/ + packages/*/ pyproject.toml paths that matter."""
    out: list[Path] = []
    root_py = root / "pyproject.toml"
    if root_py.is_file():
        out.append(root_py)
    for base in (root / "apps", root / "packages"):
        if not base.is_dir():
            continue
        for member in sorted(base.iterdir()):
            py = member / "pyproject.toml"
            if py.is_file():
                out.append(py)
    return out


def _member_dir(pyproject: Path, root: Path = ROOT) -> Path | None:
    """Return the app/package directory for a member pyproject, else None."""
    try:
        rel = pyproject.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 3 and parts[0] in {"apps", "packages"}:
        return root / parts[0] / parts[1]
    return None


def requires_pytest_filterwarnings(pyproject: Path, root: Path = ROOT) -> bool:
    """True when this pyproject must declare filterwarnings=error."""
    text = pyproject.read_text(encoding="utf-8")
    if _PYTEST_SECTION in text:
        return True
    if pyproject.resolve() == (root / "pyproject.toml").resolve():
        return True
    member = _member_dir(pyproject, root)
    if member is None:
        return False
    return (member / "tests").is_dir()


def parse_filterwarnings(text: str) -> list[str] | None:
    """Return filterwarnings entries, or None when the table key is absent."""
    if "filterwarnings" not in text:
        return None
    match = _FILTERWARNINGS_RE.search(text)
    if match is None:
        return None
    body = match.group("body")
    entries: list[str] = []
    for raw in body.splitlines():
        line = raw.strip().rstrip(",")
        if not line or line.startswith("#"):
            continue
        if (line.startswith('"') and line.endswith('"')) or (
            line.startswith("'") and line.endswith("'")
        ):
            entries.append(line[1:-1])
        else:
            entries.append(line)
    return entries


def audit_pyproject(pyproject: Path, *, root: Path = ROOT) -> list[Finding]:
    """Audit one pyproject for warnings-as-errors policy."""
    findings: list[Finding] = []
    if not requires_pytest_filterwarnings(pyproject, root):
        return findings
    text = pyproject.read_text(encoding="utf-8")
    if _PYTEST_SECTION not in text:
        findings.append(
            Finding(
                pyproject,
                "missing_pytest_section",
                "has tests/ (or is root) but lacks [tool.pytest.ini_options]",
            )
        )
        return findings
    entries = parse_filterwarnings(text)
    if entries is None:
        findings.append(
            Finding(
                pyproject,
                "missing_filterwarnings",
                "pytest.ini_options present but filterwarnings is missing",
            )
        )
        return findings
    if "error" not in entries:
        findings.append(
            Finding(
                pyproject,
                "missing_error",
                "filterwarnings must include the bare entry 'error'",
            )
        )
    ignores = [e for e in entries if e.startswith("ignore")]
    if ignores:
        findings.append(
            Finding(
                pyproject,
                "forbidden_ignore",
                "filterwarnings ignore entries are not allowed "
                f"({', '.join(ignores)}); fix emitters or use a mutation-local -W",
            )
        )
    return findings


def audit_tree(root: Path = ROOT) -> list[Finding]:
    """Audit all candidate pyprojects under ``root``."""
    findings: list[Finding] = []
    for path in iter_candidate_pyprojects(root):
        findings.extend(audit_pyproject(path, root=root))
    return findings


def main(argv: list[str] | None = None) -> int:
    """CLI entry: exit 0 when all pytest configs treat warnings as errors."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root (default: detected from script path)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    findings = audit_tree(root)
    if not findings:
        print("OK: pytest filterwarnings=['error'] on all required pyprojects")
        return 0
    print("FAIL: pytest warnings-as-errors policy violations:", file=sys.stderr)
    for finding in findings:
        print(
            f"  {_rel(finding.path)}: [{finding.code}] {finding.message}",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
