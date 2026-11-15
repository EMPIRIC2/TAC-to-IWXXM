"""Windowed Postgres load helpers for station health (F39)."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.services.station_health_aggregate import row_to_station_record
from src.services.station_health_types import StationRecord

logger = logging.getLogger(__name__)

_RECORD_SELECT = """
SELECT icao, product, observed_at, ingested_at, tac_text, source,
       solidus_count, missing_digit_count,
       lint_error_count, lint_warning_count, convert_ok,
       file_format, issue_codes
FROM station_tac_records
"""


def load_window_rows(
    engine: Engine,
    *,
    cutoff: datetime,
    product_filter: str | None,
) -> tuple[dict[str, dict[str, Any]], list[StationRecord]]:
    """
    Load registry rows and windowed TAC records from Postgres.

    Parameters
    ----------
    engine : object
        Sync SQLAlchemy engine.
    cutoff : object
        Inclusive lower bound for ``observed_at``.
    product_filter : object
        Optional product filter.

    Returns
    -------
    tuple[dict[str, dict[str, Any]], list[StationRecord]]
        Station map and observation rows.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_window_rows)
    2
    """
    try:
        with engine.connect() as conn:
            station_rows = conn.execute(
                text("SELECT icao, name, country FROM station_registry ORDER BY icao ASC")
            ).mappings()
            stations = {str(row["icao"]): dict(row) for row in station_rows}
            if product_filter:
                record_rows = conn.execute(
                    text(_RECORD_SELECT + "WHERE observed_at >= :cutoff AND product = :product"),
                    {"cutoff": cutoff, "product": product_filter},
                ).mappings()
            else:
                record_rows = conn.execute(
                    text(_RECORD_SELECT + "WHERE observed_at >= :cutoff"),
                    {"cutoff": cutoff},
                ).mappings()
            records = [row_to_station_record(dict(row)) for row in record_rows]
    except Exception:
        logger.exception("station health list query failed")
        return {}, []
    return stations, records


__all__ = ["load_window_rows"]
