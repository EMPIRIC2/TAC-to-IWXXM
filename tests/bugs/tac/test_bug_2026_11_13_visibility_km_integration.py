"""BUG-2026-11-13 — Accept kilometre visibility tokens like ``10KM`` (#1477).

Probe AYPY ``10KM`` was lint ``INVALID_VISIBILITY`` and convert
``TRANSLATION_FAILED`` / quarantine. Kilometre forms map to metres; bare
``MILES`` and five-digit metre runs stay invalid. Canadian AUTO omitting
visibility (CWDQ) stays ``MISSING_VISIBILITY``.

[Corpus: product §F15] [Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint

from tac2iwxxm import convert

AYPY_10KM = "METAR AYPY 302000Z VRB03KT 10KM SCT050 27/24 Q1012"
CWDQ_AUTO_OMIT_VIS = (
    "METAR CWDQ 021100Z AUTO 14002KT 06/05 RMK AO1 SLP214 T00630051 50002"
)

_TEN_KM = '<iwxxm:prevailingVisibility uom="m">10000</iwxxm:prevailingVisibility>'


@pytest.mark.parametrize(
    "tac",
    [
        AYPY_10KM,
        "METAR KJFK 121251Z 18008KT 10KM FEW250 22/12 A3012=",
        "SPECI AYPY 302045Z VRB03KT 5KM SCT050 27/24 Q1012=",
        "METAR AYPY 302000Z VRB03KT 15KM SCT050 27/24 Q1012=",
    ],
    ids=["aypy_10km", "kjfk_10km", "speci_5km", "aypy_15km"],
)
def test_kilometre_visibility_not_invalid(tac: str) -> None:
    report = lint(tac, product="METAR" if tac.startswith("METAR") else "SPECI")
    codes = [i.code for i in report.issues]
    assert "INVALID_VISIBILITY" not in codes
    assert "MISSING_VISIBILITY" not in codes


@pytest.mark.parametrize(
    ("tac", "product", "expected_m", "expect_above"),
    [
        (AYPY_10KM, "METAR", 10000, True),
        ("METAR KJFK 121251Z 18008KT 5KM FEW250 22/12 A3012=", "METAR", 5000, False),
        ("SPECI AYPY 302045Z VRB03KT 10KM SCT050 27/24 Q1012=", "SPECI", 10000, True),
    ],
    ids=["aypy_10km", "kjfk_5km", "speci_10km"],
)
def test_kilometre_visibility_converts_to_metres(
    tac: str,
    product: str,
    expected_m: int,
    expect_above: bool,
) -> None:
    result = convert(tac, product=product)
    assert result.ok is True
    assert result.xml is not None
    assert (
        f'<iwxxm:prevailingVisibility uom="m">{expected_m}</iwxxm:prevailingVisibility>'
        in result.xml
    )
    if expect_above:
        assert (
            "<iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>"
            in result.xml
        )
    else:
        assert (
            "<iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>"
            not in result.xml
        )
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)


def test_aypy_10km_emits_10000_m() -> None:
    result = convert(AYPY_10KM, product="METAR")
    assert result.ok is True
    assert result.xml is not None
    assert _TEN_KM in result.xml


@pytest.mark.parametrize(
    ("tac", "product", "code"),
    [
        (
            "METAR KJFK 121251Z 18008KT 10MILES FEW250 22/12 A3012=",
            "METAR",
            "INVALID_VISIBILITY",
        ),
        (
            "SPECI KJFK 121251Z 18008KT 2MILES FEW250 22/12 A3012=",
            "SPECI",
            "INVALID_VISIBILITY",
        ),
        (
            "METAR KJFK 121251Z 18008KT 12345 FEW250 22/12 A3012=",
            "METAR",
            "INVALID_VISIBILITY",
        ),
        (
            "METAR KJFK 121251Z 18008KT 10000KM FEW250 22/12 A3012=",
            "METAR",
            "INVALID_VISIBILITY",
        ),
    ],
    ids=["miles_word", "speci_miles", "five_digit", "four_digit_km"],
)
def test_still_invalid_visibility_forms(tac: str, product: str, code: str) -> None:
    report = lint(tac, product=product)
    assert any(i.code == code for i in report.issues)


def test_canadian_auto_omitting_visibility_stays_missing() -> None:
    report = lint(CWDQ_AUTO_OMIT_VIS, product="METAR")
    assert any(i.code == "MISSING_VISIBILITY" for i in report.issues)
    assert "INVALID_VISIBILITY" not in [i.code for i in report.issues]
