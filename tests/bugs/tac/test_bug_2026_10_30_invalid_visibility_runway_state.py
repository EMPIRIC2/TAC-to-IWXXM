"""BUG-2026-10-30 — CIS runway-state Rxx/dddddd must not emit INVALID_VISIBILITY.

Full-world Bar B probe (convert, n=3, on pass): ULOO METARs with ``R19/010060``
emitted INVALID_VISIBILITY because R2 ``\\d{5,}`` matched the six-digit runway
state field after ``/``. Annex-3 visibility remains 4-digit metres / SM / CAVOK;
kilometre forms like ``10KM`` are accepted separately (#1477).

Lint-only surface: mutation modes N/A (no create/update/delete of persisted
state). Matrix covers success (CIS group ignored) × failure (true bad vis) and
validation pass/fail on METAR and SPECI.

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint

# Live ULOO forms (aviationweather history around probe window).
_ULOO_METAR = (
    "METAR ULOO 302000Z 20002MPS 9999 FEW025 BKN042 07/07 Q1021 R19/010060 RMK QFE761"
)
_ULOO_SPECI = (
    "SPECI ULOO 311523Z 35002MPS 9999 FEW015 BKN046 08/07 Q1029 R19/010060 RMK QFE767"
)
# Parallel runway designator + deposit group (same six-digit shape).
_ULOO_METAR_R04L = (
    "METAR ULOO 302000Z 20002MPS 9999 FEW025 BKN042 07/07 Q1021 R04L/010062 RMK QFE761"
)

# True INVALID_VISIBILITY cases (bare 5+ digits / MILES / absurd KM).
# Do not use ``10KM`` here — accepted by #1477.
_BARE_10000 = "METAR KJFK 011200Z 18008KT 10000 SCT050 10/10 A2992="
_FIVE_MILES = "METAR KJFK 011200Z 18008KT 5MILES SCT050 10/10 A2992="
_LONG_KM = "METAR KJFK 011200Z 18008KT 1000KM SCT050 10/10 A2992="
_SPECI_MILES = "SPECI KJFK 011245Z 18008KT 2MILES SCT050 10/10 A2992="

# Same bulletin: valid metres vis + CIS runway-state (must stay clean).
_CIS_WITH_VALID_VIS = (
    "METAR ULOO 302000Z 20002MPS 8000 FEW025 BKN042 07/07 Q1021 R19/010060="
)
# Same bulletin: bad vis token + CIS runway-state (must still flag the bad vis).
_CIS_WITH_BAD_VIS = (
    "METAR ULOO 302000Z 20002MPS 10000 FEW025 BKN042 07/07 Q1021 R19/010060="
)


@pytest.mark.parametrize(
    ("tac", "product"),
    [
        (_ULOO_METAR, "METAR"),
        (_ULOO_SPECI, "SPECI"),
        (_ULOO_METAR_R04L, "METAR"),
        (_CIS_WITH_VALID_VIS, "METAR"),
    ],
    ids=[
        "uloo-metar-runway-state",
        "uloo-speci-runway-state",
        "uloo-metar-r04l-runway-state",
        "cis-with-valid-metres-vis",
    ],
)
def test_cis_runway_state_digits_not_invalid_visibility(tac: str, product: str) -> None:
    """Success / validation pass: CIS Rxx/dddddd is not treated as visibility."""
    report = lint(tac, product=product)
    codes = [i.code for i in report.issues]
    assert "INVALID_VISIBILITY" not in codes
    assert not any(
        i.code == "INVALID_VISIBILITY" and "01006" in (i.message or "")
        for i in report.issues
    )


@pytest.mark.parametrize(
    ("tac", "product", "token"),
    [
        (_BARE_10000, "METAR", "10000"),
        (_FIVE_MILES, "METAR", "5MILES"),
        (_LONG_KM, "METAR", "1000KM"),
        (_SPECI_MILES, "SPECI", "2MILES"),
        (_CIS_WITH_BAD_VIS, "METAR", "10000"),
    ],
    ids=[
        "bare-10000",
        "five-miles",
        "four-digit-km",
        "speci-miles",
        "cis-plus-bare-10000",
    ],
)
def test_malformed_visibility_still_invalid(tac: str, product: str, token: str) -> None:
    """Failure / validation fail: true bad visibility still emits INVALID_VISIBILITY."""
    report = lint(tac, product=product)
    matched = [i for i in report.issues if i.code == "INVALID_VISIBILITY"]
    assert matched
    assert any(token.lower() in (i.message or "").lower() for i in matched)
