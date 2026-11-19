"""Behavioral locks for October 2026 regional tester feedback.

Each test names a finding from the Jamaica, Guyana, Belize, St Kitts, St Maarten,
and Saint Lucia packs. Failures that are incomplete TAC stay failures.
"""

from __future__ import annotations

from pathlib import Path

from tac2iwxxm.convert import convert

_SPECI_DIRECTION = "SPECI TNCM 061126Z 09008KT 2000E SHRA BKN016 27/24 Q1016 TEMPO SHRA="
_METAR_BOTH = "METAR TNCM 081200Z 14006KT 9999 1200NE FEW020 28/24 Q1013="
_SIGMET_NO_LEAD = (
    "SIGMET 3 VALID 251435/251835 TTPP- "
    "TTZP PIARCO FIR EMBD TS OBS AT 1410Z WI N1800 W05406 - N1800 W05039 - "
    "N1031 W05542 - N1316 W05936 - N1800 W05406 TOP ABV FL380 STNR DECR="
)
_SIGMET_WITH_LEAD = (
    "TTZP SIGMET 3 VALID 251435/251835 TTPP- "
    "TTZP PIARCO FIR EMBD TS OBS AT 1410Z WI N1800 W05406 - N1800 W05039 - "
    "N1031 W05542 - N1316 W05936 - N1800 W05406 TOP ABV FL380 STNR WKN="
)
_SIGMET_TRUNCATED = "SIGMET 1 VALID 261150/261550 TTPP"
_TAF_NO_PERIOD = "TAF SYCJ 291100Z 08010KT 8000 VCSH SHRA FEW018TCU BKN020"
_METAR_TYPO_WIND = "METAR TKPK 232100Z VBR02KT 9999 FEW014CB 29/25 Q1013="
_METAR_BAD_WIND = "METAR MZBZ 240000Z 1100(3)KT 9999 FEW021 29/25 A2984 Q1010 NOSIG="
_METAR_NO_DEWPOINT = "METAR TRPG 081100Z 13013KT 080V150 9999 BKN019 27/ Q1016"
_METAR_NO_VIS = "METAR COR MZBZ 261200Z VRB02KT FEW002 FEW010CB SCT020 25/25 A2990 Q1012 NOSIG="

_KIT = Path(__file__).resolve().parents[3] / ".github" / "workflows" / "tester-regression.yml"
_KIT_PATHS = (
    "packages/tac2iwxxm/tests/test_regional_tester_feedback.py",
    "packages/tac2iwxxm/tests/test_tc_f6_055_lowercase_keyword.py",
    "packages/tac2iwxxm/tests/test_tc_f6_056_regional_packet.py",
    "packages/tac2iwxxm/tests/test_weather_grammar.py",
    "packages/tac2iwxxm/tests/test_caribbean_tester_round2.py",
    "packages/tac-decoding/tests/test_caribbean_present_recent_decode.py",
    "packages/tac-validate/tests/test_caribbean_weather_lint.py",
    "packages/iwxxm-validate/tests/test_tac_paste_not_xml.py",
    "tests/regression/caribbean_tester",
    "packages/tac2iwxxm/tests/test_time_anchor.py",
    "packages/tac2iwxxm/tests/test_taf_variable_wind_knots.py",
    "packages/tac2iwxxm/tests/test_taf_continuation_lines.py",
    "packages/tac2iwxxm/tests/test_taf_probability.py",
    "packages/tac2iwxxm/tests/test_recent_weather.py",
    "packages/tac2iwxxm/tests/test_default_remarks.py",
    "packages/tac2iwxxm/tests/test_mkjp_unobserved_visibility.py",
    "packages/tac2iwxxm/tests/test_heading_paste.py",
    "packages/tac2iwxxm/tests/test_tc_f6_051_taf_time_links.py",
    "packages/tac2iwxxm/tests/test_tc_f6_052_sigmet_body.py",
    "packages/tac2iwxxm/tests/test_tc_f6_053_visibility_10km.py",
    "packages/tac2iwxxm/tests/test_issue_1412_prefer_qnh.py",
    "packages/tac-validate/tests/test_directional_visibility.py",
    "packages/tac-validate/tests/test_tc_f15_006_unobserved_visibility.py",
    "packages/tac-validate/tests/test_tc_f6_050_unknown_cloud_base.py",
    "packages/tac-validate/tests/test_taf_amd_not_sked.py",
    "apps/backend/tests/unit/test_tc_f6_054_heading_convert.py",
    "apps/backend/tests/unit/test_tc_f6_051_output_validation_warning_catalog.py",
    "src/app/components/ConvertResultStatus.test.tsx",
    "src/app/components/FileConverter.test.tsx",
)


