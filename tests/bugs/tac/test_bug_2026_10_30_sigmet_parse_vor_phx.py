"""BUG-2026-10-30 — US convective SIGMET FROM-chain must resolve PHX VOR.

Live-map AZ convective SIGMETs name Phoenix as ``PHX``. OurAirports catalogs
that navaid as ``PXR``, and the checked-in fallback table lacked ``PHX``, so
convert failed closed with ``unknown VOR reference 'PHX'`` / HTTP 400
“All conversions failed”.

[Corpus: product §F6] [Corpus: adr/ADR-051] [Corpus: tests]
"""

from __future__ import annotations

from tac2iwxxm.geometry.reference_point import UnknownVOR, resolve_vor

from tac2iwxxm import convert

# Staging live-map place sigmet-0236c4a340b58cc9 (2026-10-30).
_PHX_CONVECTIVE = """\
WSUS33 KKCI 301055
MKCW WST 301055

CONVECTIVE SIGMET 11W
VALID UNTIL 1255Z
AZ
FROM 20ENE INW-40W SSO-30WNW TUS-20WSW PHX-30NNW DRK-20ENE INW
AREA TS MOV FROM 19020KT. TOPS TO FL420.
"""

# Peer miss seen with empty_bulletin sibling residual (AMA chart id).
_AMA_CONVECTIVE = """\
WSUS32 KKCI 301255
MKCC WST 301255

CONVECTIVE SIGMET 42C
VALID UNTIL 1455Z
TX NM AZ
FROM 30E FTI-20WSW AMA-70WSW INK-50S SSO-50S SJN-30E FTI
AREA TS MOV FROM 21020KT. TOPS ABV FL450.
"""


def test_bug_2026_10_30_resolve_vor_phx_from_fallback_table() -> None:
    lat, lon = resolve_vor("PHX")
    assert 33.0 < lat < 34.0
    assert -112.5 < lon < -111.0


def test_bug_2026_10_30_phx_convective_sigmet_converts() -> None:
    result = convert(_PHX_CONVECTIVE, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]
    assert result.xml is not None
    assert "gml:posList" in result.xml or "gml:pos>" in result.xml


def test_bug_2026_10_30_ama_vor_resolves_and_chain_converts() -> None:
    lat, lon = resolve_vor("AMA")
    assert 34.5 < lat < 36.0
    assert -103.0 < lon < -100.5
    result = convert(_AMA_CONVECTIVE, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]


def test_bug_2026_10_30_truly_unknown_vor_still_fails_closed() -> None:
    try:
        resolve_vor("ZZZ")
        raise AssertionError("expected UnknownVOR")
    except UnknownVOR:
        pass
    result = convert(
        _PHX_CONVECTIVE.replace("PHX", "ZZZ"),
        product="SIGMET",
        iwxxm_version="2025-2",
    )
    assert result.ok is False
    assert result.issues
    assert result.issues[0].code == "PARSE_ERROR"
    assert "ZZZ" in result.issues[0].message
