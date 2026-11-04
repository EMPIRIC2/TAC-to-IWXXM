"""Live Stage WST convert hard-fails for ELD / ARG VOR refs (#1536).

[Corpus: product §F6] [Corpus: tests]

ELD (El Dorado) and ARG (Walnut Ridge) are multi-country ambiguous in
OurAirports, so ``lookup_coordinate`` raises ``SourceUnavailable`` and the
bundled table must seed the US VORTAC coordinates. Without them, convert
returns ``PARSE_ERROR`` and IWXXM validate is skipped.
"""

from __future__ import annotations

from tac2iwxxm import convert
from tac2iwxxm.geometry.reference_point import resolve_vor

# Staging live-map 30d dump (EV-decode-residuals-2026-11-03) — no secrets.
_LIVE_ELD = """\
WSUS32 KKCI 031155
MKCC WST 031155
CONVECTIVE SIGMET 47C
VALID UNTIL 1355Z
LA AR TX
FROM 20WNW ELD-50NNW PSX-30WSW SAT-60NW GGG-20WNW ELD
AREA TS MOV FROM 28025KT. TOPS ABV FL450.
"""

_LIVE_ARG = """\
WSUS32 KKCI 031455
MKCC WST 031455
CONVECTIVE SIGMET 63C
VALID UNTIL 1655Z
LA MO AR TX OK
FROM 30NE RZC-20N ARG-50S EIC-50W PSX-60S SAT-30NE RZC
AREA TS MOV FROM 23040KT. TOPS ABV FL450.
"""

_LIVE_ELD_AND_ARG = """\
WSUS32 KKCI 031055
MKCC WST 031055
CONVECTIVE SIGMET 44C
VALID UNTIL 1255Z
MO AR TX OK KS
FROM 40WSW COU-60NW ARG-30W ELD-50WNW GGG-30NE OSW-40WSW COU
AREA TS MOV FROM 25030KT. TOPS TO FL430.
"""


def test_resolve_vor_eld_arg_us_vortac() -> None:
    eld_lat, eld_lon = resolve_vor("ELD")
    arg_lat, arg_lon = resolve_vor("ARG")
    assert 33.0 < eld_lat < 34.0
    assert -93.0 < eld_lon < -92.0
    assert 36.0 < arg_lat < 37.0
    assert -91.5 < arg_lon < -90.5


def test_live_eld_convective_sigmet_converts() -> None:
    result = convert(_LIVE_ELD, product="SIGMET", profile="annex3")
    assert result.ok, result.issues
    assert result.xml


def test_live_arg_convective_sigmet_converts() -> None:
    result = convert(_LIVE_ARG, product="SIGMET", profile="annex3")
    assert result.ok, result.issues
    assert result.xml


def test_live_eld_and_arg_chain_converts() -> None:
    result = convert(_LIVE_ELD_AND_ARG, product="SIGMET", profile="annex3")
    assert result.ok, result.issues
    assert result.xml


def test_unknown_vor_still_parse_error() -> None:
    tac = """\
MKCC CONVECTIVE SIGMET 1C VALID UNTIL 1755Z
TX
FROM 10N ZZZ-10S ZZZ
AREA TS MOV FROM 21010KT. TOPS TO FL300.
"""
    result = convert(tac, product="SIGMET", profile="annex3")
    assert result.ok is False
    assert any(
        issue.code == "PARSE_ERROR" and "ZZZ" in issue.message for issue in result.issues
    )
