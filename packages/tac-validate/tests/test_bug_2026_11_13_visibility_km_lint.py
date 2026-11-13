"""Package lint: kilometre visibility ``10KM`` is valid (#1477)."""

from __future__ import annotations

import pytest
from tac_validate import lint
from tac_validate.detectors import run_r2_visibility_detectors

_OK = [
    ("METAR AYPY 302000Z VRB03KT 10KM SCT050 27/24 Q1012", "METAR"),
    ("SPECI AYPY 302045Z VRB03KT 5KM SCT050 27/24 Q1012=", "SPECI"),
    ("METAR KJFK 121251Z 18008KT 15KM FEW250 22/12 A3012=", "METAR"),
]
_BAD = [
    ("METAR KJFK 121251Z 18008KT 10MILES FEW250 22/12 A3012=", "METAR"),
    ("METAR KJFK 121251Z 18008KT 12345 FEW250 22/12 A3012=", "METAR"),
    ("METAR KJFK 121251Z 18008KT 10000KM FEW250 22/12 A3012=", "METAR"),
]


@pytest.mark.parametrize(("tac", "product"), _OK, ids=["10km", "5km_speci", "15km"])
def test_r2_accepts_kilometre_visibility(tac: str, product: str) -> None:
    codes = {i.code for i in lint(tac, product=product).issues}
    assert "INVALID_VISIBILITY" not in codes
    assert "MISSING_VISIBILITY" not in codes
    det = {i.code for i in run_r2_visibility_detectors(tac, product)}
    assert "INVALID_VISIBILITY" not in det
    assert "MISSING_VISIBILITY" not in det


@pytest.mark.parametrize(("tac", "product"), _BAD, ids=["miles", "five_digit", "long_km"])
def test_r2_still_rejects_non_km_invalid_forms(tac: str, product: str) -> None:
    assert any(i.code == "INVALID_VISIBILITY" for i in lint(tac, product=product).issues)


def test_cwdq_auto_omitted_visibility_still_missing() -> None:
    tac = "METAR CWDQ 021100Z AUTO 14002KT 06/05 RMK AO1 SLP214 T00630051 50002"
    codes = {i.code for i in lint(tac, product="METAR").issues}
    assert "MISSING_VISIBILITY" in codes
