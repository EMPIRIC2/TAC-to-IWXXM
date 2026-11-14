"""BUG-2026-10-30 — CIS runway-state Rxx/dddddd must not emit INVALID_VISIBILITY.

Full-world Bar B probe (convert, n=3, on pass): ULOO METARs with ``R19/010060``
emitted INVALID_VISIBILITY because R2 ``\\d{5,}`` matched the six-digit runway
state field after ``/``. Annex-3 visibility remains 4-digit metres / SM / CAVOK;
``NNKM`` stays invalid (separate ticket #1477).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint

# Live ULOO form (aviationweather history around probe window).
_ULOO_METAR = (
    "METAR ULOO 302000Z 20002MPS 9999 FEW025 BKN042 07/07 Q1021 R19/010060 RMK QFE761"
)
_ULOO_SPECI = (
    "SPECI ULOO 311523Z 35002MPS 9999 FEW015 BKN046 08/07 Q1029 R19/010060 RMK QFE767"
)

# True INVALID_VISIBILITY cases (bare 5+ digits / non-Annex-3 units).
_BARE_10000 = "METAR KJFK 011200Z 18008KT 10000 SCT050 10/10 A2992="
_AYPY_KM = "METAR AYPY 302000Z VRB03KT 10KM SCT050 27/24 Q1012="
_FIVE_MILES = "METAR KJFK 011200Z 18008KT 5MILES SCT050 10/10 A2992="


@pytest.mark.parametrize(
    ("tac", "product"),
    [
        (_ULOO_METAR, "METAR"),
        (_ULOO_SPECI, "SPECI"),
    ],
    ids=["uloo-metar-runway-state", "uloo-speci-runway-state"],
)
def test_cis_runway_state_digits_not_invalid_visibility(tac: str, product: str) -> None:
    report = lint(tac, product=product)
    codes = [i.code for i in report.issues]
    assert "INVALID_VISIBILITY" not in codes
    assert not any(
        i.code == "INVALID_VISIBILITY" and "010060" in (i.message or "")
        for i in report.issues
    )


@pytest.mark.parametrize(
    ("tac", "token"),
    [
        (_BARE_10000, "10000"),
        (_AYPY_KM, "10KM"),
        (_FIVE_MILES, "5MILES"),
    ],
    ids=["bare-10000", "nnkm-10km", "five-miles"],
)
def test_malformed_visibility_still_invalid(tac: str, token: str) -> None:
    report = lint(tac, product="METAR")
    matched = [i for i in report.issues if i.code == "INVALID_VISIBILITY"]
    assert matched
    assert any(token.lower() in (i.message or "").lower() for i in matched)
