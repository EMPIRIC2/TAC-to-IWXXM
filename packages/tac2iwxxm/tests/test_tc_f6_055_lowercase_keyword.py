"""TC-F6-055: a lowercase METAR or SPECI matches its uppercase twin."""

from __future__ import annotations

from tac2iwxxm.bulletin import split_bulletin
from tac2iwxxm.convert import convert
from tac2iwxxm.slot_builders.metar_speci import fold_observation_case

_LOWER = "metar tncm 081200z 14006kt 9999 few020 28/24 q1013="
_UPPER = _LOWER.upper()
_SIGMET = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 STNR WKN=\n"
)


def test_lowercase_metar_matches_uppercase_twin() -> None:
    lower = convert(_LOWER, product="METAR")
    upper = convert(_UPPER, product="METAR")
    assert lower.xml == upper.xml
    assert lower.xml is not None
    assert 'gml:id="ad.tncm"' in lower.xml
    assert 'reportStatus="NORMAL"' in lower.xml
    assert '<iwxxm:meanWindDirection uom="deg">140</iwxxm:meanWindDirection>' in lower.xml
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">6</iwxxm:meanWindSpeed>' in lower.xml
    assert '<iwxxm:prevailingVisibility uom="m">10000</iwxxm:prevailingVisibility>' in lower.xml
    assert "CloudAmountReportedAtAerodrome/FEW" in lower.xml
    assert '<iwxxm:base uom="[ft_i]">2000</iwxxm:base>' in lower.xml
    assert '<iwxxm:airTemperature uom="Cel">28.0</iwxxm:airTemperature>' in lower.xml
    assert '<iwxxm:dewpointTemperature uom="Cel">24.0</iwxxm:dewpointTemperature>' in lower.xml
    assert '<iwxxm:qnh uom="hPa">1013</iwxxm:qnh>' in lower.xml
    assert not any(issue.code == "TRANSLATION_FAILED" for issue in lower.issues)


def test_lowercase_speci_matches_uppercase_twin() -> None:
    lower_tac = _LOWER.replace("metar", "speci", 1)
    lower = convert(lower_tac, product="SPECI")
    upper = convert(lower_tac.upper(), product="SPECI")
    assert lower.xml == upper.xml
    assert lower.xml is not None
    assert "<iwxxm:SPECI" in lower.xml
    assert not any(issue.code == "TRANSLATION_FAILED" for issue in lower.issues)


def test_lowercase_taf_keeps_header_failure() -> None:
    result = convert("taf tncm 081200z 0812/0912 14006kt 9999 few020", product="TAF")
    assert any(issue.message == "unable to parse TAF header" for issue in result.issues)


def test_lowercase_sigmet_keeps_todays_result() -> None:
    lower = convert(_SIGMET.lower(), product="SIGMET")
    upper = convert(_SIGMET, product="SIGMET")
    assert [(issue.code, issue.message) for issue in lower.issues] == [
        (issue.code, issue.message) for issue in upper.issues
    ]


def test_fold_leaves_a_following_taf_line_unchanged() -> None:
    mixed = "metar tncm 081200z 14006kt 9999 few020 28/24 q1013=\ntaf tncm 081200z 0812/0912 14006kt"
    folded = fold_observation_case(mixed)
    assert folded.startswith("METAR TNCM 081200Z")
    assert "\ntaf tncm 081200z" in folded


def test_bulletin_split_finds_a_lowercase_metar() -> None:
    text = "SAXX31 TNCM 081200\n" + _LOWER
    split = split_bulletin(text, product="METAR")
    assert len(split.reports) == 1
    assert split.reports[0].upper().startswith("METAR TNCM") or _LOWER.upper() in split.reports[0].upper()
