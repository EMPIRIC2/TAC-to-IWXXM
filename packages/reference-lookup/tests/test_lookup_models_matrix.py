"""Mandatory evolve-auto test matrix for reference-lookup models and index mutation.

Covers success, failure, validation, and IdentIndex mutation permutations for
ICAO (4-letter) and navaid (3-letter) cases. [Corpus: tests] [Corpus: product §F6]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from reference_lookup import SourceUnavailable, lookup_coordinate, set_coordinate_source
from reference_lookup.csv_index import index_csv
from reference_lookup.lookup import CsvCoordinateSource
from reference_lookup.models import (
    IDENT_COLUMN,
    LATITUDE_COLUMN,
    LONGITUDE_COLUMN,
    REQUIRED_COLUMNS,
    Coordinate,
    CoordinateCsvRow,
    IdentIndex,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
NAVAIDS = (FIXTURES / "navaids.csv").read_text(encoding="utf-8")
AIRPORTS = (FIXTURES / "airports.csv").read_text(encoding="utf-8")


def _source() -> CsvCoordinateSource:
    return CsvCoordinateSource(NAVAIDS, AIRPORTS)


# --- Success paths (S) + read/query happy path ---


@pytest.mark.parametrize(
    ("ident", "lat", "lon"),
    [
        ("SRQ", 27.39780044555664, -82.5542984008789),
        ("srq", 27.39780044555664, -82.5542984008789),
        ("KSRQ", 27.394631, -82.554359),
        ("ksrq", 27.394631, -82.554359),
    ],
)
def test_success_lookup_navaid_and_icao_case_permute(ident: str, lat: float, lon: float) -> None:
    """S / Read+validation pass: fixture resolves navaid and ICAO with case folding."""
    got_lat, got_lon = _source().lookup(ident)
    assert got_lat == pytest.approx(lat)
    assert got_lon == pytest.approx(lon)


def test_success_public_lookup_with_injected_source() -> None:
    """S: package public API returns the same wire tuple shape."""
    set_coordinate_source(_source())
    try:
        point = lookup_coordinate("SRQ")
        assert isinstance(point, tuple)
        assert len(point) == 2
        assert point[0] == pytest.approx(27.39780044555664)
    finally:
        set_coordinate_source(None)


# --- Failure modes (F) + read/query not found ---


@pytest.mark.parametrize(
    "ident",
    [
        "ZZZ",
        "ZZZZ",
        "SR",
        "SRQ-",
        "12",
        "ABCD!",
        "",
        "   ",
    ],
)
def test_failure_missing_or_bad_shape_ident(ident: str) -> None:
    """F / Read fault: missing idents and illegal shapes raise SourceUnavailable."""
    with pytest.raises(SourceUnavailable):
        _source().lookup(ident)


def test_failure_ambiguous_navaid() -> None:
    """F: ambiguous 3-letter navaid is a source error."""
    with pytest.raises(SourceUnavailable):
        _source().lookup("AAL")


# --- Validation success (V+) and failure (V-) ---


def test_validation_success_coordinate_and_csv_row_fields() -> None:
    """V+: Coordinate and CoordinateCsvRow accept valid field values."""
    point = Coordinate(1.5, -2.25)
    assert point.latitude == 1.5
    assert point.longitude == -2.25
    assert point.as_tuple() == (1.5, -2.25)
    row: CoordinateCsvRow = {
        IDENT_COLUMN: "EMP",
        LATITUDE_COLUMN: "1.0",
        LONGITUDE_COLUMN: "2.0",
    }
    assert row[IDENT_COLUMN] == "EMP"
    assert frozenset({IDENT_COLUMN, LATITUDE_COLUMN, LONGITUDE_COLUMN}) == REQUIRED_COLUMNS
    index = index_csv("ident,latitude_deg,longitude_deg\nEMP,1.0,2.0\n")
    assert index.unique_point("EMP") == Coordinate(1.0, 2.0)


@pytest.mark.parametrize(
    "csv_text",
    [
        "name\nonly\n",
        "ident,latitude_deg\nABC,1\n",
        "ident,longitude_deg\nABC,1\n",
        "ident,latitude_deg,longitude_deg\nABC,nope,1\n",
        "ident,latitude_deg,longitude_deg\nABC,1,nope\n",
    ],
)
def test_validation_failure_csv_columns_or_non_numeric(csv_text: str) -> None:
    """V-: missing columns or non-numeric coordinates are rejected."""
    with pytest.raises(SourceUnavailable):
        index_csv(csv_text)


def test_validation_skips_blank_ident_and_empty_coords() -> None:
    """V+: blank ident / empty lat-lon rows are skipped, not accepted as hits."""
    index = index_csv("ident,latitude_deg,longitude_deg\n,1,2\nEMP,,\nOK,3,4\n")
    assert "EMP" not in index
    assert index.unique_point("OK") == Coordinate(3.0, 4.0)
    with pytest.raises(SourceUnavailable):
        CsvCoordinateSource(
            "ident,latitude_deg,longitude_deg\n,1,2\nEMP,,\n",
            "ident,latitude_deg,longitude_deg\n",
        ).lookup("EMP")


# --- Mutation modes (M): IdentIndex create / update / delete-equivalent ---


def test_mutation_create_add_then_unique_success() -> None:
    """Create + validation pass: add one row → unique_point succeeds."""
    index = IdentIndex()
    assert len(index) == 0
    index.add("ABC", Coordinate(10.0, 20.0))
    assert "ABC" in index
    assert len(index) == 1
    assert index.unique_point("ABC") == Coordinate(10.0, 20.0)
    assert index.rows_for("ABC") == [Coordinate(10.0, 20.0)]


def test_mutation_create_add_duplicate_makes_ambiguous_failure() -> None:
    """Create + validation fail outcome: second add → unique_point is None / lookup fails."""
    index = IdentIndex()
    index.add("AAL", Coordinate(1.0, 1.0))
    index.add("AAL", Coordinate(2.0, 2.0))
    assert index.unique_point("AAL") is None
    assert len(index.rows_for("AAL")) == 2
    navaids = "ident,latitude_deg,longitude_deg\nAAL,1,1\nAAL,2,2\n"
    with pytest.raises(SourceUnavailable):
        CsvCoordinateSource(navaids, "ident,latitude_deg,longitude_deg\n").lookup("AAL")


def test_mutation_update_replace_rows_via_new_index() -> None:
    """Update + validation pass: rebuild index with a corrected coordinate."""
    first = index_csv("ident,latitude_deg,longitude_deg\nEMP,1,2\n")
    assert first.unique_point("EMP") == Coordinate(1.0, 2.0)
    updated = index_csv("ident,latitude_deg,longitude_deg\nEMP,9,8\n")
    assert updated.unique_point("EMP") == Coordinate(9.0, 8.0)
    # Injected source mutation: swap fixture → new coordinates
    set_coordinate_source(CsvCoordinateSource("ident,latitude_deg,longitude_deg\nEMP,9,8\n", AIRPORTS))
    try:
        assert lookup_coordinate("EMP") == (9.0, 8.0)
    finally:
        set_coordinate_source(None)


def test_mutation_update_invalid_csv_rejected() -> None:
    """Update + validation fail: bad replacement CSV cannot become a source."""
    with pytest.raises(SourceUnavailable):
        CsvCoordinateSource("ident,latitude_deg,longitude_deg\nEMP,bad,1\n", AIRPORTS)


def test_mutation_delete_clear_injected_source() -> None:
    """Delete + allowed: clearing override restores pytest closed source (unavailable)."""
    set_coordinate_source(_source())
    assert lookup_coordinate("SRQ")[0] == pytest.approx(27.39780044555664)
    set_coordinate_source(None)
    with pytest.raises(SourceUnavailable):
        lookup_coordinate("SRQ")


def test_mutation_delete_rejected_still_closed_under_pytest() -> None:
    """Delete + rejected path: without injection, lookup stays unavailable in unit tests."""
    set_coordinate_source(None)
    with pytest.raises(SourceUnavailable):
        lookup_coordinate("KSRQ")


def test_ident_index_missing_rows_are_empty() -> None:
    """Read fault on model: absent ident yields empty rows and None unique_point."""
    index = IdentIndex()
    assert index.rows_for("ZZZ") == []
    assert index.unique_point("ZZZ") is None
    assert "ZZZ" not in index
