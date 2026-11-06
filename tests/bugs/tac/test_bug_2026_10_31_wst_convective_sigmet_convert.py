"""BUG-2026-10-31 — US convective WST convert must succeed for live-map residuals.

Stage live-map recheck left 12 quality fails: KKCI ``WSUSx`` / ``MKC[C|W] WST`` /
``CONVECTIVE SIGMET`` bulletins returned HTTP 400 ``All conversions failed``.

Two modes:
1. Ambiguous OurAirports VOR ids missing from the bundled table (e.g. TOU).
2. FROM-chain parser not terminating on ``LINE`` / ``DMSHG`` hazard text.

[Corpus: product §F6] [Corpus: adr/ADR-051] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.geometry.reference_point import (
    UnknownVOR,
    parse_vor_reference_geometry,
    resolve_vor,
)

from tac2iwxxm import convert

# Stage place_key sigmet-104ed07d1525cffe (AREA + ambiguous TOU).
_AREA_TOU = """\
WSUS33 KKCI 301355
MKCW WST 301355

CONVECTIVE SIGMET 22W
VALID UNTIL 1555Z
WA CSTL WTRS
FROM 80SW TOU-50WNW HQM-50WSW HQM-80W HQM-80SW TOU
AREA EMBD TS MOV LTL. TOPS TO FL250.
"""

# Stage place_key sigmet-2b43da18dfa2e932 (DMSHG LINE).
_DMSHG_LINE = """\
WSUS32 KKCI 301755
MKCC WST 301755

CONVECTIVE SIGMET 47C
VALID UNTIL 1955Z
IA NE
FROM 50W OVR-40ESE OVR
DMSHG LINE TS 25 NM WIDE MOV FROM 25020KT. TOPS TO FL310.
"""

# Stage place_key sigmet-641a8b73574563db (LINE TS).
_LINE_TS = """\
WSUS32 KKCI 301755
MKCC WST 301755

CONVECTIVE SIGMET 49C
VALID UNTIL 1955Z
OK KS
FROM 10N OSW-40NNW TUL
LINE TS 20 NM WIDE MOV FROM 17010KT. TOPS TO FL300.
"""

# Stage place_key sigmet-2a0aea5abef84f06 (AREA + MTU).
_AREA_MTU = """\
WSUS33 KKCI 302255
MKCW WST 302255

CONVECTIVE SIGMET 60W
VALID UNTIL 0055Z
UT
FROM MTU-40ENE HVE-10NNW HVE-30W MTU-MTU
AREA EMBD TS MOV FROM 18020KT. TOPS TO FL280.
"""

# Remaining Stage place_keys (full remaining-failures set coverage).
_REMAINING: list[tuple[str, str]] = [
    ("sigmet-104ed07d1525cffe", _AREA_TOU),
    ("sigmet-2a0aea5abef84f06", _AREA_MTU),
    ("sigmet-2b43da18dfa2e932", _DMSHG_LINE),
    (
        "sigmet-34369d7484afb837",
        """\
WSUS33 KKCI 310055
MKCW WST 310055

CONVECTIVE SIGMET 2W
VALID UNTIL 0255Z
CO NM AZ UT
FROM 20SSE MTU-20ENE RSK-50SSW RSK-30N HVE-20SSE MTU
AREA TS MOV FROM 22020KT. TOPS TO FL350.
""",
    ),
    (
        "sigmet-34cea91726ea5ff3",
        """\
WSUS32 KKCI 310055
MKCC WST 310055

CONVECTIVE SIGMET 3C
VALID UNTIL 0255Z
MN IA NE SD
FROM 50SSE ABR-50N FSD-40WNW FOD-70S FSD-50SE PIR-50SSE ABR
AREA TS MOV FROM 21020KT. TOPS TO FL380.
""",
    ),
    (
        "sigmet-40e51d5d33325d73",
        """\
WSUS32 KKCI 310155
MKCC WST 310155

CONVECTIVE SIGMET 7C
VALID UNTIL 0355Z
MN IA NE SD
FROM 40SSE ABR-70WNW RWF-10WNW FOD-30NNE ONL-70ESE PIR-40SSE ABR
AREA TS MOV FROM 21020KT. TOPS TO FL380.
""",
    ),
    (
        "sigmet-5dca377101a6e27b",
        """\
