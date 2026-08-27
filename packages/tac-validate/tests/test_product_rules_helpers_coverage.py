"""Coverage gaps for product_rules helpers (F15 CI cov-fail-under=95)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from tac_validate import membership
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
from tac_validate.product_rules_pkg.swxa import _check_swxa_spacewx_membership
from tac_validate.product_rules_pkg.taf import _check_us_faa_nws_taf
from tac_validate.product_rules_pkg.tca import _check_us_faa_nws_swxa_overlay, _check_us_faa_nws_tca_overlay


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


def test_us_faa_nws_taf_overlay_rules() -> None:
    tokens = ["TAF", "KJFK", "231730Z", "2318/2418", "24008KT", "9999", "BKN020", "BECMG", "2322/2400", "24015KT"]
    becmg = _check_us_faa_nws_taf(
        tokens,
        product="TAF",
        core="",
        body_start=0,
        body_end=10,
        profile="iwxxm_us",
    )
    assert any(i.code == "US_TAF_BECMG_FORBIDDEN" for i in becmg)
    assert _check_us_faa_nws_taf(tokens, product="TAF", core="", body_start=0, body_end=10, profile="annex3") == []

    tempo_tokens = [
        "TAF",
        "KJFK",
        "231730Z",
        "2318/2418",
        "24008KT",
        "9999",
        "BKN020",
        "TEMPO",
        "1606/1612",
        "4000",
        "-RA",
    ]
    tempo = _check_us_faa_nws_taf(
        tempo_tokens,
        product="TAF",
        core="",
        body_start=0,
        body_end=10,
        profile="iwxxm_us",
    )
    assert any(i.code == "US_TAF_TEMPO_MAX_4H" for i in tempo)


def test_metar_nil_auto_and_cor_emit_info() -> None:
    tac = "METAR KJFK 101851Z AUTO COR NIL="
    codes = {i.code for i in check_product_rules(tac, "METAR")}
    assert {"AUTO_PRESENT", "COR_PRESENT"}.issubset(codes)


def test_metar_present_weather_membership_and_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tac_validate.product_rules_pkg.metar_speci._weather_in_register",
        lambda _token: False,
    )
    tac = "METAR KJFK 121255Z 18008KT 10SM TSRA SCT040 22/18 A2992="
    membership_issues = [i for i in check_product_rules(tac, "METAR") if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert membership_issues
    assert any("present_or_forecast_weather" in i.message for i in membership_issues)

    invalid_tac = "METAR KJFK 121255Z 18008KT 10SM ZZWX SCT040 22/18 A2992="
    invalid = check_product_rules(invalid_tac, "METAR")
    assert any(i.code == "INVALID_WEATHER" for i in invalid)


def test_metar_cloud_membership_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    real_is_member = membership.is_member

    def fake_is_member(family: str, token: str, sets=None) -> bool:
        if family == "cloud_amount" and token == "BKN":
            return False
        if family == "cloud_type" and token == "CB":
            return False
        return real_is_member(family, token, sets=sets)

    monkeypatch.setattr("tac_validate.product_rules_pkg.metar_speci.membership.is_member", fake_is_member)
    amount_tac = "METAR KJFK 121255Z 18008KT 10SM BKN020 22/18 A2992="
    amount_issues = [i for i in check_product_rules(amount_tac, "METAR") if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert amount_issues

    type_tac = "METAR KJFK 121255Z 18008KT 10SM BKN020CB 22/18 A2992="
    type_issues = [i for i in check_product_rules(type_tac, "METAR") if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert type_issues


def test_us_faa_nws_tca_and_swxa_overlays() -> None:
    tca_no_cb = "TC ADVISORY\nDTG: 20040925/1800Z\nTCAC: MIAMI\nTC: IDA\n"
    assert _check_us_faa_nws_tca_overlay(tca_no_cb, profile="iwxxm_us") == []

    tca_cb = "TC ADVISORY\nDTG: 20040925/1800Z\nTCAC: MIAMI\nTC: IDA\nCB: OBSERVED\n"
    tca_issues = _check_us_faa_nws_tca_overlay(tca_cb, profile="iwxxm_us")
    assert any(i.code == "US_TCA_OBSERVED_CB_NOT_PROVIDED" for i in tca_issues)

    swxa_effect = "SWX ADVISORY\nDTG: 20201108/0100Z\nSWXC: DONLON\nSWX EFFECT: SATCOM\n"
    effect_issues = _check_us_faa_nws_swxa_overlay(swxa_effect, start=0, profile="iwxxm_us")
    assert any(i.code == "US_SWXA_SATCOM_NOT_ISSUED" for i in effect_issues)

    swxa_obs = (
        "SWX ADVISORY\nDTG: 20201108/0100Z\nSWXC: DONLON\nSWX EFFECT: HF COM\nOBS SWX: 08/0100Z SATCOM MOD IONOSPHERE\n"
    )
    obs_issues = _check_us_faa_nws_swxa_overlay(swxa_obs, start=0, profile="iwxxm_us")
    assert any(i.code == "US_SWXA_SATCOM_NOT_ISSUED" for i in obs_issues)


def test_swxa_spacewx_membership_branches() -> None:
    assert _check_swxa_spacewx_membership("DTG: 20201108/0100Z\nSWXC: DONLON\n", start=0) == []

    with patch.object(membership, "is_member", return_value=False):
        issues = _check_swxa_spacewx_membership(
            "DTG: 20201108/0100Z\nSWXC: DONLON\nSWX EFFECT: HF COM\nOBS SWX: 08/0100Z SEV HF COM\n",
            start=0,
        )
    assert any(i.code == "UNKNOWN_WMO_MEMBERSHIP" for i in issues)


def test_vona_onset_and_dur_non_nil_skip_info() -> None:
    tac = "VONA ADVISORY\nDTG: 20201108/0100Z\nSVO: WASHINGTON\nVOLCANO: MOUNT TEST\nONSET: 20201108/0100Z\nDUR: 6 HR\n"
    codes = {i.code for i in check_product_rules(tac, "VONA")}
    assert "VONA_ONSET_NIL" not in codes
    assert "VONA_DUR_NIL" not in codes
