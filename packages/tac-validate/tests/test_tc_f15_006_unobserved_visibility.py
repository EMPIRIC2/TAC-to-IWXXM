"""TC-F15-006: //// and ////SM are unobserved visibility, not a missing group."""

from __future__ import annotations

from tac_validate import lint

_MKJP = "METAR MKJP 072300Z 12012KT //// ////// 30/26 Q1013 RMK CLD FROM CEILOMETER RWY 30 NCD="
_STATUTE = "METAR MKJP 072300Z AUTO 12012KT ////SM FEW020 30/26 A2992="
_OMITTED = "METAR MKJP 072300Z 12012KT 30/26 Q1013="
_SIX_SLASH = "METAR MKJP 072300Z 12012KT ////// 30/26 Q1013="
_BODY_NCD = "METAR MKJP 072300Z AUTO 12012KT 9999 NCD 30/26 Q1013="


def test_four_slashes_are_not_missing_visibility() -> None:
    report = lint(_MKJP, product="METAR")
    assert not any(issue.code == "MISSING_VISIBILITY" for issue in report.issues)
    assert not any(issue.code == "NCD_PRESENT" for issue in report.issues)


def test_statute_mile_slashes_are_not_missing_visibility() -> None:
    report = lint(_STATUTE, product="METAR")
    assert not any(issue.code == "MISSING_VISIBILITY" for issue in report.issues)


def test_omitted_visibility_is_still_missing() -> None:
    report = lint(_OMITTED, product="METAR")
    assert any(issue.code == "MISSING_VISIBILITY" for issue in report.issues)


def test_six_slashes_are_not_a_visibility_group() -> None:
    report = lint(_SIX_SLASH, product="METAR")
    assert any(issue.code == "MISSING_VISIBILITY" for issue in report.issues)


def test_body_ncd_is_still_noted() -> None:
    report = lint(_BODY_NCD, product="METAR")
    assert any(issue.code == "NCD_PRESENT" for issue in report.issues)
