"""BUG-2026-11-02 — WST convective FROM-chains must resolve END/TLH/ALS peers.

Live-map US convective SIGMETs name VORs that OurAirports marks ambiguous
(multi-country) or omits (TLH chart id). The checked-in fallback table lacked
those US points, so convert failed closed with ``unknown VOR reference 'END'``.

[Corpus: product §F6] [Corpus: adr/ADR-051] [Corpus: tests]
"""

from __future__ import annotations

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

_EXPECTED_US = {
    "END": (36.2, 36.5, -98.0, -97.8),  # Vance VORTAC
    "ALS": (37.2, 37.5, -106.0, -105.7),  # Alamosa
    "ORL": (28.4, 28.7, -81.5, -81.2),  # Orlando
    "FAR": (46.6, 46.9, -97.0, -96.7),  # Fargo
    "GRB": (44.4, 44.7, -88.4, -88.0),  # Green Bay
    "BRD": (46.2, 46.5, -94.2, -93.9),  # Brainerd
    "TLH": (30.4, 30.7, -84.5, -84.2),  # Seminole SZW under TLH key
}


@pytest.mark.parametrize("vor_id", sorted(_EXPECTED_US))
def test_bug_2026_11_02_resolve_wst_vor_from_fallback_table(vor_id: str) -> None:
    lat_lo, lat_hi, lon_lo, lon_hi = _EXPECTED_US[vor_id]
    lat, lon = resolve_vor(vor_id)
    assert lat_lo < lat < lat_hi, vor_id
    assert lon_lo < lon < lon_hi, vor_id


def test_bug_2026_11_02_end_convective_sigmet_converts() -> None:
    result = convert(_END_CONVECTIVE, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]
    assert result.xml is not None
    assert "gml:posList" in result.xml or "gml:pos>" in result.xml


def test_bug_2026_11_02_tlh_convective_sigmet_converts() -> None:
    result = convert(_TLH_CONVECTIVE, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]


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
