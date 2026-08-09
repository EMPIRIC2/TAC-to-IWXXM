"""Coverage gaps for product_rules helpers (F15 CI cov-fail-under=95)."""

from __future__ import annotations

import pytest

from tac_validate.api import lint
from tac_validate.models import Issue
from tac_validate.product_rules import (
    _append_remark_issue,
    _body_span,
    _is_valid_weather_token,
    _sigmet_validity_hours,
    _weather_candidate_tokens,
    check_product_rules,
)


def test_body_span_whitespace_only() -> None:
    start, end, body = _body_span("   \n")
    assert body == ""
    assert start == 0
    assert end == 4


def test_weather_token_edge_cases() -> None:
    assert _is_valid_weather_token("UP") is True
    assert _is_valid_weather_token("//") is True
    assert _is_valid_weather_token("++RA") is False
    assert _is_valid_weather_token("+-RA") is False
    assert _is_valid_weather_token("+") is False
    assert _is_valid_weather_token("+VCSH") is False
    assert _is_valid_weather_token("RA+") is False
    assert _is_valid_weather_token("XYZ") is False
    assert _is_valid_weather_token("TSRA") is True
    assert _is_valid_weather_token("SHRA") is True
    assert _is_valid_weather_token("-") is False
    # Descriptor-only residual → invalid; multi-phenomenon concatenation → valid.
    assert _is_valid_weather_token("SH") is False
    assert _is_valid_weather_token("RASN") is True
    assert _is_valid_weather_token("FZDZ") is True


def test_weather_candidates_skip_without_wind() -> None:
    assert _weather_candidate_tokens(["METAR", "KJFK", "101200Z"]) == []


def test_sigmet_validity_hours_edges() -> None:
    assert _sigmet_validity_hours("bad", "101200") is None
    assert _sigmet_validity_hours("320000", "010200") is None
    assert _sigmet_validity_hours("312200", "010200") == pytest.approx(4.0)


def test_append_remark_issue_falls_back_when_token_absent() -> None:
    issues: list[Issue] = []
    _append_remark_issue(
        issues,
        code="INVALID_REMARK",
        message="missing token span",
        core="METAR KJFK RMK AO2",
        body_start=0,
        body_end=20,
        token="NOTPRESENT",
    )
    assert issues[0].start == 0
    assert issues[0].end == 20


def test_check_product_rules_unknown_product() -> None:
    assert check_product_rules("METAR KJFK=", "NOTAPRODUCT") == []


def test_taf_nil_with_amd_and_cor_emits_modifiers() -> None:
    report = lint("TAF AMD COR KJFK 231730Z NIL=", product="TAF")
    codes = {i.code for i in report.issues}
    assert "AMD_PRESENT" in codes
    assert "COR_PRESENT" in codes


def test_vaa_empty_volcano_field() -> None:
    tac = "VA ADVISORY\nDTG: 20040925/1900Z\nVAAC: TOKYO\nVOLCANO: \n"
    issues = check_product_rules(tac, "VAA")
    assert any(i.code == "MISSING_VOLCANO" for i in issues)


def test_tca_empty_tc_field() -> None:
    tac = "TC ADVISORY\nDTG: 20040925/1800Z\nTCAC: MIAMI\nTC: \n"
    issues = check_product_rules(tac, "TCA")
    assert any(i.code == "MISSING_TC" for i in issues)


def test_airmet_cnl_short_circuits_families() -> None:
    tac = "YUDD AIRMET 1 VALID 101200/101600 YUSO- YUDD FIR CNL="
    issues = check_product_rules(tac, "AIRMET")
    assert not any(i.code == "MULTIPLE_PHENOMENA" for i in issues)
