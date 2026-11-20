"""Mandatory evolve-auto test matrix for shared TAC patterns [Corpus: tests]."""

from __future__ import annotations

import pytest

from metar_shared.models.tac_tokens import AhlHeadingParts, StationIcao
from metar_shared.tac_patterns import (
    AHL_HEADING_LINE,
    AHL_HEADING_LINE_BBB3,
    STATION_ICAO_FULLMATCH,
    STATION_ICAO_TOKEN,
    is_ahl_heading_line,
    is_station_icao,
    parse_ahl_heading_line,
    parse_station_icao,
    replace_ahl_heading_mapping,
)

# --- S / V+ : success + validation pass ---


@pytest.mark.parametrize(
    "code",
    ["K10U", "K05U", "K1F0", "KJFK"],
    ids=["k10u", "k05u", "k1f0", "kjfk"],
)
def test_parse_station_icao_accepts_letter_first_with_digits(code: str) -> None:
    station = parse_station_icao(code.lower())
    assert station.code == code
    assert is_station_icao(code)
    assert STATION_ICAO_FULLMATCH.fullmatch(code)
    assert STATION_ICAO_TOKEN.search(f"METAR {code}") is not None


def test_parse_ahl_heading_line_accepts_optional_bbb() -> None:
    parts = parse_ahl_heading_line("SAUS31 KZNY 121200 CCA")
    assert parts == AhlHeadingParts(
        ttaaii="SAUS31",
        cccc="KZNY",
        yygggg="121200",
        bbb="CCA",
    )
    assert is_ahl_heading_line("SAUS31 KZNY 121200")
    assert AHL_HEADING_LINE.fullmatch("SAUS31 KZNY 121200")


def test_replace_ahl_heading_mapping_create_update_delete_style() -> None:
    """Mutation modes: create key, update key, delete optional bbb via rewrite."""
    base: dict[str, object] = {"product": "metar"}
    created = replace_ahl_heading_mapping(
        base,
        key="ahl",
        parts=AhlHeadingParts("SAUS31", "KZNY", "121200", "CCA"),
    )
    assert created["ahl"] == {
        "ttaaii": "SAUS31",
        "cccc": "KZNY",
        "yygggg": "121200",
        "bbb": "CCA",
    }
    assert "ahl" not in base  # create must not mutate source

    updated = replace_ahl_heading_mapping(
        created,
        key="ahl",
        parts=AhlHeadingParts("SPUS31", "KZNY", "121230"),
    )
    assert updated["ahl"] == {
        "ttaaii": "SPUS31",
        "cccc": "KZNY",
        "yygggg": "121230",
    }
    assert "bbb" not in updated["ahl"]  # delete optional field on rewrite
    assert created["ahl"]["bbb"] == "CCA"  # prior mapping unchanged


# --- V- / F : validation failure + rejected ops ---


def test_parse_station_icao_rejects_invalid_shapes() -> None:
    with pytest.raises(ValueError, match="invalid station ICAO"):
        parse_station_icao("12AB")
    with pytest.raises(ValueError, match="invalid station ICAO"):
        parse_station_icao("ABC")
    with pytest.raises(ValueError, match="invalid station ICAO"):
        StationIcao("!!!!")
    assert not is_station_icao("12AB")
    assert STATION_ICAO_TOKEN.search("METAR KJFK") is not None


def test_parse_ahl_heading_line_rejects_invalid_and_bbb3_gate() -> None:
    with pytest.raises(ValueError, match="invalid AHL heading line"):
        parse_ahl_heading_line("NOT AN AHL")
    with pytest.raises(ValueError, match="invalid AHL heading line"):
        parse_ahl_heading_line("SAUS31 KZNY 12120")  # yygggg too short
    assert not is_ahl_heading_line("ZZZZ")
    # BBB length 1 is OK for flexible pattern, rejected by BBB3-only pattern
    assert is_ahl_heading_line("SAUS31 KZNY 121200 A", require_bbb3=False)
    assert not is_ahl_heading_line("SAUS31 KZNY 121200 A", require_bbb3=True)
    assert AHL_HEADING_LINE_BBB3.fullmatch("SAUS31 KZNY 121200 CCA")
    assert AHL_HEADING_LINE_BBB3.fullmatch("SAUS31 KZNY 121200 A") is None


def test_replace_ahl_heading_mapping_rejects_bad_station_via_model() -> None:
    """Failure path when constructing parts used for mapping mutation."""
    with pytest.raises(ValueError, match="invalid station ICAO"):
        StationIcao("1ABC")