WSUS33 KKCI 302355
MKCW WST 302355

CONVECTIVE SIGMET 62W
VALID UNTIL 0155Z
CO NM AZ UT
FROM 20N MTU-50SSW ABQ-20NW SJN-20ESE HVE-20N MTU
AREA TS MOV FROM 22020KT. TOPS TO FL350.
""",
    ),
    ("sigmet-641a8b73574563db", _LINE_TS),
    (
        "sigmet-b026696c049e76fb",
        """\
WSUS32 KKCI 302055
MKCC WST 302055

CONVECTIVE SIGMET 57C
VALID UNTIL 2255Z
MO IA
FROM 70SE OVR-20NNW IRK
LINE TS 20 NM WIDE MOV FROM 25020KT. TOPS TO FL300.
""",
    ),
    (
        "sigmet-b71b7f21c19b142f",
        """\
WSUS32 KKCI 302355
MKCC WST 302355

CONVECTIVE SIGMET 67C
VALID UNTIL 0155Z
TX AND LA TX CSTL WTRS
FROM 20SSE IAH-80SE LCH-110WSW LEV-80ESE CRP-20SSE IAH
AREA TS MOV FROM 21015KT. TOPS TO FL420.
""",
    ),
    (
        "sigmet-bc309c92d488bfae",
        """\
WSUS33 KKCI 301555
MKCW WST 301555

CONVECTIVE SIGMET 30W
VALID UNTIL 1755Z
AZ
FROM 40S TUS-50SSW SSO
LINE EMBD TS 25 NM WIDE MOV FROM 23020KT. TOPS TO FL290.
""",
    ),
    (
        "sigmet-c34e8c1e3fe30870",
        """\
WSUS33 KKCI 310155
MKCW WST 310155

CONVECTIVE SIGMET 8W
VALID UNTIL 0355Z
CO NM UT
FROM 20SSE MTU-20ENE RSK-30WSW RSK-50SW MTU-20SSE MTU
AREA EMBD TS MOV FROM 22020KT. TOPS TO FL360.
""",
    ),
]


def test_bug_2026_10_31_resolve_vor_tou_from_fallback_table() -> None:
    lat, lon = resolve_vor("TOU")
    assert 48.0 < lat < 48.5
    assert -125.0 < lon < -124.0


def test_bug_2026_10_31_from_chain_stops_before_dmshg_line() -> None:
    geom = parse_vor_reference_geometry(
        "FROM 50W OVR-40ESE OVR DMSHG LINE TS 25 NM WIDE MOV FROM 25020KT"
    )
    assert geom is not None
    assert geom["kind"] in {"polygon", "point"}
    refs = geom.get("reference_points") or []
    assert len(refs) == 2
    assert refs[0]["vor"] == "OVR"
    assert refs[1]["vor"] == "OVR"


def test_bug_2026_10_31_area_tou_convective_converts() -> None:
    result = convert(_AREA_TOU, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]
    assert result.xml is not None
    assert "gml:posList" in result.xml or "gml:pos>" in result.xml


def test_bug_2026_10_31_dmshg_line_convective_converts() -> None:
    result = convert(_DMSHG_LINE, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]


def test_bug_2026_10_31_line_ts_tul_converts() -> None:
    result = convert(_LINE_TS, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]


@pytest.mark.parametrize(
    ("place_key", "tac"), _REMAINING, ids=[p for p, _ in _REMAINING]
)
def test_bug_2026_10_31_remaining_stage_wst_converts(place_key: str, tac: str) -> None:
    result = convert(tac, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, (place_key, [(i.code, i.message) for i in (result.issues or [])])


def test_bug_2026_10_31_truly_unknown_vor_still_fails_closed() -> None:
    try:
        resolve_vor("ZZZ")
        raise AssertionError("expected UnknownVOR")
    except UnknownVOR:
        pass
    result = convert(
        _AREA_TOU.replace("TOU", "ZZZ"),
        product="SIGMET",
        iwxxm_version="2025-2",
    )
    assert result.ok is False
    assert result.issues
    assert result.issues[0].code == "PARSE_ERROR"
    assert "ZZZ" in result.issues[0].message