def test_directional_visibility_converts_as_metres() -> None:
    result = convert(_SPECI_DIRECTION, product="SPECI")
    assert result.xml is not None
    assert not any(issue.code == "TRANSLATION_FAILED" for issue in result.issues)
    assert '<iwxxm:prevailingVisibility uom="m">2000</iwxxm:prevailingVisibility>' in result.xml
    assert '<iwxxm:minimumVisibility uom="m">2000</iwxxm:minimumVisibility>' in result.xml
    assert '<iwxxm:minimumVisibilityDirection uom="deg">90</iwxxm:minimumVisibilityDirection>' in result.xml


def test_prevailing_metres_stay_when_a_minimum_direction_is_also_present() -> None:
    result = convert(_METAR_BOTH, product="METAR")
    assert result.xml is not None
    assert '<iwxxm:prevailingVisibility uom="m">10000</iwxxm:prevailingVisibility>' in result.xml
    assert "<iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>" in result.xml
    assert '<iwxxm:minimumVisibility uom="m">1200</iwxxm:minimumVisibility>' in result.xml
    assert '<iwxxm:minimumVisibilityDirection uom="deg">45</iwxxm:minimumVisibilityDirection>' in result.xml


def test_sigmet_without_a_leading_region_indicator_keeps_decrease() -> None:
    result = convert(_SIGMET_NO_LEAD, product="SIGMET")
    assert result.xml is not None
    assert not any(issue.code == "TRANSLATION_FAILED" for issue in result.issues)
    assert "PIARCO FIR" in result.xml
    assert 'intensityChange="WEAKEN"' in result.xml
    assert "FL380" in result.xml or "380" in result.xml


def test_sigmet_without_a_named_region_uses_the_watch_office() -> None:
    tac = "SIGMET 2 VALID 101200/101600 YUSO- OBSC TS FCST S OF N54 TOP FL390 STNR WKN="
    result = convert(tac, product="SIGMET")
    assert result.xml is not None
    assert not any(issue.code == "TRANSLATION_FAILED" for issue in result.issues)
    assert "YUSO" in result.xml
    assert 'intensityChange="WEAKEN"' in result.xml


def test_sigmet_with_a_leading_region_indicator_still_names_that_region() -> None:
    result = convert(_SIGMET_WITH_LEAD, product="SIGMET")
    assert result.xml is not None
    assert "PIARCO FIR" in result.xml
    assert 'intensityChange="WEAKEN"' in result.xml


def test_truncated_sigmet_header_still_fails() -> None:
    result = convert(_SIGMET_TRUNCATED, product="SIGMET")
    assert result.xml is None or any(issue.message == "unable to parse SIGMET header" for issue in result.issues)
    assert any(issue.message == "unable to parse SIGMET header" for issue in result.issues)


def test_incomplete_tac_from_the_packet_still_fails_closed() -> None:
    cases = {
        _TAF_NO_PERIOD: ("TAF", "unable to parse TAF header"),
        _METAR_TYPO_WIND: ("METAR", "missing wind group"),
        _METAR_BAD_WIND: ("METAR", "missing wind group"),
        _METAR_NO_DEWPOINT: ("METAR", "missing temperature/dewpoint group"),
        _METAR_NO_VIS: ("METAR", "missing visibility (SM/m/CAVOK) group"),
    }
    for tac, (product, message) in cases.items():
        result = convert(tac, product=product)
        assert any(issue.message == message for issue in result.issues), (product, message, result.issues)


def test_tester_regression_workflow_runs_the_feedback_suite() -> None:
    text = _KIT.read_text(encoding="utf-8")
    missing = [path for path in _KIT_PATHS if path not in text]
    assert missing == []
