"""Typed OurAirports CSV row fields used when indexing coordinates."""

from __future__ import annotations

from typing import TypedDict


class CoordinateCsvRow(TypedDict, total=False):
    """
    One OurAirports CSV row with the columns this package reads.

    Attributes
    ----------
    ident :
        Navaid or airport identifier.
    latitude_deg :
        Latitude text from the CSV.
    longitude_deg :
        Longitude text from the CSV.
    """

    ident: str
    latitude_deg: str
    longitude_deg: str


IDENT_COLUMN = "ident"
LATITUDE_COLUMN = "latitude_deg"
LONGITUDE_COLUMN = "longitude_deg"
REQUIRED_COLUMNS = frozenset({IDENT_COLUMN, LATITUDE_COLUMN, LONGITUDE_COLUMN})
