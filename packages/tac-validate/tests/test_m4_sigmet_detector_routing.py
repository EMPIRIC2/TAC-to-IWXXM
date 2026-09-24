"""M4 SIGMET detector routing coverage (#1230)."""

from __future__ import annotations

import pytest
from tac_validate.api import lint
from tac_validate.product_rules import check_product_rules

_MINIMAL_SIGMET = "YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD OBSC TS FCST="


def test_sigmet_legacy_mode_uses_check_sigmet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    issues = check_product_rules("SIGMET =", product="SIGMET")
    assert any(i.code == "MISSING_VALID" for i in issues)


def test_sigmet_detector_mode_uses_sigmet_core_pack(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    issues = check_product_rules(_MINIMAL_SIGMET, product="SIGMET")
    assert isinstance(issues, list)
    bad = check_product_rules("SIGMET =", product="SIGMET")
    assert any(i.code == "MISSING_VALID" for i in bad)


_LIVE_CONVECTIVE = """\
WSUS31 KKCI 232155
SIGE
CONVECTIVE SIGMET 47E
VALID UNTIL 2355Z
FL AND CSTL WTRS
FROM 60ESE PBI-140SE MIA-50SW EYW
AREA TS MOV FROM 25010KT. TOPS ABV FL450.
"""


def test_convective_sigmet_does_not_use_international_identity_rules() -> None:
    report = lint(_LIVE_CONVECTIVE, product="SIGMET", profile="annex3")
    codes = {issue.code for issue in report.issues if issue.severity == "error"}
    assert "MISSING_VALID" not in codes
    assert "MISSING_FIR_OR_CTA" not in codes
    assert "MISSING_OBS_OR_FCST" not in codes


def test_convective_sigmet_without_valid_until_is_missing_valid() -> None:
    report = lint(
        "WSUS31 KKCI 232155\nSIGE\nCONVECTIVE SIGMET 47E\nFL AND CSTL WTRS\n",
        product="SIGMET",
        profile="annex3",
    )
    errors = [issue for issue in report.issues if issue.severity == "error"]
    assert any(issue.code == "MISSING_VALID" for issue in errors)
