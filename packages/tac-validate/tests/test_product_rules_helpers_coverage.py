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


def test_weather_token_rejects_sign_only_after_shape_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_validate.product_rules_pkg import _common

    fake_shape = type("_Shape", (), {"fullmatch": staticmethod(lambda _token: True)})()
    monkeypatch.setattr(_common, "_WX_TOKEN_SHAPE", fake_shape)

    assert _common._is_valid_weather_token("+") is False


def test_weather_candidates_skip_without_wind() -> None:
    assert _weather_candidate_tokens(["METAR", "KJFK", "101200Z"]) == []
    assert _weather_candidate_tokens(["18008KT"]) == []


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

    tl_only = _check_us_faa_nws_taf(
        ["TAF", "TEMPO", "TL1200"],
        product="TAF",
        core="",
        body_start=0,
        body_end=10,
        profile="iwxxm_us",
    )
    assert not any(i.code == "US_TAF_TEMPO_MAX_4H" for i in tl_only)
    unknown_window = _check_us_faa_nws_taf(
        ["TAF", "TEMPO", "UNKNOWN"],
        product="TAF",
        core="",
        body_start=0,
        body_end=10,
        profile="iwxxm_us",
    )
    assert not any(i.code == "US_TAF_TEMPO_MAX_4H" for i in unknown_window)


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
    tca_nil_cb = "TC ADVISORY\nCB: NIL\n"
    assert _check_us_faa_nws_tca_overlay(tca_nil_cb, profile="iwxxm_us") == []

    swxa_effect = "SWX ADVISORY\nDTG: 20201108/0100Z\nSWXC: DONLON\nSWX EFFECT: SATCOM\n"
    effect_issues = _check_us_faa_nws_swxa_overlay(swxa_effect, start=0, profile="iwxxm_us")
    assert any(i.code == "US_SWXA_SATCOM_NOT_ISSUED" for i in effect_issues)
    assert _check_us_faa_nws_swxa_overlay("SWX ADVISORY\n", start=0, profile="iwxxm_us") == []

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

    with patch.object(membership, "is_member", return_value=True):
        mod_issues = _check_swxa_spacewx_membership(
            "SWX EFFECT: HF COM\nOBS SWX: 08/0100Z MOD HF COM\n",
            start=0,
        )
    assert mod_issues == []
    no_severity = _check_swxa_spacewx_membership(
        "SWX EFFECT: HF COM\nOBS SWX: 08/0100Z HF COM\n",
        start=0,
    )
    assert no_severity == []


def test_vona_onset_and_dur_non_nil_skip_info() -> None:
    tac = "VONA ADVISORY\nDTG: 20201108/0100Z\nSVO: WASHINGTON\nVOLCANO: MOUNT TEST\nONSET: 20201108/0100Z\nDUR: 6 HR\n"
    codes = {i.code for i in check_product_rules(tac, "VONA")}
    assert "VONA_ONSET_NIL" not in codes
    assert "VONA_DUR_NIL" not in codes


def test_common_helper_remaining_empty_and_fallback_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_validate.product_rules_pkg import _common

    ca_issues = _common._check_ca_manobs(
        ["XSM", "P6SM", "RMK", "PRESFR"],
        product="METAR",
        core="XSM P6SM RMK PRESFR",
        body_start=0,
        body_end=20,
        profile="ca_eccc",
    )
    assert {"CA_STATUTE_MILE_VIS", "CA_REMARK_PRESFR"}.issubset({issue.code for issue in ca_issues})

    assert (
        _common._check_ca_manair(
            [],
            product="TAF",
            core="",
            body_start=0,
            body_end=0,
            profile="ca_eccc",
        )
        == []
    )
    assert (
        _common._check_ca_gfa_airmet(
            product="AIRMET",
            core="",
            body_start=0,
            body_end=0,
            profile="ca_eccc",
        )
        == []
    )
    assert _common._forecast_or_obs_segments(["TEMPO"]) == [["TEMPO"]]
    assert _common._forecast_or_obs_segments([]) == []

    monkeypatch.setattr(_common, "_token_span_in_core", lambda *_args: None)
    issues: list[Issue] = []
    _common._emit_nsc_layer_exclusivity(
        issues,
        product="METAR",
        tokens=["NSC", "BKN020"],
        core="unrelated",
        body_start=3,
        body_end=12,
    )
    assert issues[0].start == 3
    assert issues[0].end == 12

    assert _common._check_metar_speci_field_order(["METAR"], product="METAR", start=0, end=5) is None


def test_sigmet_airmet_remaining_noop_paths() -> None:
    from tac_validate.product_rules_pkg import sigmet_airmet

    g2 = sigmet_airmet._check_sigmet_g2(start=0, end=4, upper="TEST")
    assert not any(issue.code in {"SIGMET_SEQUENCE", "MISSING_SEQUENCE"} for issue in g2)
    airmet = sigmet_airmet._check_airmet_a1(start=0, end=6, upper="AIRMET")
    assert not any(issue.code in {"SIGMET_SEQUENCE", "MISSING_SEQUENCE"} for issue in airmet)
    assert not any(issue.code == "FIR_OR_CTA" for issue in airmet)

    no_intensity = sigmet_airmet._check_airmet_a2(start=0, end=6, upper="AIRMET OBS STNR")
    assert not any(issue.code == "INTENSITY_CHANGE" for issue in no_intensity)

    assert sigmet_airmet._check_sigmet_v1(start=0, end=4, upper="TEST") == []
    cancelled_va = sigmet_airmet._check_sigmet_v1(start=0, end=20, upper="SIGMET VA CNL")
    assert not any(issue.code == "MISSING_VA_VOLCANO" for issue in cancelled_va)

    assert sigmet_airmet._check_sigmet_tc(start=0, end=4, upper="TEST") == []
    bare_tc = sigmet_airmet._check_sigmet_tc(start=0, end=8, upper="SIGMET TC")
    assert bare_tc == []

    other_product = sigmet_airmet._check_sigmet_airmet("TEST=", "VAA")
    assert isinstance(other_product, list)
