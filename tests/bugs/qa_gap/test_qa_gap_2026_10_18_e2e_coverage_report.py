"""Regression test: apps/e2e has a coverage report.

Fails while the Playwright tree has no Istanbul or coverage.py report.
Passes once one of the usual report files is present. [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E2E = ROOT / "apps" / "e2e"
WORKFLOW = ROOT / ".github" / "workflows" / "ci-cd.yml"
MAKEFILE = ROOT / "Makefile"

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


def test_qa_gap_1448_ci_publishes_e2e_coverage_artifact() -> None:
    """#1448: bugs CI collects the suite report and uploads e2e-coverage-report."""
    makefile = MAKEFILE.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    missing: list[str] = []
    if "collect-e2e-coverage:" not in makefile:
        missing.append("Makefile missing collect-e2e-coverage target")
    if "scripts/ci/collect_e2e_coverage.mjs" not in makefile:
        missing.append("Makefile collect-e2e-coverage does not invoke the collector")
    if "make collect-e2e-coverage" not in workflow:
        missing.append("ci-cd.yml bugs job does not run make collect-e2e-coverage")
    if "e2e-coverage-report" not in workflow:
        missing.append("ci-cd.yml does not upload e2e-coverage-report")
    if "apps/e2e/coverage/coverage-final.json" not in workflow:
        missing.append(
            "ci-cd.yml upload path omits apps/e2e/coverage/coverage-final.json"
        )
    assert not missing, "; ".join(missing)
