"""BUG-2026-10-30 — MISSING_VA_VOLCANO must not fire on VA NAME PSN without MT.

MHTG live VA SIGMETs use ``VA FUEGO PSN …`` / ``VA SANTA MARIA PSN …`` without
the Annex-3 ``MT`` keyword. Lint required ``MT…PSN`` only, so convert soft-failed
with ``MISSING_VA_VOLCANO`` on otherwise valid identity.

Live-map full-world probe 2026-10-30: 8 places, all pass=true.
Ticket: #1478. [Corpus: product §F23] [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint

# Staging live-map samples (Bar B).
_VA_FUEGO = """WVHO31 MHTG 301320
MHTG SIGMET 3 VALID 301320/301920 MHTG-
MHCC CENTRAL AMERICAN FIR VA FUEGO PSN N1428 W09052
VA CLD OBS AT 1230Z SFC/FL160 N1430 W09108 - N1428 W09053
- N1426 W09053 - N1426 W09108 - N1430 W09108 MOV W 15KT
FCST 1830Z VA CLD SFC/FL160 N1428 W09053- N1427 W09052
 - N1421 W09113 - N1427 W09116 -N1428 W09053=
"""

_VA_SANTA_MARIA = """WVHO31 MHTG 301130
MHTG SIGMET A2 VALID 301130/301730 MHTG-
MHCC CENTRAL AMERICAN FIR VA SANTA MARIA PSN N1445 W09133
VA CLD OBS AT 1100Z SFC/FL140 N1446 W09132 - N1445 W09132
- N1444 W09135 - N1445 W09136 - N1446 W09132 MOV SW 10KT
FCST 1700Z VA CLD SFC/FL140 N1446 W09132
- N1444 W09132 - N1443 W09138 - N1446 W09138 - N1446 W09132=
"""

_VA_CLD_ONLY = """EGGX SIGMET 4 VALID 251600/252000 EGRR-
EGGX SHANWICK OCEANIC FIR VA CLD OBS AT 1600Z WI N6000 W01150 - N5900 W01300 - N6000 W01600 - N6000 W01150 SFC/FL550 NC=
"""


def _codes(tac: str) -> set[str]:
    return {i.code for i in lint(tac, product="SIGMET").issues}


def test_bug_2026_10_30_va_fuego_psn_not_missing_volcano() -> None:
    codes = _codes(_VA_FUEGO)
    assert "MISSING_VA_VOLCANO" not in codes
    assert "VA_VOLCANO_IDENTITY" in codes


def test_bug_2026_10_30_va_santa_maria_psn_not_missing_volcano() -> None:
    codes = _codes(_VA_SANTA_MARIA)
    assert "MISSING_VA_VOLCANO" not in codes
    assert "VA_VOLCANO_IDENTITY" in codes


def test_bug_2026_10_30_va_cld_only_still_missing_volcano() -> None:
    assert "MISSING_VA_VOLCANO" in _codes(_VA_CLD_ONLY)


def test_bug_2026_10_30_va_mt_psn_still_identity_info() -> None:
    """Classic Annex-3 ``VA MT … PSN`` form remains accepted (success of MT path)."""
    tac = (
        "EGGX SIGMET 4 VALID 251600/252000 EGRR-\n"
        "EGGX SHANWICK OCEANIC FIR VA MT ETNA PSN N3744 E01500 "
        "VA CLD OBS AT 1600Z WI N6000 W01150 - N5900 W01300 - N6000 W01600 "
        "- N6000 W01150 SFC/FL550 NC="
    )
    codes = _codes(tac)
    assert "MISSING_VA_VOLCANO" not in codes
    assert "VA_VOLCANO_IDENTITY" in codes
