"""#1562 — omitted METAR/SPECI fields emit common/nil/missing; lint stays error.

[Corpus: product §F6] [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import re

import pytest
from tac_validate.api import lint_with_profile

from tac2iwxxm import convert

_NIL_MISSING = "http://codes.wmo.int/common/nil/missing"
_HAPPY = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="

# (case_id, product, tac, lint_codes, xml_nil_snippets)
_CASES: list[tuple[str, str, str, tuple[str, ...], tuple[str, ...]]] = [
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


@pytest.mark.parametrize(
    ("case_id", "product", "tac", "lint_codes", "nil_snippets"),
    _CASES,
    ids=[row[0] for row in _CASES],
)
def test_omitted_field_emits_nilreason_and_lint_stays_error(
    case_id: str,
    product: str,
    tac: str,
    lint_codes: tuple[str, ...],
    nil_snippets: tuple[str, ...],
) -> None:
    del case_id
    result = convert(tac, product=product, bulletin_date="2026-11-02")
    assert result.ok is True
    assert result.xml is not None
    assert "MeteorologicalAerodromeObservation" in result.xml
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)
    for snippet in nil_snippets:
        assert snippet in result.xml

    icao = re.search(r"\b([A-Z]{4})\b", tac)
    assert icao is not None
    report = lint_with_profile(tac, product=product, profile="annex3", icao=icao.group(1))
    for code in lint_codes:
        matched = [i for i in report.issues if i.code == code]
        assert matched, f"expected {code} in {[i.code for i in report.issues]}"
        assert all(i.severity == "error" for i in matched)


def test_happy_path_metar_unchanged() -> None:
    result = convert(_HAPPY, product="METAR", bulletin_date="2026-11-23")
    assert result.ok is True
    assert result.xml is not None
    assert f'<iwxxm:visibility xsi:nil="true" nilReason="{_NIL_MISSING}"/>' not in result.xml
    assert f'<iwxxm:surfaceWind xsi:nil="true" nilReason="{_NIL_MISSING}"/>' not in result.xml
    assert f'<iwxxm:qnh uom="N/A" xsi:nil="true" nilReason="{_NIL_MISSING}"/>' not in result.xml
    assert re.search(r'<iwxxm:airTemperature uom="Cel">15(?:\.0)?</iwxxm:airTemperature>', result.xml)
    assert re.search(r'<iwxxm:qnh uom="hPa">\d+', result.xml)
    assert "meanWindSpeed" in result.xml
    assert "prevailingVisibility" in result.xml
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)
