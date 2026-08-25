"""TC-EV080 — US_FAA_NWS SIGMET VOR reference geometry (EV-080 / #919 M9).

[Corpus: product §F36] [Corpus: tests §TC-EV080] [Corpus: domain-profiles §US_FAA_NWS]
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from metar_shared.xml_canonical import canonicalize_xml

from tac2iwxxm import convert
from tac2iwxxm.geometry.reference_point import (
    ReferencePointGeometryParser,
    UnknownVOR,
    offset_nm,
    parse_vor_reference_geometry,
    resolve_vor,
)
from tac2iwxxm.products.sigmet_airmet import parse_sigmet

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "US_FAA_NWS"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "US_FAA_NWS"

VOR_VALID_CASES = ("sigmet_vor_chain", "sigmet_vor_single")


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing US_FAA_NWS manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def us_manifest() -> dict:
    return _load_manifest()


def test_tc_ev080_001_offset_nm_cardinals() -> None:
    """Spherical offset moves north and east as expected."""
    lat, lon = 32.0, -114.0
    north = offset_nm(lat, lon, 60, "N")
    east = offset_nm(lat, lon, 60, "E")
    assert north[0] > lat
    assert abs(north[1] - lon) < 0.01
    assert east[1] > lon
    assert abs(east[0] - lat) < 0.5


def test_tc_ev080_002_vor_chain_parse_vertices() -> None:
    """VOR FROM chain yields closed polygon with ≥3 vertices."""
    tac = (FIXTURES / "SIGMET/valid/sigmet_vor_chain.tac").read_text(encoding="utf-8")
    ir = parse_sigmet(tac)
    geom = ir["geometry"]
    assert geom["kind"] == "polygon"
    verts = geom["pos_list"].split()
    assert len(verts) >= 8  # 4 points × lat/lon
    assert len(geom.get("reference_points", [])) == 3


def test_tc_ev080_003_unknown_vor_raises() -> None:
    """Unknown VOR id fails closed."""
    tac = (FIXTURES / "SIGMET/invalid/sigmet_vor_unknown.tac").read_text(encoding="utf-8")
    with pytest.raises(UnknownVOR):
        parse_sigmet(tac)


@pytest.mark.parametrize("case_id", VOR_VALID_CASES)
def test_tc_ev080_004_manifest_and_convert(case_id: str, us_manifest: dict) -> None:
    """Manifest rows convert to profile goldens with polygon/point geometry."""
    case = next(c for c in us_manifest["cases"] if c["id"] == case_id)
    assert case["rule_id"] == "US.SIGMET.GEOM.VOR"
    tac_path = FIXTURES / case["tac"]
    golden_path = FIXTURES / case["golden"]
    tac = tac_path.read_text(encoding="utf-8")
    expected = golden_path.read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok, result.issues
    assert result.xml is not None
    assert canonicalize_xml(result.xml) == canonicalize_xml(expected)
    assert "gml:posList" in result.xml or "gml:pos>" in result.xml


def test_tc_ev080_005_resolve_fixture_vors() -> None:
    """Bundled table resolves EV-080 fixture VOR ids."""
    for vor_id in ("EED", "BZA", "TRM"):
        lat, lon = resolve_vor(vor_id)
        assert -125 < lon < -110
        assert 30 < lat < 36


def test_tc_ev080_006_offset_bad_cardinal() -> None:
    """Unsupported cardinal raises ValueError."""
    with pytest.raises(ValueError, match="unsupported cardinal"):
        offset_nm(32.0, -114.0, 10, "INVALID")


def test_tc_ev080_007_parse_no_from_chain() -> None:
    """Body without FROM chain returns None."""
    assert parse_vor_reference_geometry("SEV ICE FCST FL180/FL240 MOV NE 30KT NC") is None


def test_tc_ev080_008_parse_empty_from_chain() -> None:
    """FROM with only dashes (no segments) returns None."""
    assert parse_vor_reference_geometry("SEV ICE FROM --- NC") is None


def test_tc_ev080_009_parse_bad_segment() -> None:
    """Malformed segment raises ValueError."""
    table = {"EED": {"lat": 34.0, "lon": -114.0}}
    parser = ReferencePointGeometryParser(table)
    with pytest.raises(ValueError, match="unable to parse VOR reference segment"):
        parser.parse_from_body("FROM BADSEG MOV NE 30KT")


def test_tc_ev080_010_polygon_already_closed() -> None:
    """Closed polygon skips duplicate closing vertex when first equals last."""
    table = {"AAA": {"lat": 10.0, "lon": -100.0}}
    parser = ReferencePointGeometryParser(table)
    with patch(
        "tac2iwxxm.geometry.reference_point.offset_nm",
        side_effect=[(1.0, -1.0), (2.0, -2.0), (1.0, -1.0)],
    ):
        result = parser.parse_from_body("FROM 10N AAA-20NE AAA-30E AAA MOV NE 30KT")
    assert result is not None
    assert result["kind"] == "polygon"
    assert len(result["pos_list"].split()) == 6
