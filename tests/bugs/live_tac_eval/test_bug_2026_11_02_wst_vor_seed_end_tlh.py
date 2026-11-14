"""BUG-2026-11-02 — WST convective FROM-chains must resolve END/TLH/ALS peers.

Live-map US convective SIGMETs name VORs that OurAirports marks ambiguous
(multi-country) or omits (TLH chart id). The checked-in fallback table lacked
those US points, so convert failed closed with ``unknown VOR reference 'END'``.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tac2iwxxm.geometry.reference_point import UnknownVOR, resolve_vor

from tac2iwxxm import convert

# Staging live-map residual (2026-11-02 detail eval) — unknown VOR END.
_END_CONVECTIVE = """\
WSUS32 KKCI 021055
MKCC WST 021055
CONVECTIVE SIGMET 8C
VALID UNTIL 1255Z
TX OK KS
FROM 20WNW ICT-40W END-20SW MMB-60ESE GCK-20WNW ICT
AREA TS MOV FROM 25035KT. TOPS TO FL400.
"""

# Eastern WST peer — TLH chart id (Seminole / Tallahassee area).
_TLH_CONVECTIVE = """\
WSUS31 KKCI 020055
MKCE WST 020055
CONVECTIVE SIGMET 1E
VALID UNTIL 0255Z
FL AND CSTL WTRS
FROM 40SE TLH-30ENE CTY-90W PIE-40SE TLH
AREA TS MOV FROM 22025KT. TOPS TO FL400.
"""

_ALS_CONVECTIVE = """\
WSUS32 KKCI 022155
MKCC WST 022155
CONVECTIVE SIGMET 45C
VALID UNTIL 2355Z
TX OK KS NE CO NM
FROM 60E MCK-40E GCK-30NNW TCC-50NNE ALS-20WSW MCK-60E MCK
AREA EMBD TS MOV LTL. TOPS TO FL350.
"""

_ORL_CONVECTIVE = """\
WSUS31 KKCI 022055
MKCE WST 022055
CONVECTIVE SIGMET 51E
VALID UNTIL 2255Z
FL AND CSTL WTRS
FROM 20NNE ORL-130ENE TRV-50ESE PBI-110WSW RSW-20NNE ORL
AREA EMBD TS MOV FROM 15015KT. TOPS ABV FL450.
"""

_FAR_CONVECTIVE = """\
WSUS32 KKCI 022255
MKCC WST 022255
CONVECTIVE SIGMET 48C
VALID UNTIL 0055Z
MN IA NE SD
FROM 40SE FAR-40WSW BRD-40WNW FOD-70W PWE-50SSW OBH-40SE FAR
AREA TS MOV FROM 22025KT. TOPS TO FL380.
"""

_GRB_CONVECTIVE = """\
WSUS32 KKCI 022255
MKCC WST 022255
CONVECTIVE SIGMET 51C
VALID UNTIL 0055Z
WI IL MN IA
FROM 30E EAU-40WSW GRB-30SSW DBQ-30SE MCW-30E EAU
DMSHG AREA TS MOV FROM 22050KT. TOPS TO FL250.
"""

_BRD_CONVECTIVE = """\
WSUS32 KKCI 022155
MKCC WST 022155
CONVECTIVE SIGMET 46C
VALID UNTIL 2355Z
MN IA NE SD ND
FROM 50W BRD-60ESE FSD-60SSE OBH-60SSW OBH-30S FAR-50W BRD
AREA TS MOV FROM 22050KT. TOPS TO FL390.
"""

_HAND_CONVECTIVE: dict[str, str] = {
    "END": _END_CONVECTIVE,
    "TLH": _TLH_CONVECTIVE,
    "ALS": _ALS_CONVECTIVE,
    "ORL": _ORL_CONVECTIVE,
    "FAR": _FAR_CONVECTIVE,
    "GRB": _GRB_CONVECTIVE,
    "BRD": _BRD_CONVECTIVE,
}

_LIVE_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "wst_vor_live_2026_11_02.json"
)

_EXPECTED_US = {
    "END": (36.2, 36.5, -98.0, -97.8), # Vance VORTAC
    "ALS": (37.2, 37.5, -106.0, -105.7), # Alamosa
    "ORL": (28.4, 28.7, -81.5, -81.2), # Orlando
    "FAR": (46.6, 46.9, -97.0, -96.7), # Fargo
    "GRB": (44.4, 44.7, -88.4, -88.0), # Green Bay
    "BRD": (46.2, 46.5, -94.2, -93.9), # Brainerd
    "TLH": (30.4, 30.7, -84.5, -84.2), # Seminole SZW under TLH key
}


def _load_live_cases() -> list[dict[str, Any]]:
    payload = json.loads(_LIVE_FIXTURE.read_text(encoding="utf-8"))
    cases = payload["cases"]
    assert isinstance(cases, list)
    return cases


_LIVE_CASES = _load_live_cases()
_LIVE_IDS = [f"{c['vor_id']}-{c['place_key']}" for c in _LIVE_CASES]


@pytest.mark.parametrize("vor_id", sorted(_EXPECTED_US))
def test_bug_2026_11_02_resolve_wst_vor_from_fallback_table(vor_id: str) -> None:
    lat_lo, lat_hi, lon_lo, lon_hi = _EXPECTED_US[vor_id]
    lat, lon = resolve_vor(vor_id)
    assert lat_lo < lat < lat_hi, vor_id
    assert lon_lo < lon < lon_hi, vor_id


@pytest.mark.parametrize("vor_id", sorted(_HAND_CONVECTIVE))
def test_bug_2026_11_02_hand_convective_sigmet_converts(vor_id: str) -> None:
    result = convert(
        _HAND_CONVECTIVE[vor_id],
        product="SIGMET",
        iwxxm_version="2025-2",
    )
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]
    assert result.xml is not None


def test_bug_2026_11_02_end_convective_sigmet_converts() -> None:
    result = convert(_END_CONVECTIVE, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]
    assert result.xml is not None
    assert "gml:posList" in result.xml or "gml:pos>" in result.xml


def test_bug_2026_11_02_tlh_convective_sigmet_converts() -> None:
    result = convert(_TLH_CONVECTIVE, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]


@pytest.mark.parametrize("case", _LIVE_CASES, ids=_LIVE_IDS)
def test_bug_2026_11_02_live_wst_vor_fixture_converts(case: dict[str, Any]) -> None:
    result = convert(case["tac"], product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, (
        case["vor_id"],
        case["place_key"],
        [(i.code, i.message) for i in (result.issues or [])],
    )


def test_bug_2026_11_02_live_fixture_covers_expected_vors() -> None:
    vor_ids = {case["vor_id"] for case in _LIVE_CASES}
    assert vor_ids == set(_EXPECTED_US)
    assert len(_LIVE_CASES) == 22


def test_bug_2026_11_02_truly_unknown_vor_still_fails_closed() -> None:
    with pytest.raises(UnknownVOR):
        resolve_vor("ZZZ")
    result = convert(
        _END_CONVECTIVE.replace(" END-", " ZZZ-"),
        product="SIGMET",
        iwxxm_version="2025-2",
    )
    assert result.ok is False
    assert result.issues
    assert result.issues[0].code == "PARSE_ERROR"
    assert "ZZZ" in result.issues[0].message
