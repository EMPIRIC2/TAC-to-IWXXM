"""Package convert: kilometre visibility ``10KM`` → metres (#1477).

Covers success paths, ABOVE boundary, digit bounds, case folding, and convert
failures for forms that lint rejects.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci
from tac2iwxxm.visibility_measure import prevailing_from_kilometres

from tac2iwxxm import convert

_AYPY = "METAR AYPY 302000Z VRB03KT 10KM SCT050 27/24 Q1012"


@pytest.mark.parametrize(
    ("km", "metres", "above"),
    [
        (1, 1000, False),
        (5, 5000, False),
        (9, 9000, False),
        (10, 10000, True),
        (15, 15000, True),
        (999, 999000, True),
    ],
    ids=["1", "5", "9_below", "10_above", "15", "999"],
)
def test_prevailing_from_kilometres(km: int, metres: int, above: bool) -> None:
    assert prevailing_from_kilometres(km) == (metres, above)


@pytest.mark.parametrize(
    ("tac", "product", "metres", "above"),
    [
        (_AYPY, "METAR", 10000, True),
        ("METAR KJFK 121251Z 18008KT 5KM FEW250 22/12 A3012=", "METAR", 5000, False),
        ("METAR KJFK 121251Z 18008KT 9KM FEW250 22/12 A3012=", "METAR", 9000, False),
        ("METAR KJFK 121251Z 18008KT 10km FEW250 22/12 A3012=", "METAR", 10000, True),
        ("SPECI AYPY 302045Z VRB03KT 10KM SCT050 27/24 Q1012=", "SPECI", 10000, True),
        ("METAR KJFK 121251Z 18008KT 1KM FEW250 22/12 A3012=", "METAR", 1000, False),
        ("METAR KJFK 121251Z 18008KT 999KM FEW250 22/12 A3012=", "METAR", 999000, True),
    ],
    ids=["aypy_10km", "5km", "9km", "lowercase", "speci_10km", "1km", "999km"],
)
def test_parse_and_convert_kilometre_visibility(
    tac: str,
    product: str,
    metres: int,
    above: bool,
) -> None:
    ir = parse_metar_speci(tac, product=product)
    assert ir["visibility_m"] == metres
    assert ir["visibility_above"] is above
    assert ir.get("visibility_km") == metres // 1000

    result = convert(tac, product=product)
    assert result.ok is True
    assert result.xml is not None
    assert f'<iwxxm:prevailingVisibility uom="m">{metres}</iwxxm:prevailingVisibility>' in result.xml
    if above:
        assert "<iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>" in result.xml
    else:
        assert "<iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>" not in result.xml
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)


def test_missing_visibility_without_km_emits_missing_flag() -> None:
    """Clean omission (#1562): no vis group → visibility_missing, not raise."""
    ir = parse_metar_speci(
        "METAR CWDQ 021100Z AUTO 14002KT 06/05 RMK AO1 SLP214",
        product="METAR",
    )
    assert ir.get("visibility_missing") is True


@pytest.mark.parametrize(
    "tac",
    [
        "METAR KJFK 121251Z 18008KT 10MILES FEW250 22/12 A3012=",
        "METAR KJFK 121251Z 18008KT 12345 FEW250 22/12 A3012=",
        "METAR KJFK 121251Z 18008KT 10000KM FEW250 22/12 A3012=",
        "METAR KJFK 121251Z 18008KT 1000KM FEW250 22/12 A3012=",
    ],
    ids=["miles", "five_digit", "long_km", "4digit_km"],
)
def test_convert_rejects_invalid_visibility_tokens(tac: str) -> None:
    result = convert(tac, product="METAR")
    codes = {i.code for i in result.issues}
    assert "TRANSLATION_FAILED" in codes
    assert result.xml is not None
    assert "translation.failed" in result.xml
    assert "prevailingVisibility" not in result.xml
