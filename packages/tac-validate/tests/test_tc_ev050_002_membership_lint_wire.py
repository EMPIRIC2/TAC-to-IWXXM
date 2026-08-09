"""TC-EV050-002 / AC2 — membership wired into lint (stable issue codes).

S059 / EV-050 T2.2: recent weather, AIRMET underscore↔space normalize, cloud type,
and unknown/sad tokens emit ``UNKNOWN_WMO_MEMBERSHIP``.
"""

from __future__ import annotations

from tac_validate import lint, membership
from tac_validate.issue_registry import by_code


def test_unknown_wmo_membership_registered() -> None:
    spec = by_code("UNKNOWN_WMO_MEMBERSHIP")
    assert spec.severity == "error"
    assert "membership" in spec.tags or "wmo" in spec.tags


def test_normalize_register_notation_airmet_space_to_underscore() -> None:
    assert membership.normalize_register_notation("ISOL TS") == "ISOL_TS"
    assert membership.normalize_register_notation("ISOL_TS") == "ISOL_TS"
    assert membership.is_member_normalized("airwx_phenomena", "ISOL TS")
    assert membership.is_member_normalized("airwx_phenomena", "ISOL_TS")
    assert not membership.is_member_normalized("airwx_phenomena", "ISOL ZZ")


def test_lint_recent_weather_happy_rera() -> None:
    tac = "METAR KJFK 121255Z 18008KT 10SM RERA SCT040 22/18 A2992="
    report = lint(tac, product="METAR")
    codes = {i.code for i in report.issues}
    assert "INVALID_WEATHER" not in codes
    assert "UNKNOWN_WMO_MEMBERSHIP" not in codes
    assert report.ok


def test_lint_recent_weather_sad_emits_membership() -> None:
    tac = "METAR KJFK 121255Z 18008KT 10SM REZZZZ SCT040 22/18 A2992="
    report = lint(tac, product="METAR")
    membership_issues = [i for i in report.issues if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert membership_issues
    assert any("recent_weather" in i.message for i in membership_issues)
    assert not report.ok


def test_lint_present_weather_sad_still_invalid_or_membership() -> None:
    tac = "METAR KJFK 121255Z 18008KT 10SM ZZWX SCT040 22/18 A2992="
    report = lint(tac, product="METAR")
    codes = {i.code for i in report.issues}
    assert "INVALID_WEATHER" in codes or "UNKNOWN_WMO_MEMBERSHIP" in codes
    assert not report.ok


def test_lint_cloud_tcu_happy() -> None:
    tac = "SPECI KJFK 121255Z 18008KT 10SM BKN020TCU 22/18 A2992="
    report = lint(tac, product="SPECI")
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert "UNKNOWN_WMO_MEMBERSHIP" not in codes
    assert "INVALID_CLOUD_TOKEN" not in codes


def test_lint_airmet_spaced_phenomenon_membership_ok() -> None:
    tac = "YUDD AIRMET 1 VALID 151520/151800 YUSO-\nYUDD SHANLON FIR ISOL TS OBS N OF S50 TOP ABV FL100 STNR WKN="
    report = lint(tac, product="AIRMET")
    assert "UNKNOWN_WMO_MEMBERSHIP" not in {i.code for i in report.issues}
    assert report.ok or not any(i.severity == "error" for i in report.issues)


def test_lint_airmet_underscore_phenomenon_membership_ok() -> None:
    tac = "YUDD AIRMET 1 VALID 151520/151800 YUSO-\nYUDD SHANLON FIR ISOL_TS OBS N OF S50 TOP ABV FL100 STNR WKN="
    report = lint(tac, product="AIRMET")
    codes = {i.code for i in report.issues}
    assert "UNKNOWN_WMO_MEMBERSHIP" not in codes
    err = [i for i in report.issues if i.severity == "error"]
    assert not err, err


def test_lint_airmet_unknown_phenomenon_membership() -> None:
    tac = "YUDD AIRMET 1 VALID 151520/151800 YUSO-\nYUDD SHANLON FIR ISOL_ZZ OBS N OF S50 TOP ABV FL100 STNR WKN="
    report = lint(tac, product="AIRMET")
    membership_issues = [i for i in report.issues if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert membership_issues
    assert any("airwx_phenomena" in i.message for i in membership_issues)
    assert not report.ok


def test_lint_sigmet_va_membership_ok() -> None:
    tac = (
        "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
        "YUDD FIR VA OBS AT 1200Z WI N2000 E12000 - N2100 E12100 FL100/200 MOV E 20KT="
    )
    report = lint(tac, product="SIGMET")
    assert "UNKNOWN_WMO_MEMBERSHIP" not in {i.code for i in report.issues}
