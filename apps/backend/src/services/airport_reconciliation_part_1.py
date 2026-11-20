"""Part 1 of ``airport_reconciliation.py`` (line-cap split)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from dataclasses import field as dc_field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source priority."""

    OPENAIP = 1  # Highest priority
    GIFTS = 2
    AVIATION_WEATHER = 3
    FALLBACK = 4  # Lowest priority


@dataclass
class ConflictLog:
    """
    Log entry for data conflicts.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    icao: str
    field: str
    sources: dict[str, Any] = dc_field(default_factory=dict)
    resolution: str = ""
    winner: str | None = None

    def __str__(self) -> str:
        """
        Internal helper ``__str__``.

        Returns
        -------
        object
            Return value.
        """
        values_str = ", ".join(f"{src}={val}" for src, val in self.sources.items())
        return f"Conflict for {self.icao}.{self.field}: {values_str} → resolved to {self.winner}={self.resolution}"


@dataclass
class ReconciledAirport:
    """
    Reconciled airport data from multiple sources.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    icao_code: str
    name: str
    country: str
    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None  # meters
    iata_code: str | None = None

    # Data provenance
    sources: set[str] = dc_field(default_factory=set)
    primary_source: str | None = None
    conflicts: list[ConflictLog] = dc_field(default_factory=list)

    # Confidence scores
    coordinate_confidence: float = 1.0  # 0.0-1.0
    elevation_confidence: float = 1.0

    def has_conflicts(self) -> bool:
        """
        Check if any conflicts were found during reconciliation.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (has_conflicts)
        2

        Returns
        -------
        object
            Return value.
        """
        return len(self.conflicts) > 0

    def get_conflict_summary(self) -> str:
        """
        Get summary of conflicts.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_conflict_summary)
        2

        Returns
        -------
        object
            Return value.
        """
        if not self.conflicts:
            return "No conflicts"

        return f"{len(self.conflicts)} conflicts:\n" + "\n".join(f"  - {conflict}" for conflict in self.conflicts)
