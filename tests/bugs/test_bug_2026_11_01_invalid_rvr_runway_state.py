"""C5 — CIS runway-state Rxx/dddddd must not emit INVALID_RVR (sibling of #1479).

[Corpus: product §F15] [Corpus: tests §TC-EV-RPR-005]
"""

from __future__ import annotations

from tac_validate import lint

_ULOO_SPECI = "SPECI ULOO 311523Z 35002MPS 9999 FEW015 BKN046 08/07 Q1029 R19/010060 RMK OBST OBSC QFE767"
_ULOO_METAR = (
    "METAR ULOO 011330Z 04002MPS 9999 OVC036 08/05 Q1031 R19/010062 RMK QFE769"
)
_BAD_RVR = "METAR KJFK 011200Z 18008KT 1/2SM R04/P2000N VV005 10/10 A2992="


def test_uloo_runway_state_not_invalid_rvr_speci() -> None:
    report = lint(_ULOO_SPECI, product="SPECI")
    codes = [i.code for i in report.issues]
    assert "INVALID_RVR" not in codes


def test_uloo_runway_state_not_invalid_rvr_metar() -> None:
    report = lint(_ULOO_METAR, product="METAR")
    codes = [i.code for i in report.issues]
    assert "INVALID_RVR" not in codes


def test_true_icao_rvr_malform_still_invalid() -> None:
    # R04/P2000N is valid; use a clearly bad RVR token.
    report = lint(
        "METAR KJFK 011200Z 18008KT 1/2SM R04/ABC VV005 10/10 A2992=",
        product="METAR",
    )
    assert any(i.code == "INVALID_RVR" for i in report.issues)
