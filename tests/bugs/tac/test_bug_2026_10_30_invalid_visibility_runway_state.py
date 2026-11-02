"""BUG-2026-10-30 — CIS runway-state Rxx/dddddd must not emit INVALID_VISIBILITY.

Full-world Bar B probe (convert, n=3, on pass): ULOO METARs with ``R19/010060``
emitted INVALID_VISIBILITY because R2 ``\\d{5,}`` matched the six-digit runway
state field after ``/``. Annex-3 visibility remains 4-digit metres / SM / CAVOK;
``NNKM`` stays invalid (separate ticket).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint

# Live ULOO form (aviationweather history around probe window).
ULOO_RUNWAY_STATE = (
    "METAR ULOO 302000Z 20002MPS 9999 FEW025 BKN042 07/07 Q1021 R19/010060 RMK QFE761"
)

# Papua New Guinea non-Annex-3 kilometre form — still INVALID_VISIBILITY by design.
AYPY_KM = "METAR AYPY 302000Z VRB03KT 10KM SCT050 27/24 Q1012"


def test_cis_runway_state_digits_not_invalid_visibility() -> None:
    report = lint(ULOO_RUNWAY_STATE, product="METAR")
    codes = [i.code for i in report.issues]
    assert "INVALID_VISIBILITY" not in codes
    assert not any(
        i.code == "INVALID_VISIBILITY" and "010060" in (i.message or "")
        for i in report.issues
    )


def test_nnkm_still_invalid_visibility() -> None:
    report = lint(AYPY_KM, product="METAR")
    assert any(i.code == "INVALID_VISIBILITY" for i in report.issues)
