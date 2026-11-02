"""Wind-shear runway designators must not fire INVALID_RVR.

Live 30d METAR SKBO: ``… Q1029 WS R14R NOSIG`` — ``R14R`` is the runway after
``WS`` (wind shear), not an RVR group. True RVR always has ``/`` after the
runway designator (``R14R/P2000N``). Product-rule-fix: do not select bare
``R##[LCR]?`` tokens as RVR candidates (not a severity soften).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint
from tac_validate.api import lint_with_profile

# Live-map METAR (staging 2026-11-02); no secrets.
_SKBO_WS = "METAR SKBO 021500Z 06006KT 360V110 9999 BKN040 17/11 Q1029 WS R14R NOSIG"
_TRUE_RVR = "METAR KJFK 011200Z 18008KT 1/2SM R04L/P2000N VV005 10/10 A2992="
_BAD_RVR = "METAR KJFK 011200Z 18008KT 1/2SM R04/ABC VV005 10/10 A2992="


def test_skbo_ws_runway_not_invalid_rvr_prefer() -> None:
    report = lint_with_profile(_SKBO_WS, product="METAR", profile="annex3", icao="SKBO")
    assert "INVALID_RVR" not in {i.code for i in report.issues}


def test_skbo_ws_runway_not_invalid_rvr_bare_lint() -> None:
    report = lint(_SKBO_WS, product="METAR")
    assert "INVALID_RVR" not in {i.code for i in report.issues}


def test_true_rvr_with_slash_still_ok() -> None:
    report = lint(_TRUE_RVR, product="METAR")
    assert "INVALID_RVR" not in {i.code for i in report.issues}
    assert any(i.code == "RVR_PRESENT" for i in report.issues)


def test_malformed_rvr_with_slash_still_invalid() -> None:
    report = lint(_BAD_RVR, product="METAR")
    assert any(i.code == "INVALID_RVR" for i in report.issues)
