"""M2 parity baseline - lint codes/severities must match the registry (TC-F12-001 / TC-F15-001).

Pinned before T2.2 migrates ``rules.py`` / ``product_rules.py`` onto ``issue_from``.
Accept + negative fixture packs must stay green through that migration.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tac_validate import lint
from tac_validate.issue_registry import by_code

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _read_tac(rel: str) -> str:
    return (FIXTURES / rel).read_text(encoding="utf-8")


def _case_ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


_MANIFEST = _load_manifest()
_ACCEPT = list(_MANIFEST["accept"])
_NEGATIVE = list(_MANIFEST["negative"])


@pytest.mark.parametrize("case", _ACCEPT, ids=_case_ids(_ACCEPT))
def test_parity_accept_fixtures_remain_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    for issue in report.issues:
        spec = by_code(issue.code)
        assert issue.severity == spec.severity, (issue.code, issue.severity, spec.severity)


@pytest.mark.parametrize("case", _NEGATIVE, ids=_case_ids(_NEGATIVE))
def test_parity_negative_expected_codes_match_registry_severity(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    by_emitted = {i.code: i for i in report.issues}
    for expected in case["expected_codes"]:
        assert expected in by_emitted, f"{case['id']}: missing {expected}"
        issue = by_emitted[expected]
        spec = by_code(expected)
        assert issue.severity == spec.severity, (
            case["id"],
            expected,
            issue.severity,
            spec.severity,
        )


def test_parity_shared_parse_gate_severities() -> None:
    """Shared parse-gate codes keep registry severities (EMPTY_TAC error, terminator info)."""
    empty = lint("", product="METAR")
    empty_issue = next(i for i in empty.issues if i.code == "EMPTY_TAC")
    assert empty_issue.severity == by_code("EMPTY_TAC").severity == "error"

    no_term = lint(
        "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034",
        product="METAR",
    )
    term = next(i for i in no_term.issues if i.code == "MISSING_TERMINATOR")
    assert term.severity == by_code("MISSING_TERMINATOR").severity == "info"
