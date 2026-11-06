"""EV-regional-profile-remainder — C1/C2/C4/C5/C6/C7 fixtures.

[Corpus: product §F15/§F20/§F23/§F36] [Corpus: adr/ADR-046]
[Corpus: tests §TC-EV-RPR-001..007]
"""

from __future__ import annotations

from tac_validate.api import lint, lint_with_profile
from tac_validate.product_rules_pkg._common import _check_r8_pack
from tac_validate.product_rules_pkg.sigmet_airmet import (
    _check_airmet_a2,
    _is_us_domestic_ws_sigmet,
)
from tac_validate.quality_policy_bind import resolve_tac_quality_policy_id
from tac_validate.station_scoped_policy import resolve_profile_for_station

_PTRO_TAF = "TAF PTRO 011200Z 0112/0212 09010KT P6SM SCT020 PROB30 0118/0122 3SM BR="
_YSSY_TAF = "TAF YSSY 011200Z 0112/0218 18012KT 9999 SCT025 PROB30 0118/0122 4000 SHRA BKN012="
_YCFS_METAR = "METAR YCFS 011300Z AUTO 16008KT 9999 // SCT020 21/// Q1016="
_FNUE_METAR = "METAR FNUE 010100Z AUTO /////KT //// ////// ///// Q////="
_ULOO_SPECI = "SPECI ULOO 311523Z 35002MPS 9999 FEW015 BKN046 08/07 Q1029 R19/010060 RMK QFE767"
_HABANA = (
    "WSCU31 MUHA 312045\n"
    "MUFH SIGMET 3 VALID 312045/010045 MUHA-\n"
    "MUFH HABANA FIR EMBD TS OBS AT 2045Z WI N2300 W08200 - N2200 W08100 - "
    "N2200 W08230 - N2300 W08200 CB TOP FL480 MOV STNR INTSF="
)
_INDIA = (
    "WSIN31 VOMM 311315\n"
    "VOMM SIGMET 2 VALID 311315/311715 VOMM-\n"
    "CHENNAI FIR EMBD TS OBS AT 1315Z WI N1200 E08000 - N1100 E08100 - "
    "N1100 E08000 - N1200 E08000 TOP FL550 MOV N STNR NC="
)
_YANKEE = """\
WSUS06 KKCI 312208
SFOY WS 312208
SIGMET YANKEE 1 VALID UNTIL 010208
WA OR CA CSTL WTRS
FROM 20NW TOU TO 30NNW ONP TO 150W ENI TO 140WSW FOT TO 110WNW
ONP TO 130W TOU TO 20NW TOU
OCNL SEV TURB BTN FL210 AND FL290. DUE TO WNDSHR ASSOCD WITH
JTST. RPTD BY ACFT. CONDS CONTG BYD 0208Z.
"""
_NOVEMBER = """\
WSUS06 KKCI 312322
SFON WS 312322
SIGMET NOVEMBER 1 VALID UNTIL 010322
CA NV AND CSTL WTRS
FROM 50NW BAM TO 40SW FMG TO 50SE OAL TO 70SW BAM TO 50NW BAM
OCNL SEV TURB BTN FL180 AND FL280. RPTD BY ACFT.
"""
_INTL = "YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD FIR OBSC TS FCST="


def test_c1_ptro_ptsa_exact_prefer() -> None:
    assert resolve_profile_for_station("PTRO") == "iwxxm_us"
    assert resolve_profile_for_station("PTSA") == "iwxxm_us"
    assert resolve_profile_for_station("PTKK") is None
    report = lint_with_profile(_PTRO_TAF, product="TAF", profile="annex3")
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
    assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)


def test_c2_y_prefix_au_bom_prob_info() -> None:
    assert resolve_profile_for_station("YSSY") == "au_bom"
    assert resolve_profile_for_station("YCFS") == "au_bom"
    assert resolve_tac_quality_policy_id("au_bom", product="TAF") == "taf-prob-period-info-quality"
    report = lint_with_profile(_YSSY_TAF, product="TAF", profile="annex3")
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
    assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)


def test_c4_ycfs_dewpoint_nil_info() -> None:
    report = lint(_YCFS_METAR, product="METAR")
    assert any(i.code == "DEWPOINT_NOT_OBSERVABLE" and i.severity == "info" for i in report.issues)
    assert not any(i.code == "MISSING_TEMP_DEWPOINT" for i in report.issues)


def test_c4_fnue_all_solidus_stays_missing() -> None:
    report = lint(_FNUE_METAR, product="METAR")
    assert any(i.code == "MISSING_TEMP_DEWPOINT" and i.severity == "error" for i in report.issues)
    assert not any(i.code == "DEWPOINT_NOT_OBSERVABLE" for i in report.issues)


