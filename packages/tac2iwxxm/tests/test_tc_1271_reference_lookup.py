"""SRQ resolves from an injected OurAirports fixture. The table remains the fallback."""

from __future__ import annotations

from pathlib import Path

import pytest
from reference_lookup import SourceUnavailable, set_coordinate_source
from reference_lookup.lookup import CsvCoordinateSource
from tac2iwxxm.geometry.reference_point import UnknownVOR, parse_vor_reference_geometry, resolve_vor

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parents[2] / "reference-lookup" / "tests" / "fixtures"
US_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "US_FAA_NWS"
SRQ_TAC = "YUDD SIGMET 6 VALID 101200/101600 YUSO-\nYUDD SHANLON FIR/UIR SEV ICE FCST FROM SRQ MOV NE 30KT NC=\n"
PROFILE = "US_FAA_NWS"
VERSION = "2025-2"


@pytest.fixture
def ourairports_fixture() -> CsvCoordinateSource:
    source = CsvCoordinateSource(
        (FIXTURES / "navaids.csv").read_text(encoding="utf-8"),
        (FIXTURES / "airports.csv").read_text(encoding="utf-8"),
    )
    set_coordinate_source(source)
    yield source
    set_coordinate_source(None)


def test_public_hit_converts_srq(ourairports_fixture: CsvCoordinateSource) -> None:
    del ourairports_fixture
    result = convert(SRQ_TAC, product="SIGMET", profile=PROFILE, iwxxm_version=VERSION)
    assert result.ok, result.issues
    assert result.xml is not None
    assert "27.3978" in result.xml


def test_table_fallback_when_source_errors() -> None:
    set_coordinate_source(None)
    lat, lon = resolve_vor("EED")
    assert 30 < lat < 36
    assert -125 < lon < -110


def test_ambiguous_fixture_falls_back_to_the_table(ourairports_fixture: CsvCoordinateSource) -> None:
    with pytest.raises(SourceUnavailable):
        ourairports_fixture.lookup("AAL")
    lat, lon = resolve_vor("EED")
    assert 30 < lat < 36
    assert -125 < lon < -110


def test_double_miss_is_unknown_vor(ourairports_fixture: CsvCoordinateSource) -> None:
    del ourairports_fixture
    with pytest.raises(UnknownVOR):
        resolve_vor("ZZZ")
    result = convert(
        SRQ_TAC.replace("FROM SRQ", "FROM ZZZ"),
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=VERSION,
    )
    assert result.ok is False
    assert result.issues[0].code == "PARSE_ERROR"


def test_latlon_sigmet_still_converts() -> None:
    tac = (US_FIXTURES / "SIGMET/valid/sigmet_obsc_ts.tac").read_text(encoding="utf-8")
    geom = parse_vor_reference_geometry(tac)
    assert geom is None
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=VERSION)
    assert result.ok, result.issues
    assert result.xml is not None
