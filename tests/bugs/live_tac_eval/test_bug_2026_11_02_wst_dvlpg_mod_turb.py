"""Live residual convert/lint: WST DVLPG FROM-ring + SIGMET MOD TURB.

Convert soft-tolerates NWS ``DVLPG AREA TS`` after isolating the FROM ring;
prefer lint accepts the canonical developing-area form (#1554). SIGMET
``MOD TURB`` stays fail-closed on convert and lint membership error.

[Corpus: product §F6] [Corpus: product §F15] [Corpus: product §F23] [Corpus: tests]
"""

from __future__ import annotations

import re

import pytest
from tac2iwxxm.geometry.reference_point import _SEGMENT, parse_vor_reference_geometry
from tac_validate import lint

from tac2iwxxm import convert

# Live WST residuals (session live-tac-eval-vor-residual-2026-11-02).
_DVLPG_LIVE: tuple[tuple[str, str], ...] = (
    (
        "sigmet-055d7ff848506dae",
        """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 30C
VALID UNTIL 2055Z
TX OK
FROM 10E MMB-50WSW END-20N CDS-30ESE AMA-10E MMB
DVLPG AREA TS MOV FROM 22025KT. TOPS TO FL340.
""",
    ),
    (
        "sigmet-62bc3b350e0fe313",
        """\
WSUS32 KKCI 021755
MKCC WST 021755
CONVECTIVE SIGMET 24C
VALID UNTIL 1955Z
OK KS
FROM 30W OSW-40NNW ADM-50N SPS-30NNE END-30W OSW
DVLPG AREA TS MOV FROM 22050KT. TOPS TO FL320.
""",
    ),
    (
        "sigmet-83fc4f347eccb160",
        """\
WSUS32 KKCI 022055
MKCC WST 022055
CONVECTIVE SIGMET 41C
VALID UNTIL 2255Z
KS
FROM 60ENE HLC-40NNW SLN-50WNW ICT-50E GCK-60ENE HLC
DVLPG AREA TS MOV FROM 22050KT. TOPS TO FL380.
""",
    ),
    (
        "sigmet-9779da4a4c5a9ff8",
        """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 29C
VALID UNTIL 2055Z
IA NE SD
FROM 60ESE ABR-70S FSD-10NNW OBH-50E PIR-60ESE ABR
DVLPG AREA TS MOV FROM 22050KT. TOPS TO FL320.
""",
    ),
    (
        "sigmet-cc2bb31aa90dee62",
        """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 28C
VALID UNTIL 2055Z
OK KS
FROM 40WSW BUM-30N ADM-50SW OKC-30SSE ICT-40WSW BUM
DVLPG AREA TS MOV FROM 22050KT. TOPS TO FL390.
""",
    ),
)

_AREA_TS_OK = """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 30C
VALID UNTIL 2055Z
TX OK
FROM 10E MMB-50WSW END-20N CDS-30ESE AMA-10E MMB
AREA TS MOV FROM 22025KT. TOPS TO FL340.
"""

_DMSHG_LINE_OK = """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 30C
VALID UNTIL 2055Z
TX OK
FROM 10E MMB-50WSW END-20N CDS-30ESE AMA-10E MMB
DMSHG LINE TS MOV FROM 22025KT. TOPS TO FL340.
"""

_FQBE_MOD_TURB = """\
WSMZ31 FQMA 021100
FQBE SIGMET A02 VALID 021126/021526  FQMA-
FQBE BEIRA FIR MOD TURB FCST WI S2619 E03142 - S2355 E03142 - S2443
E03407 - S2654 E03434 - S2619 E03142 TOP FL400=
"""

_FQBE_SEV_TURB = """\
WSMZ31 FQMA 021100
FQBE SIGMET A02 VALID 021126/021526  FQMA-
FQBE BEIRA FIR SEV TURB FCST WI S2619 E03142 - S2355 E03142 - S2443
E03407 - S2654 E03434 - S2619 E03142 TOP FL400=
"""

_FQBE_AIRMET_MOD_TURB = """\
WSMZ31 FQMA 021100
FQBE AIRMET A02 VALID 021126/021526  FQMA-
FQBE BEIRA FIR MOD TURB FCST WI S2619 E03142 - S2355 E03142 - S2443
E03407 - S2654 E03434 - S2619 E03142 TOP FL400=
"""

_UNKNOWN_VOR_FAIL = """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 1C
VALID UNTIL 2055Z
TX
FROM 10N ZZZ-10S ZZZ
AREA TS MOV FROM 22010KT. TOPS TO FL300.
"""