def test_c5_cis_runway_state_skips_rvr_in_r8_pack() -> None:
    """CIS Rxx/dddddd must take the runway-state continue path in R8."""
    issues = _check_r8_pack(
        ["R19/010060", "R04L/010062"],
        product="METAR",
        core="R19/010060 R04L/010062",
        body_start=0,
        body_end=24,
    )
    assert not any(i.code in {"INVALID_RVR", "RVR_PRESENT"} for i in issues)
    assert "INVALID_RVR" not in {i.code for i in lint(_ULOO_SPECI, product="SPECI").issues}


def test_c6_habana_mov_stnr_info() -> None:
    report = lint(_HABANA, product="SIGMET")
    assert any(i.code == "STNR_MOVEMENT" for i in report.issues)
    assert not any(i.code == "INVALID_STNR_MOVEMENT" for i in report.issues)


def test_c6_airmet_mov_stnr_info() -> None:
    """AIRMET MOV STNR (no direction) is stationary info, not INVALID_STNR_MOVEMENT."""
    issues = _check_airmet_a2(start=0, end=40, upper="AIRMET ISOL TS OBS MOV STNR WKN")
    codes = {i.code for i in issues}
    assert "STNR_MOVEMENT" in codes
    assert "INVALID_STNR_MOVEMENT" not in codes
    tac = "YUDD AIRMET 1 VALID 101200/101600 YUSO- YUDD SHANLON FIR MOD ICE FCST S OF N54 TOP FL150 MOV STNR NC="
    report = lint(tac, product="AIRMET")
    assert any(i.code == "STNR_MOVEMENT" for i in report.issues)
    assert not any(i.code == "INVALID_STNR_MOVEMENT" for i in report.issues)


def test_c6_india_mov_n_stnr_error() -> None:
    report = lint(_INDIA, product="SIGMET")
    assert any(i.code == "INVALID_STNR_MOVEMENT" and i.severity == "error" for i in report.issues)


def test_c7_us_domestic_ws_clears_triad() -> None:
    for tac in (_YANKEE, _NOVEMBER):
        report = lint(tac, product="SIGMET", profile="annex3")
        codes = {i.code for i in report.issues if i.severity == "error"}
        assert "MISSING_VALID" not in codes
        assert "MISSING_FIR_OR_CTA" not in codes
        assert "MISSING_OBS_OR_FCST" not in codes


def test_c7_us_domestic_ws_missing_valid_until() -> None:
    tac = "WSUS06 KKCI 312208\nSFOY WS 312208\nSIGMET YANKEE 1\nWA OR CA CSTL WTRS\n"
    report = lint(tac, product="SIGMET", profile="annex3")
    assert any(i.code == "MISSING_VALID" for i in report.issues)
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert "MISSING_FIR_OR_CTA" not in codes
    assert "MISSING_OBS_OR_FCST" not in codes


def test_c7_international_still_needs_valid() -> None:
    report = lint("SIGMET =", product="SIGMET", profile="annex3")
    assert any(i.code == "MISSING_VALID" for i in report.issues)


def test_c7_international_valid_ok() -> None:
    report = lint(_INTL, product="SIGMET", profile="annex3")
    assert not any(i.code == "MISSING_VALID" for i in report.issues)


def test_c7_tc_phonetic_series_with_icao_valid_not_domestic_gate() -> None:
    """TC SIGMET TANGO + VALID ddhhmm/ddhhmm must not short-circuit to domestic WS."""
    tac = (
        "WCPA07 PHFO 300118\n\n"
        "KZAK SIGMET TANGO 31 VALID 300120/300720 PHFO-\n"
        "OAKLAND OCEANIC FIR TC IN-FA OBS AT 0000Z N1755 E14750. CB TOP FL520 "
        "WI 160NM OF CENTER. MOV WNW 18KT. NC. FCST 0600Z TC CENTER N1840 E14610."
    )
    report = lint(tac, product="SIGMET")
    codes = {i.code for i in report.issues}
    assert "TC_CYCLONE_IDENTITY" in codes
    assert "MISSING_VALID" not in codes


def test_c7_domestic_gate_excludes_convective_and_hazard_tokens() -> None:
    """Direct shape helper: convective / TC / VA never classify as domestic WS."""
    assert _is_us_domestic_ws_sigmet("CONVECTIVE SIGMET 47E VALID UNTIL 2355Z") is False
    assert _is_us_domestic_ws_sigmet("SIGMET TANGO 1 TC IN-FA OBS") is False
    assert _is_us_domestic_ws_sigmet("SIGMET TANGO 1 VA ERUPTION") is False
    assert _is_us_domestic_ws_sigmet("WSUS06 KKCI SIGMET YANKEE 1") is True
