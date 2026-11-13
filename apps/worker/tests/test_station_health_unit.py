"""Worker station health helpers."""

from __future__ import annotations

from metar_worker.station_health import extract_icao, solidus_counts


def test_extract_icao_metar_and_taf() -> None:
    """Parse ICAO from METAR and TAF; skip SIGMET."""
    assert extract_icao("METAR KJFK 010000Z 18008KT=", "METAR") == "KJFK"
    assert extract_icao("TAF KLAX 010000Z 0100/0206 25010KT=", "TAF") == "KLAX"
    assert extract_icao("SIGMET ...", "SIGMET") is None


def test_solidus_counts() -> None:
    """Count solidus characters and missing-digit runs."""
    solidus, missing = solidus_counts("METAR KJFK 010000Z ////KT 15/07=")
    assert solidus == 5
    assert missing == 1