@pytest.mark.parametrize(
    ("place_key", "tac"), _DVLPG_LIVE, ids=[p for p, _ in _DVLPG_LIVE]
)
def test_dvlpg_live_wst_convert_ok_with_geometry(place_key: str, tac: str) -> None:
    """Success: live DVLPG AREA after FROM ring converts with geometry."""
    result = convert(tac, product="SIGMET", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok, (place_key, result.issues)
    assert result.xml is not None
    assert "posList" in result.xml or "pos " in result.xml
    assert "AreaTS" in result.xml or "areaOf" in result.xml or "Airspace" in result.xml


@pytest.mark.parametrize(
    ("place_key", "tac"), _DVLPG_LIVE, ids=[p for p, _ in _DVLPG_LIVE]
)
def test_dvlpg_live_wst_lint_accepts_canonical_area(place_key: str, tac: str) -> None:
    """Success/lint: canonical DVLPG AREA after FROM ring is not a false error."""
    report = lint(tac, product="SIGMET")
    matched = [i for i in report.issues if i.code == "DVLPG_AREA_QUALIFIER"]
    assert not matched, (
        place_key,
        [(i.code, i.severity, i.message) for i in report.issues],
    )


def test_area_ts_and_dmshg_line_still_convert_ok() -> None:
    """Success: existing AREA / DMSHG LINE stops are unchanged."""
    for tac in (_AREA_TS_OK, _DMSHG_LINE_OK):
        result = convert(
            tac, product="SIGMET", profile="iwxxm_us", iwxxm_version="2025-2"
        )
        assert result.ok, result.issues
        assert result.xml is not None
        assert "posList" in result.xml or "pos " in result.xml


def test_area_ts_without_dvlpg_has_no_dvlpg_lint() -> None:
    """Success/lint: plain AREA TS does not emit DVLPG_AREA_QUALIFIER."""
    report = lint(_AREA_TS_OK, product="SIGMET")
    assert not any(i.code == "DVLPG_AREA_QUALIFIER" for i in report.issues)


def test_glued_vor_segment_shape_still_rejected_by_segment_regex() -> None:
    """Failure: glued ``'10E MMB DVLPG'`` is not a valid VOR offset segment."""
    assert _SEGMENT.match("10E MMB DVLPG") is None
    # Without a FROM-chain stop token, a trailing garbage token stays fail-closed.
    with pytest.raises(ValueError, match=r"unable to parse VOR reference segment"):
        parse_vor_reference_geometry("FROM 10E MMB-20N CDS GARBAGE")


def test_from_chain_stops_before_dvlpg() -> None:
    """Success: FROM-chain lookahead treats DVLPG like DMSHG / AREA."""
    geom = parse_vor_reference_geometry("FROM 10E MMB-20N CDS-10E MMB DVLPG AREA TS")
    assert geom is not None
    assert geom.get("kind") == "polygon"
    assert len(geom.get("reference_points") or []) >= 3


def test_unknown_vor_still_fail_closed() -> None:
    """Failure: unknown VOR remains convert hard-fail."""
    result = convert(
        _UNKNOWN_VOR_FAIL,
        product="SIGMET",
        profile="iwxxm_us",
        iwxxm_version="2025-2",
    )
    assert result.ok is False
    assert any(i.code == "PARSE_ERROR" and "ZZZ" in i.message for i in result.issues)


def test_mod_turb_sigmet_convert_fail_closed_with_clear_message() -> None:
    """Failure: FQBE MOD TURB stays convert fail-closed with clearer copy."""
    result = convert(
        _FQBE_MOD_TURB,
        product="SIGMET",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok is False
    assert any(i.code == "PARSE_ERROR" for i in result.issues)
    messages = " ".join(i.message for i in result.issues).lower()
    assert "missing phenomenon" in messages
    assert "mod turb" in messages or "moderate turbulence" in messages
    assert "sev" in messages or "airmet" in messages
    assert not re.search(r"\b(?:ADR-|EV-|Corpus:)\b", messages, flags=re.I)


def test_mod_turb_sigmet_lint_unknown_membership_error() -> None:
    """Failure/lint: MOD TURB on SIGMET stays UNKNOWN_WMO_MEMBERSHIP error."""
    report = lint(_FQBE_MOD_TURB, product="SIGMET")
    membership = [i for i in report.issues if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert membership
    assert all(i.severity == "error" for i in membership)
    assert any("MOD TURB" in i.message for i in membership)


def test_sev_turb_sigmet_convert_ok() -> None:
    """Success: same TAC with SEV TURB converts."""
    result = convert(
        _FQBE_SEV_TURB,
        product="SIGMET",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok, result.issues
    assert result.xml is not None


def test_sev_turb_sigmet_lint_no_mod_turb_membership() -> None:
    """Success/lint: SEV TURB does not emit membership on the phenomenon."""
    report = lint(_FQBE_SEV_TURB, product="SIGMET")
    membership = [i for i in report.issues if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert not any(
        "SEV TURB" in i.message or "SEV_TURB" in i.message for i in membership
    )
    assert not any("MOD TURB" in i.message for i in membership)


def test_airmet_mod_turb_convert_ok() -> None:
    """Success: same hazard as AIRMET converts."""
    result = convert(
        _FQBE_AIRMET_MOD_TURB,
        product="AIRMET",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok, result.issues
    assert result.xml is not None
