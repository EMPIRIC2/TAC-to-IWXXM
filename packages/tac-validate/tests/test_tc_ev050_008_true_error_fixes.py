"""TC-EV050-008 / AC8 — true-error profile fixes + regressions (S059)."""

from __future__ import annotations

import json
from pathlib import Path

from tac_validate import lint
from tac_validate.dual_profile import compare_lint_profiles

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))


def _remark_info_cases() -> list[dict[str, object]]:
    return list(MANIFEST.get("remark_us_info", []))


def test_remark_us_extension_only_under_iwxxm_us() -> None:
    """True-error fix: annex3 must not emit US-profile awareness info."""
    cases = _remark_info_cases()
    assert cases, "expected remark_us_info fixtures"
    case = cases[0]
    tac = (FIXTURES / str(case["tac"])).read_text(encoding="utf-8")
    product = str(case["product"])

    annex3 = lint(tac, product=product, profile="annex3")
    us = lint(tac, product=product, profile="iwxxm_us")
    assert "REMARK_US_EXTENSION" not in {i.code for i in annex3.issues}
    assert "REMARK_US_EXTENSION" in {i.code for i in us.issues}

    result = compare_lint_profiles(tac, product=product)
    assert result.disposition == "dual"
    assert result.ok, result.note
    assert "REMARK_US_EXTENSION" in result.divergent_codes
    assert "REMARK_US_EXTENSION" not in result.unclassified_divergent


def test_invalid_remark_still_errors_under_both_profiles() -> None:
    errors = list(MANIFEST.get("remark_errors", []))
    assert errors
    case = errors[0]
    tac = (FIXTURES / str(case["tac"])).read_text(encoding="utf-8")
    product = str(case["product"])
    for profile in ("annex3", "iwxxm_us"):
        report = lint(tac, product=product, profile=profile)
        assert report.ok is False
        assert "INVALID_REMARK" in {i.code for i in report.issues if i.severity == "error"}
