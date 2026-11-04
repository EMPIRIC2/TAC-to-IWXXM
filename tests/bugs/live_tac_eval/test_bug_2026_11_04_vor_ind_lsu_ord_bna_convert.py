"""Live Stage WST convert hard-fails for IND / LSU / ORD / BNA (#1552).

[Corpus: product §F6] [Corpus: tests]

IND and ORD are chart ids absent from OurAirports navaids (Brickyard VHP /
Chicago O'Hare VOR/DME). LSU is the Fighting Tiger chart id (OA lists BTR).
BNA is multi-country ambiguous in OurAirports. Without US seeds in the
bundled table, convert returns PARSE_ERROR and IWXXM validate is
blocked_by_convert.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tac2iwxxm.geometry.reference_point import UnknownVOR, resolve_vor

from tac2iwxxm import convert

# Staging live-map residual (#1552 sample) — unknown VOR IND.
_IND_CONVECTIVE = """\
WSUS32 KKCI 040755
MKCC WST 040755
CONVECTIVE SIGMET 21C
VALID UNTIL 0955Z
TN KY IN AL IL
FROM 40NNE IND-40WNW LOZ-60W GQO-30SSE DYR-60WNW PXV-40NNE IND
AREA EMBD TS MOV FROM 23030KT. TOPS TO FL370.
"""

_LSU_CONVECTIVE = """\
WSUS32 KKCI 040555
MKCC WST 040555
CONVECTIVE SIGMET 15C
VALID UNTIL 0755Z
TN AL MS LA
FROM 30NE MEM-40NNW MSL-20SE IGB-10E LSU-40SE LCH-30NE MEM
AREA EMBD TS MOV FROM 24040KT. TOPS TO FL450.
"""

_ORD_CONVECTIVE = """\
WSUS32 KKCI 031655
MKCC WST 031655
CONVECTIVE SIGMET 77C
VALID UNTIL 1855Z
WI IL LM
FROM 30ESE GRB-10N ORD-60ESE DBQ-40WSW GRB-30ESE GRB
AREA TS MOV FROM 21045KT. TOPS TO FL330.
"""

_BNA_CONVECTIVE = """\
WSUS32 KKCI 040855
MKCC WST 040855
CONVECTIVE SIGMET 25C
VALID UNTIL 1055Z
TN AL MS
FROM 40SSW BNA-30SW VUZ-20ENE MCB-30WNW MCB-30ESE SQS-40SSW BNA
AREA EMBD TS MOV FROM 26025KT. TOPS TO FL450.
"""

_HAND_CONVECTIVE: dict[str, str] = {
    "IND": _IND_CONVECTIVE,
    "LSU": _LSU_CONVECTIVE,
    "ORD": _ORD_CONVECTIVE,
    "BNA": _BNA_CONVECTIVE,
}

_LIVE_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "wst_vor_live_2026_11_04.json"
)

# Decimal bounds around published US navaid coordinates.
_EXPECTED_US = {
    "IND": (39.7, 39.9, -86.5, -86.2),  # Brickyard VHP under IND chart id
    "LSU": (30.4, 30.6, -91.4, -91.2),  # Fighting Tiger (OA BTR)
    "ORD": (41.9, 42.1, -88.0, -87.8),  # Chicago O'Hare VOR/DME
    "BNA": (36.0, 36.3, -86.8, -86.5),  # Nashville US VORTAC
}


def _load_live_cases() -> list[dict[str, Any]]:
    payload = json.loads(_LIVE_FIXTURE.read_text(encoding="utf-8"))
    cases = payload["cases"]
    assert isinstance(cases, list)
    return cases


_LIVE_CASES = _load_live_cases()
_LIVE_IDS = [f"{c['vor_id']}-{c['place_key']}" for c in _LIVE_CASES]


@pytest.mark.parametrize("vor_id", sorted(_EXPECTED_US))
def test_bug_2026_11_04_resolve_wst_vor_from_fallback_table(vor_id: str) -> None:
    lat_lo, lat_hi, lon_lo, lon_hi = _EXPECTED_US[vor_id]
    lat, lon = resolve_vor(vor_id)
    assert lat_lo < lat < lat_hi, vor_id
    assert lon_lo < lon < lon_hi, vor_id


@pytest.mark.parametrize("vor_id", sorted(_HAND_CONVECTIVE))
def test_bug_2026_11_04_hand_convective_sigmet_converts(vor_id: str) -> None:
    result = convert(
        _HAND_CONVECTIVE[vor_id],
        product="SIGMET",
        iwxxm_version="2025-2",
    )
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]
    assert result.xml is not None


def test_bug_2026_11_04_ind_sample_converts() -> None:
    result = convert(_IND_CONVECTIVE, product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, [(i.code, i.message) for i in (result.issues or [])]
    assert result.xml is not None
    assert "gml:posList" in result.xml or "gml:pos>" in result.xml


@pytest.mark.parametrize("case", _LIVE_CASES, ids=_LIVE_IDS)
def test_bug_2026_11_04_live_wst_vor_fixture_converts(case: dict[str, Any]) -> None:
    result = convert(case["tac"], product="SIGMET", iwxxm_version="2025-2")
    assert result.ok, (
        case["vor_id"],
        case["place_key"],
        [(i.code, i.message) for i in (result.issues or [])],
    )
    assert result.xml


def test_bug_2026_11_04_live_fixture_covers_expected_vors() -> None:
    vor_ids = {case["vor_id"] for case in _LIVE_CASES}
    assert vor_ids == set(_EXPECTED_US)
    assert len(_LIVE_CASES) == 16


def test_bug_2026_11_04_truly_unknown_vor_still_fails_closed() -> None:
    with pytest.raises(UnknownVOR):
        resolve_vor("ZZZ")
    result = convert(
        _IND_CONVECTIVE.replace(" IND-", " ZZZ-").replace(" IND\n", " ZZZ\n"),
        product="SIGMET",
        iwxxm_version="2025-2",
    )
    assert result.ok is False
    assert result.issues
    assert result.issues[0].code == "PARSE_ERROR"
    assert "ZZZ" in result.issues[0].message
