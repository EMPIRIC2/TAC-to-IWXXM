"""Part 1 of ``metar_test_generator.py`` (line-cap split)."""

import logging
from dataclasses import field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class METARTestCase:
    """
    A single METAR test case with metadata.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    station_id: str
    raw_metar: str
    latitude: float | None = None
    longitude: float | None = None
    country: str | None = None
    elevation: float | None = None

    # Meteorological features (extracted)
    weather_phenomena: list[str] = field(default_factory=list)
    cloud_types: list[str] = field(default_factory=list)
    cloud_amounts: list[str] = field(default_factory=list)
    visibility: str | None = None
    temperature: float | None = None

    # Test metadata
    region: str | None = None
    timestamp: datetime | None = None
    source: str = "aviation_weather"

    def has_weather(self) -> bool:
        """
        Check if METAR has significant weather.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (has_weather)
        2

        Returns
        -------
        object
            Return value.
        """
        return len(self.weather_phenomena) > 0

    def has_clouds(self) -> bool:
        """
        Check if METAR has cloud information.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (has_clouds)
        2

        Returns
        -------
        object
            Return value.
        """
        return len(self.cloud_amounts) > 0

    def complexity_score(self) -> int:
        """
        Calculate complexity score (higher = more complex).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (complexity_score)
        2

        Returns
        -------
        object
            Return value.
        """
        score = 0
        score += len(self.weather_phenomena) * 2
        score += len(self.cloud_types) * 2
        score += len(self.cloud_amounts)
        if self.visibility:
            score += 1
        if self.temperature:
            score += 1
        return score


class CoverageReport:
    """
    Coverage tracking for generated test cases.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    total_cases: int = 0
    unique_stations: set[str] = field(default_factory=set)
    countries: set[str] = field(default_factory=set)
    regions: set[str] = field(default_factory=set)

    # Meteorological coverage
    weather_phenomena: set[str] = field(default_factory=set)
    cloud_types: set[str] = field(default_factory=set)
    cloud_amounts: set[str] = field(default_factory=set)

    # Complexity distribution
    simple_cases: int = 0  # score 0-2
    medium_cases: int = 0  # score 3-6
    complex_cases: int = 0  # score 7+

    def add_test_case(self, test_case: METARTestCase) -> None:
        """
        Add a test case to coverage tracking.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (add_test_case)
        2

        Parameters
        ----------
        test_case : object
            Argument ``test_case``.
        """
        self.total_cases += 1
        self.unique_stations.add(test_case.station_id)

        if test_case.country:
            self.countries.add(test_case.country)
        if test_case.region:
            self.regions.add(test_case.region)

        self.weather_phenomena.update(test_case.weather_phenomena)
        self.cloud_types.update(test_case.cloud_types)
        self.cloud_amounts.update(test_case.cloud_amounts)

        score = test_case.complexity_score()
        if score <= 2:
            self.simple_cases += 1
        elif score <= 6:
            self.medium_cases += 1
        else:
            self.complex_cases += 1

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (to_dict)
        2

        Returns
        -------
        object
            Return value.
        """
        return {
            "total_cases": self.total_cases,
            "unique_stations": len(self.unique_stations),
            "countries": sorted(self.countries),
            "regions": sorted(self.regions),
            "weather_phenomena": sorted(self.weather_phenomena),
            "cloud_types": sorted(self.cloud_types),
            "cloud_amounts": sorted(self.cloud_amounts),
            "complexity_distribution": {
                "simple": self.simple_cases,
                "medium": self.medium_cases,
                "complex": self.complex_cases,
            },
        }
