"""TC-EVPVD-004..005 — station name enrich via location resolver (#724).

[Corpus: product §F9] [Corpus: tests §TC-EVPVD] [Corpus: api]
"""

from __future__ import annotations

from tac_decoding import decode_tac, set_location_name_resolver


def test_tc_evpvd_004_station_name_on_decode_hit() -> None:
    set_location_name_resolver(lambda icao: "John F. Kennedy International Airport" if icao == "KJFK" else None)
    try:
        result = decode_tac(
            "METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3012=",
            product="METAR",
        )
        station = next(s for s in result.segments if s.code.upper() == "KJFK")
        assert "John F. Kennedy International Airport" in station.explanation
        assert "station John F. Kennedy International Airport (KJFK)" in result.summary
    finally:
        set_location_name_resolver(None)


def test_tc_evpvd_005_station_name_soft_fail_unknown() -> None:
    set_location_name_resolver(lambda _icao: None)
    try:
        result = decode_tac(
            "METAR ZZ99 121251Z 18004KT 10SM FEW250 24/18 A3012=",
            product="METAR",
        )
        station = next(s for s in result.segments if s.code.upper() == "ZZ99")
        assert "John F." not in station.explanation
        assert "ZZ99" in station.explanation
        assert "station ZZ99" in result.summary
        assert result.summary  # soft-fail still produces summary
    finally:
        set_location_name_resolver(None)


def test_tc_evpvd_004_summary_skips_parenthetical_place_after_dash() -> None:
    """Coverage: named-station sep present but place is parenthetical → code-only."""
    from tac_decoding.decode import DecodeSegment, _sentence_from_segment

    seg = DecodeSegment(
        start=0,
        end=4,
        code="KJFK",
        explanation="ICAO station location indicator — (legacy)",
    )
    assert _sentence_from_segment(seg) == "station KJFK"
    set_location_name_resolver(lambda icao: "Test Field" if icao == "KJFK" else None)
    try:
        result = decode_tac(
            "SPECI KJFK 121251Z 18004KT 10SM FEW250 24/18 A3012=",
            product="SPECI",
        )
        station = next(s for s in result.segments if s.code.upper() == "KJFK")
        assert "Test Field" in station.explanation
        assert "station Test Field (KJFK)" in result.summary
    finally:
        set_location_name_resolver(None)
