"""Regression test: Playwright coverage meets the 100% statement floor.

Fails while ``apps/e2e/coverage/coverage-final.json`` is missing, statement
coverage is under 100%, or the report has no branch data. The load-only
collector currently writes 9.50% statements and empty branch maps.
Passes once a run records every statement and at least one branch.
[Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "apps" / "e2e" / "coverage" / "coverage-final.json"


def _statement_and_branch_counts(report: dict[str, object]) -> tuple[int, int, int]:
    statements = 0
    covered = 0
    branches = 0
    for entry in report.values():
        if not isinstance(entry, dict):
            continue
        statement_hits = entry.get("s")
        if isinstance(statement_hits, dict):
            statements += len(statement_hits)
            covered += sum(1 for hits in statement_hits.values() if hits)
        branch_hits = entry.get("b")
        if isinstance(branch_hits, dict):
            for slots in branch_hits.values():
                if isinstance(slots, list):
                    branches += len(slots)
    return statements, covered, branches


def test_e2e_coverage_report_meets_statement_floor() -> None:
    """apps/e2e Istanbul report is present at 100% statements with branch data."""
    assert REPORT.is_file(), f"missing Playwright coverage report: {REPORT}"
    loaded: object = json.loads(REPORT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), "Playwright coverage report is not an object"
    statements, covered, branches = _statement_and_branch_counts(loaded)
    assert statements > 0, "Playwright coverage report has no statements"
    percent = 100 * covered / statements
    assert covered == statements, (
        "Playwright statement coverage is "
        f"{percent:.2f}% ({covered}/{statements}), under the 100% floor (#1448 / G2)"
    )
    assert branches > 0, "Playwright coverage report has no branch data (#1448 / G2)"
