"""WMO-No. 782 METAR/SPECI lint quality — success / failure / validation shapes.

Companion to ``tac2iwxxm`` convert+validate pack. Pins handbook-shaped TAC
against the annex3 lint registry.
"""

from __future__ import annotations

import pytest
from tac_validate import lint

WMO782_OK = [
    "METAR KJFK 121251Z 18008KT CAVOK 18/09 Q1013=",
    "METAR EGLL 121250Z 27015KT 9999 -RA SCT020 BKN040 12/10 Q1008=",
    "SPECI LFPG 121305Z 22012KT 2000 BR BKN005 08/07 Q1010=",
]

WMO782_BAD = [
    "METAR 121251Z 18008KT CAVOK 18/09 Q1013=",
    "METAR KJFK 121251Z 18008 CAVOK 18/09 Q1013=",
    "METAR KJFK 121251Z 18008KT 10SM ZZ FEW040 18/09 Q1013=",
]


@pytest.mark.parametrize("tac", WMO782_OK, ids=["cavok", "precip", "speci-br"])
def test_wmo782_lint_success(tac: str) -> None:
    """Success: handbook-shaped METAR/SPECI lint clean under annex3."""
    product = tac.split()[0]
    report = lint(tac, product=product)
    assert report.ok is True, report.issues


@pytest.mark.parametrize("tac", WMO782_BAD, ids=["no-station", "wind-unit", "bad-wx"])
def test_wmo782_lint_failure(tac: str) -> None:
    """Failure: handbook deviations emit lint errors."""
    product = "METAR"
    report = lint(tac, product=product)
    assert report.ok is False
    assert any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize(
    ("tac", "expect_cavok"),
    [
        (WMO782_OK[0], True),
        (WMO782_OK[1], False),
        (WMO782_OK[2], False),
    ],
    ids=["cavok-yes", "cavok-no-ra", "cavok-no-speci"],
)
def test_wmo782_lint_validation_cavok(tac: str, expect_cavok: bool) -> None:
    """Validation: CAVOK presence matches handbook mutual-exclusion shape."""
    parts = tac.replace("=", "").split()
    has_cavok = "CAVOK" in parts
    assert has_cavok is expect_cavok
    if has_cavok:
        assert "RA" not in parts
        assert not any(p.startswith(("FEW", "SCT", "BKN", "OVC")) for p in parts)
    product = parts[0]
    report = lint(tac, product=product)
    assert report.ok is True
