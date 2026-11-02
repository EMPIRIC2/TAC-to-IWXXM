"""BUG-2026-10-30 — MISSING_CCCC must not fire on digit ICAO (K10U).

US METAR station designators may include digits (e.g. K10U, K05U, K1F0).
R1 CCCC detection used ``[A-Z]{4}`` only, so convert soft-failed with
``MISSING_CCCC`` even when the station token was present.

Live-map full-world probe 2026-10-30: 8 places, all pass=true.
Ticket: #1476. [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint

# Staging live-map place K10U (Bar B sample).
_K10U = "METAR K10U 302035Z AUTO 23005KT 10SM FEW023 OVC100 12/05 A2989 RMK AO2"
_K05U = "METAR K05U 302055Z AUTO 17012KT 10SM CLR 13/06 A2989 RMK AO2"
_K1F0 = "METAR K1F0 302055Z AUTO 00000KT 10SM SCT017 SCT110 22/18 A3009 RMK AO2"


def _codes(tac: str) -> set[str]:
    return {i.code for i in lint(tac, product="METAR").issues}


def test_bug_2026_10_30_digit_icao_k10u_not_missing_cccc() -> None:
    assert "MISSING_CCCC" not in _codes(_K10U)


def test_bug_2026_10_30_digit_icao_k05u_and_k1f0_not_missing_cccc() -> None:
    assert "MISSING_CCCC" not in _codes(_K05U)
    assert "MISSING_CCCC" not in _codes(_K1F0)


def test_bug_2026_10_30_truly_missing_cccc_still_errors() -> None:
    codes = _codes("METAR 302035Z AUTO 23005KT 10SM FEW023 OVC100 12/05 A2989=")
    assert "MISSING_CCCC" in codes
