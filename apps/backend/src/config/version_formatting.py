"""
Version-Specific Formatting Rules for IWXXM

Defines how coordinates, elevations, and other data should be formatted
when generating IWXXM XML for different versions.
"""

from typing import Dict, TypedDict


class CoordinatePrecisionRule(TypedDict):
    """Rule for coordinate precision formatting."""

    decimals: int
    rationale: str


class ElevationFormatRule(TypedDict):
    """Rule for elevation formatting."""

    unit: str  # Currently always "M" (meters)
    round_to: int  # Number of decimal places to round to (0 = round to int)
    rationale: str


# Coordinate precision rules by version
# Precision determines gml:pos format: e.g., 2 decimals = "61.17 -45.42"
COORDINATE_PRECISION: Dict[str, CoordinatePrecisionRule] = {
    "2016": {"decimals": 2, "rationale": "Legacy precision from original implementations"},
    "2018": {"decimals": 2, "rationale": "ICAO Annex 3 legacy standard (~1.1 km per degree)"},
    "2021-2": {"decimals": 6, "rationale": "Increased precision ~0.111 meters per degree"},
    "2023-1": {"decimals": 6, "rationale": "Same as 2021-2 for compatibility"},
    "2025-2": {"decimals": 8, "rationale": "ICAO Annex 3 high-precision standard ~1.1 mm per degree"},
}


# Elevation formatting rules by version
ELEVATION_FORMAT: Dict[str, ElevationFormatRule] = {
    "2016": {"unit": "M", "round_to": 1, "rationale": "Round to nearest meter for legacy systems"},
    "2018": {"unit": "M", "round_to": 1, "rationale": "Round to nearest meter"},
    "2021-2": {"unit": "M", "round_to": 0, "rationale": "No rounding - maintain source precision"},
    "2023-1": {"unit": "M", "round_to": 0, "rationale": "No rounding"},
    "2025-2": {"unit": "M", "round_to": 0, "rationale": "No rounding - maintain full precision"},
}


# Airport name formatting: short vs long
AIRPORT_NAME_FORMAT = {
    "2016": "short",  # "BGBW"
    "2018": "short",  # "BGBW"
    "2021-2": "long",  # "NARSARSUAQ INTERNATIONAL AIRPORT"
    "2023-1": "long",  # Same as 2021-2
    "2025-2": "long",  # High-precision version
}


# IATA code inclusion by version
INCLUDE_IATA_CODE = {
    "2016": False,
    "2018": False,
    "2021-2": False,  # Added later
    "2023-1": False,
    "2025-2": True,  # New functionality
}


# Designator element inclusion (ICAO 4-letter code)
INCLUDE_DESIGNATOR = {
    "2016": True,
    "2018": True,
    "2021-2": False,  # Removed in favor of locationIndicatorICAO
    "2023-1": False,
    "2025-2": False,
}


def get_coordinate_decimals(version: str) -> int:
    """Get number of decimal places for coordinates in a version.

    Args:
        version: IWXXM version (e.g., "2025-2")

    Returns:
        Number of decimal places (2-8)
    """
    return COORDINATE_PRECISION.get(version, {}).get("decimals", 2)


def get_elevation_rounding(version: str) -> int:
    """Get elevation rounding rule for a version.

    Args:
        version: IWXXM version

    Returns:
        Number of decimal places to round to (0 = round to integer)
    """
    return ELEVATION_FORMAT.get(version, {}).get("round_to", 0)


def format_coordinates(lat: float, lon: float, version: str) -> str:
    """Format coordinates for a specific IWXXM version.

    Args:
        lat: Latitude
        lon: Longitude
        version: IWXXM version

    Returns:
        Formatted coordinate string for gml:pos
    """
    decimals = get_coordinate_decimals(version)
    return f"{lat:.{decimals}f} {lon:.{decimals}f}"


def format_elevation(elevation_m: float, version: str) -> int:
    """Format elevation for a specific IWXXM version.

    Args:
        elevation_m: Elevation in meters
        version: IWXXM version

    Returns:
        Formatted elevation value
    """
    rounding = get_elevation_rounding(version)
    return round(elevation_m, rounding)
