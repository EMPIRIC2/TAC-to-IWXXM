"""Regression test: apps/e2e has a coverage report.

Fails while the Playwright tree has no Istanbul or coverage.py report.
Passes once one of the usual report files is present. [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E2E = ROOT / "apps" / "e2e"

_REPORTS = (
    E2E / "coverage-final.json",
    E2E / "coverage" / "coverage-final.json",
    E2E / "coverage.json",
    E2E / "coverage.xml",
    E2E / ".coverage",
)


def test_qa_gap_e2e_has_a_coverage_report() -> None:
    """apps/e2e publishes an Istanbul or coverage.py report."""
    present = [path.relative_to(ROOT).as_posix() for path in _REPORTS if path.is_file()]
    assert present, (
        "apps/e2e has no coverage report "
        "(coverage-final.json, coverage/coverage-final.json, coverage.json, "
        "coverage.xml, or .coverage)"
    )
