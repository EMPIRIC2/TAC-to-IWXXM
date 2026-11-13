"""Shared station health types and metric catalog (F39)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

DEFAULT_METRICS: tuple[dict[str, Any], ...] = (
    {
        "id": "availability",
        "label": "Availability",
        "description": "Share of expected TAC reports received in the window",
        "unit": "percent",
        "higher_is_better": True,
        "enabled": True,
        "sort_order": 10,
    },
    {
        "id": "solidus_rate",
        "label": "Solidus rate",
        "description": "Share of solidus characters in received TAC text",
        "unit": "ratio",
        "higher_is_better": False,
        "enabled": True,
        "sort_order": 20,
    },
    {
        "id": "missing_digit_rate",
        "label": "Missing digit rate",
        "description": "Average missing-digit solidus runs per report",
        "unit": "ratio",
        "higher_is_better": False,
        "enabled": True,
        "sort_order": 30,
    },
    {
        "id": "lint_severity",
        "label": "Lint severity",
        "description": "Quality score from stored lint error and warning counts",
        "unit": "percent",
        "higher_is_better": True,
        "enabled": True,
        "sort_order": 40,
    },
    {
        "id": "overall_grade",
        "label": "Overall grade",
        "description": "Combined availability and quality letter grade",
        "unit": "letter",
        "higher_is_better": True,
        "enabled": True,
        "sort_order": 50,
    },
)


@dataclass(slots=True)
class StationRecord:
    """
    One stored TAC observation for a station.

    Attributes
    ----------
    icao : str
        Station ICAO identifier.
    product : str
        Lowercase product family (metar, speci, taf, ...).
    observed_at : datetime
        Observation time (UTC).
    ingested_at : datetime
        Ingest timestamp (UTC).
    tac_text : str
        Raw TAC body.
    source : str
        Ingest source label.
    solidus_count : int
        Solidus character count.
    missing_digit_count : int
        Missing-digit solidus runs.
    lint_error_count : int
        Stored lint error count.
    lint_warning_count : int
        Stored lint warning count.
    convert_ok : bool | None
        Conversion success flag when known.
    character_count : int
        Length of ``tac_text``.
    """

    icao: str
    product: str
    observed_at: datetime
    ingested_at: datetime
    tac_text: str
    source: str
    solidus_count: int
    missing_digit_count: int
    lint_error_count: int
    lint_warning_count: int
    convert_ok: bool | None
    character_count: int


@dataclass(slots=True)
class StationMeta:
    """
    Station registry row.

    Attributes
    ----------
    icao : str
        Station ICAO identifier.
    name : str | None
        Optional station name.
    country : str | None
        Optional ISO country code.
    latitude : float | None
        Optional latitude.
    longitude : float | None
        Optional longitude.
    first_seen_at : datetime | None
        First observation time.
    last_seen_at : datetime | None
        Latest observation time.
    """

    icao: str
    name: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None


class StationHealthStoreProtocol(Protocol):
    """Shared read/write surface for memory and Postgres stores."""

    def reset(self) -> None:
        """Clear mutable state when supported."""
        ...

    def list_metrics(self) -> list[dict[str, Any]]:
        """Return enabled metric definitions."""
        ...

    def record_observation(
        self,
        *,
        icao: str,
        product: str,
        tac_text: str,
        source: str,
        observed_at: datetime | None = None,
        name: str | None = None,
        lint_error_count: int = 0,
        lint_warning_count: int = 0,
        convert_ok: bool | None = None,
    ) -> StationRecord | None:
        """Append one observation."""
        ...

    def list_stations(
        self,
        *,
        window_key: str = "6h",
        product: str | None = None,
        grade: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Build the public list payload."""
        ...

    def get_station(self, icao: str) -> dict[str, Any] | None:
        """Build the public detail payload."""
        ...


__all__ = [
    "DEFAULT_METRICS",
    "StationHealthStoreProtocol",
    "StationMeta",
    "StationRecord",
]
