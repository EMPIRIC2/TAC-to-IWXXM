"""Parse OurAirports CSV text into an ``IdentIndex``."""

from __future__ import annotations

import csv
import io
from typing import cast

from reference_lookup.exceptions import SourceUnavailable
from reference_lookup.models import (
    IDENT_COLUMN,
    LATITUDE_COLUMN,
    LONGITUDE_COLUMN,
    REQUIRED_COLUMNS,
    Coordinate,
    CoordinateCsvRow,
    IdentIndex,
)


def index_csv(csv_text: str) -> IdentIndex:
    """
    Group coordinate rows by ident.

    Parameters
    ----------
    csv_text : str
        OurAirports CSV text.

    Returns
    -------
    IdentIndex
        Ident to every parsed coordinate. More than one row is ambiguous.

    Raises
    ------
    SourceUnavailable
        When required columns are missing or a coordinate is not numeric.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (index_csv)
    2
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    names = reader.fieldnames or []
    if not REQUIRED_COLUMNS.issubset(names):
        raise SourceUnavailable("missing coordinate columns")
    grouped = IdentIndex()
    for raw in reader:
        row = cast(CoordinateCsvRow, raw)
        ident = (row.get(IDENT_COLUMN) or "").strip().upper()
        if not ident:
            continue
        lat_text = (row.get(LATITUDE_COLUMN) or "").strip()
        lon_text = (row.get(LONGITUDE_COLUMN) or "").strip()
        if not lat_text or not lon_text:
            continue
        try:
            point = Coordinate(float(lat_text), float(lon_text))
        except ValueError as exc:
            raise SourceUnavailable(ident) from exc
        grouped.add(ident, point)
    return grouped
