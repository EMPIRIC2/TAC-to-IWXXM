"""EV-regional-profile-remainder — C1/C2/C4/C6/C7 fixtures.

[Corpus: product §F15/§F20/§F23/§F36] [Corpus: adr/ADR-046]
[Corpus: tests §TC-EV-RPR-001..007]
"""

from __future__ import annotations

from tac2iwxxm.profile_resolve import resolve_validation_policies
from tac_validate.api import lint, lint_with_profile
from tac_validate.station_scoped_policy import resolve_profile_for_station

_PTRO_TAF = "TAF PTRO 011200Z 0112/0212 09010KT P6SM SCT020 PROB30 0118/0122 3SM BR="
_YSSY_TAF = "TAF YSSY 011200Z 0112/0218 18012KT 9999 SCT025 PROB30 0118/0122 4000 SHRA BKN012="
_YCFS_METAR = "METAR YCFS 011300Z AUTO 16008KT 9999 // SCT020 21/// Q1016="
_FNUE_METAR = "METAR FNUE 010100Z AUTO /////KT //// ////// ///// Q////="
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
    matched = [i for i in report.issues if i.code == "PROB_PERIOD_WITHOUT_TEMPO"]
    assert matched
    assert all(i.severity == "info" for i in matched)


def test_c2_y_prefix_au_bom_prob_info() -> None:
    assert resolve_profile_for_station("YSSY") == "au_bom"
    assert resolve_profile_for_station("YCFS") == "au_bom"
    policies = resolve_validation_policies("au_bom", product="TAF")
    assert policies.tac_quality_policy_id == "taf-prob-period-info-quality"
    report = lint_with_profile(_YSSY_TAF, product="TAF", profile="annex3")
    matched = [i for i in report.issues if i.code == "PROB_PERIOD_WITHOUT_TEMPO"]
    assert matched
    assert all(i.severity == "info" for i in matched)


def test_c4_ycfs_dewpoint_nil_info() -> None:
    report = lint(_YCFS_METAR, product="METAR")
    assert any(i.code == "DEWPOINT_NOT_OBSERVABLE" and i.severity == "info" for i in report.issues)
    assert not any(i.code == "MISSING_TEMP_DEWPOINT" for i in report.issues)


def test_c4_fnue_all_solidus_stays_missing() -> None:
    report = lint(_FNUE_METAR, product="METAR")
    assert any(i.code == "MISSING_TEMP_DEWPOINT" and i.severity == "error" for i in report.issues)
    assert not any(i.code == "DEWPOINT_NOT_OBSERVABLE" for i in report.issues)


def test_c6_habana_mov_stnr_info() -> None:
    report = lint(_HABANA, product="SIGMET")
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


def test_c7_international_still_needs_valid() -> None:
    report = lint("SIGMET =", product="SIGMET", profile="annex3")
    assert any(i.code == "MISSING_VALID" for i in report.issues)


def test_c7_international_valid_ok() -> None:
    report = lint(_INTL, product="SIGMET", profile="annex3")
    assert not any(i.code == "MISSING_VALID" for i in report.issues)
