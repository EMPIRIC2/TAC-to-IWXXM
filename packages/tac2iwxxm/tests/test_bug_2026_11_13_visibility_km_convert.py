"""Package convert: kilometre visibility ``10KM`` → metres (#1477)."""

from __future__ import annotations

import pytest
from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci
from tac2iwxxm.visibility_measure import prevailing_from_kilometres

from tac2iwxxm import convert

_AYPY = "METAR AYPY 302000Z VRB03KT 10KM SCT050 27/24 Q1012"


@pytest.mark.parametrize(
    ("km", "metres", "above"),
    [
        (5, 5000, False),
        (10, 10000, True),
        (15, 15000, True),
    ],
)
def test_prevailing_from_kilometres(km: int, metres: int, above: bool) -> None:
    assert prevailing_from_kilometres(km) == (metres, above)


@pytest.mark.parametrize(
    ("tac", "product", "metres", "above"),
    [
        (_AYPY, "METAR", 10000, True),
        ("METAR KJFK 121251Z 18008KT 5KM FEW250 22/12 A3012=", "METAR", 5000, False),
        ("SPECI AYPY 302045Z VRB03KT 10KM SCT050 27/24 Q1012=", "SPECI", 10000, True),
    ],
    ids=["aypy_10km", "5km", "speci_10km"],
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
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)


def test_missing_visibility_without_km_still_fails_parse() -> None:
    with pytest.raises(ValueError, match="missing visibility"):
        parse_metar_speci(
            "METAR CWDQ 021100Z AUTO 14002KT 06/05 RMK AO1 SLP214",
            product="METAR",
        )
