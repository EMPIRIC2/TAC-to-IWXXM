"""Coordinate lookup for convert.

The live source is OurAirports. Callers inject a fixture in tests.
"""

from reference_lookup.lookup import (
    SourceUnavailable,
    lookup_coordinate,
    set_coordinate_source,
)

__all__ = [
    "SourceUnavailable",
    "lookup_coordinate",
    "set_coordinate_source",
]
