"""Unit tests for IWXXM version formatting helpers."""

from src.config import version_formatting as vf


def test_get_coordinate_decimals_known_and_default() -> None:
    assert vf.get_coordinate_decimals("2016") == 2
    assert vf.get_coordinate_decimals("2025-2") == 8
    assert vf.get_coordinate_decimals("unknown") == 2


def test_get_elevation_rounding_known_and_default() -> None:
    assert vf.get_elevation_rounding("2018") == 1
    assert vf.get_elevation_rounding("2025-2") == 0
    assert vf.get_elevation_rounding("unknown") == 0


def test_format_coordinates_respects_version_precision() -> None:
    lat = 61.123456789
    lon = -45.987654321

    assert vf.format_coordinates(lat, lon, "2016") == "61.12 -45.99"
    assert vf.format_coordinates(lat, lon, "2025-2") == "61.12345679 -45.98765432"


def test_format_elevation_applies_rounding_rules() -> None:
    assert vf.format_elevation(123.6, "2016") == 123.6
    assert vf.format_elevation(123.6, "2025-2") == 124.0
    assert vf.format_elevation(123.4, "unknown") == 123.0
