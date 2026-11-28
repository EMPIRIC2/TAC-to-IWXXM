"""#1562: omitted METAR/SPECI fields emit common/nil/missing; lint stays error.

Combinatorial matrix: success omit->nilReason x profiles; present fields must not
gain spurious nilReason; malformed inputs stay TRANSLATION_FAILED; lint MISSING_*
severity stays error. [Corpus: product §F6] [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import re

import pytest
from tac_validate.api import lint_with_profile

from tac2iwxxm import convert

_NIL_MISSING = "http://codes.wmo.int/common/nil/missing"
_HAPPY = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
_PROFILES = ("annex3", "ca_eccc")

# (case_id, product, tac, lint_codes, xml_nil_snippets)
_OMIT_CASES: list[tuple[str, str, str, tuple[str, ...], tuple[str, ...]]] = [
    (
        "metar_missing_visibility",
        "METAR",
        "METAR KJFK 231751Z 18012KT FEW040 15/07 A3005=",
        ("MISSING_VISIBILITY",),
        (f'<iwxxm:visibility xsi:nil="true" nilReason="{_NIL_MISSING}"/>',),
    ),
    (
        "speci_missing_visibility",
        "SPECI",
        "SPECI KJFK 231751Z 18012KT FEW040 15/07 A3005=",
        ("MISSING_VISIBILITY",),
        (f'<iwxxm:visibility xsi:nil="true" nilReason="{_NIL_MISSING}"/>',),
    ),
    (
        "metar_missing_qnh",
        "METAR",
        "METAR KDEN 021100Z AUTO 14002KT 10SM FEW020 06/05 RMK AO2",
        ("MISSING_QNH",),
        (f'<iwxxm:qnh uom="N/A" xsi:nil="true" nilReason="{_NIL_MISSING}"/>',),
    ),
    (
        "metar_missing_wind",
        "METAR",
        "METAR K05U 021155Z AUTO 10SM OVC048 03/02 A3023 RMK AO2",
        ("MISSING_WIND",),
        (f'<iwxxm:surfaceWind xsi:nil="true" nilReason="{_NIL_MISSING}"/>',),
    ),
    (
        "metar_missing_temp_dewpoint",
        "METAR",
        "METAR KDEN 021153Z AUTO 18012KT 10SM FEW040 A3005 RMK AO2",
        ("MISSING_TEMP_DEWPOINT",),
        (
            f'<iwxxm:airTemperature uom="N/A" xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
            f'<iwxxm:dewpointTemperature uom="N/A" xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
        ),
    ),
    (
        "metar_cwdq_missing_vis_and_qnh",
        "METAR",
        "METAR CWDQ 021100Z AUTO 14002KT 06/05 RMK AO1 SLP214 T00630051 50002",
        ("MISSING_VISIBILITY", "MISSING_QNH"),
        (
            f'<iwxxm:visibility xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
            f'<iwxxm:qnh uom="N/A" xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
        ),
    ),
]

_FAIL_CLOSED: list[tuple[str, str, str, str]] = [
    ("typo_wind_vbr", "METAR", "METAR TKPK 232100Z VBR02KT 9999 FEW014CB 29/25 Q1013=", "missing wind group"),
    (
        "partial_temp_tt_slash",
        "METAR",
        "METAR KJFK 231751Z 18012KT 10SM 15/ A3005=",
        "missing temperature/dewpoint group",
    ),
]

_SPURIOUS_NIL_SNIPPETS = (
    f'<iwxxm:visibility xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
    f'<iwxxm:surfaceWind xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
    f'<iwxxm:qnh uom="N/A" xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
    f'<iwxxm:airTemperature uom="N/A" xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
    f'<iwxxm:dewpointTemperature uom="N/A" xsi:nil="true" nilReason="{_NIL_MISSING}"/>',
)


@pytest.mark.parametrize("profile", _PROFILES)
@pytest.mark.parametrize(
    ("case_id", "product", "tac", "lint_codes", "nil_snippets"),
    _OMIT_CASES,
    ids=[row[0] for row in _OMIT_CASES],
)
def test_omitted_field_emits_nilreason_and_lint_stays_error(
    profile: str,
    case_id: str,
    product: str,
    tac: str,
    lint_codes: tuple[str, ...],
    nil_snippets: tuple[str, ...],
) -> None:
    del case_id
    result = convert(tac, product=product, profile=profile, bulletin_date="2026-11-02")
    assert result.ok is True
    assert result.xml is not None
    assert "MeteorologicalAerodromeObservation" in result.xml
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)
    for snippet in nil_snippets:
        assert snippet in result.xml

    icao = re.search(r"\b([A-Z]{4})\b", tac)
    assert icao is not None
    report = lint_with_profile(tac, product=product, profile=profile, icao=icao.group(1))
    for code in lint_codes:
        matched = [i for i in report.issues if i.code == code]
        assert matched, f"expected {code} in {[i.code for i in report.issues]}"
        assert all(i.severity == "error" for i in matched)


@pytest.mark.parametrize("profile", _PROFILES)
def test_present_fields_do_not_get_spurious_nilreason(profile: str) -> None:
    result = convert(_HAPPY, product="METAR", profile=profile, bulletin_date="2026-11-23")
    assert result.ok is True
    assert result.xml is not None
    for snippet in _SPURIOUS_NIL_SNIPPETS:
        assert snippet not in result.xml
    assert re.search(r'<iwxxm:airTemperature uom="Cel">15(?:\.0)?</iwxxm:airTemperature>', result.xml)
    assert re.search(r'<iwxxm:qnh uom="hPa">\d+', result.xml)
    assert "meanWindSpeed" in result.xml
    assert "prevailingVisibility" in result.xml
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)

    report = lint_with_profile(_HAPPY, product="METAR", profile=profile, icao="KJFK")
    assert not any(i.code.startswith("MISSING_") for i in report.issues)


@pytest.mark.parametrize("profile", _PROFILES)
@pytest.mark.parametrize(
    ("case_id", "product", "tac", "message"),
    _FAIL_CLOSED,
    ids=[row[0] for row in _FAIL_CLOSED],
)
def test_malformed_groups_stay_translation_failed(
    profile: str,
    case_id: str,
    product: str,
    tac: str,
    message: str,
) -> None:
    del case_id
    result = convert(tac, product=product, profile=profile)
    assert any(i.code == "TRANSLATION_FAILED" and i.message == message for i in result.issues), result.issues
    assert result.xml is None or "MeteorologicalAerodromeObservation" not in (result.xml or "")


@pytest.mark.parametrize("profile", _PROFILES)
def test_slash_visibility_stays_not_observable_not_missing(profile: str) -> None:
    tac = "METAR KJFK 231751Z AUTO 18012KT //// FEW040 15/07 A3005="
    result = convert(tac, product="METAR", profile=profile, bulletin_date="2026-11-23")
    assert result.ok is True
    assert result.xml is not None
    assert 'nilReason="http://codes.wmo.int/common/nil/notObservable"' in result.xml
    assert f'<iwxxm:visibility xsi:nil="true" nilReason="{_NIL_MISSING}"/>' not in result.xml


def test_happy_path_metar_unchanged() -> None:
    result = convert(_HAPPY, product="METAR", bulletin_date="2026-11-23")
    assert result.ok is True
    assert result.xml is not None
    for snippet in _SPURIOUS_NIL_SNIPPETS:
        assert snippet not in result.xml
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)


def test_cor_update_omit_visibility_emits_nilreason_with_lint_error() -> None:
    """Update-path (COR) create still emits nilReason; lint MISSING_VISIBILITY stays error."""
    tac = "METAR COR MZBZ 261200Z VRB02KT FEW002 FEW010CB SCT020 25/25 A2990 Q1012 NOSIG="
    result = convert(tac, product="METAR", bulletin_date="2026-10-26")
    assert result.ok is True
    assert result.xml is not None
    assert f'<iwxxm:visibility xsi:nil="true" nilReason="{_NIL_MISSING}"/>' in result.xml
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)
    report = lint_with_profile(tac, product="METAR", profile="ICAO_2025", icao="MZBZ")
    matched = [i for i in report.issues if i.code == "MISSING_VISIBILITY"]
    assert matched
    assert all(i.severity == "error" for i in matched)


def test_slash_visibility_only_in_tempo_keeps_not_observable_without_missing() -> None:
    """//// only in TEMPO: first pass marks notObservable; re-bind skips missing flag."""
    from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci

    tac = "METAR KJFK 231751Z AUTO 18012KT FEW040 15/07 A3005 TEMPO ////="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir.get("visibility_not_observable") is True
    assert ir.get("visibility_missing") is not True
