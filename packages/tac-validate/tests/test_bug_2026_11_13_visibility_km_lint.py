"""Package lint: kilometre visibility ``10KM`` success and failure matrix (#1477).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint
from tac_validate.detectors import run_r2_visibility_detectors

_OK = [
    ("METAR AYPY 302000Z VRB03KT 10KM SCT050 27/24 Q1012", "METAR", "10km"),
    ("SPECI AYPY 302045Z VRB03KT 5KM SCT050 27/24 Q1012=", "SPECI", "5km_speci"),
    ("METAR KJFK 121251Z 18008KT 15KM FEW250 22/12 A3012=", "METAR", "15km"),
    ("METAR KJFK 121251Z 18008KT 1KM FEW250 22/12 A3012=", "METAR", "1km"),
    ("METAR KJFK 121251Z 18008KT 9KM FEW250 22/12 A3012=", "METAR", "9km_below_above"),
    ("METAR KJFK 121251Z 18008KT 999KM FEW250 22/12 A3012=", "METAR", "999km_digit_cap"),
    ("METAR KJFK 121251Z 18008KT 10km FEW250 22/12 A3012=", "METAR", "lowercase_km"),
    ("METAR KJFK 121251Z 18008KT 10Km FEW250 22/12 A3012=", "METAR", "mixed_case_km"),
]
_BAD = [
    ("METAR KJFK 121251Z 18008KT 10MILES FEW250 22/12 A3012=", "METAR", "miles"),
    ("SPECI KJFK 121251Z 18008KT 2MILES FEW250 22/12 A3012=", "SPECI", "speci_miles"),
    ("METAR KJFK 121251Z 18008KT 12345 FEW250 22/12 A3012=", "METAR", "five_digit"),
    ("METAR KJFK 121251Z 18008KT 10000KM FEW250 22/12 A3012=", "METAR", "long_km"),
    ("METAR KJFK 121251Z 18008KT 1000KM FEW250 22/12 A3012=", "METAR", "4digit_km_edge"),
]


@pytest.mark.parametrize(
    ("tac", "product"),
    [(t, p) for t, p, _ in _OK],
    ids=[i for _, _, i in _OK],
)
def test_r2_accepts_kilometre_visibility(tac: str, product: str) -> None:
    codes = {i.code for i in lint(tac, product=product).issues}
    assert "INVALID_VISIBILITY" not in codes
    assert "MISSING_VISIBILITY" not in codes
    det = {i.code for i in run_r2_visibility_detectors(tac, product)}
    assert "INVALID_VISIBILITY" not in det
    assert "MISSING_VISIBILITY" not in det


@pytest.mark.parametrize(
    ("tac", "product"),
    [(t, p) for t, p, _ in _BAD],
    ids=[i for _, _, i in _BAD],
)
def test_r2_rejects_invalid_visibility_forms(tac: str, product: str) -> None:
    issues = lint(tac, product=product).issues
    assert any(i.code == "INVALID_VISIBILITY" for i in issues)
    det = run_r2_visibility_detectors(tac, product)
    assert any(i.code == "INVALID_VISIBILITY" for i in det)


def test_cwdq_auto_omitted_visibility_still_missing() -> None:
    tac = "METAR CWDQ 021100Z AUTO 14002KT 06/05 RMK AO1 SLP214 T00630051 50002"
    codes = {i.code for i in lint(tac, product="METAR").issues}
    assert "MISSING_VISIBILITY" in codes
    assert "INVALID_VISIBILITY" not in codes


def test_invalid_visibility_registry_message_mentions_km() -> None:
    from tac_validate.issue_registry import issue_from

    msg = issue_from("INVALID_VISIBILITY", product="METAR").message or ""
    assert "KM" in msg or "kilometre" in msg.lower()
