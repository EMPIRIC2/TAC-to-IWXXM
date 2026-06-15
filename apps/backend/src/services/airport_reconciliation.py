"""Airport data reconciliation service.

Reconciles airport metadata from multiple sources with priority-based
conflict resolution.
"""
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..clients.aviation_weather_client import AviationWeatherClient
from ..clients.openaip_client import OpenAIPClient

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source priority."""
    OPENAIP = 1  # Highest priority
    GIFTS = 2
    AVIATION_WEATHER = 3
    FALLBACK = 4  # Lowest priority


@dataclass
class ConflictLog:
    """Log entry for data conflicts."""

    icao: str
    field: str
    sources: Dict[str, any] = field(default_factory=dict)
    resolution: str = ""
    winner: str = ""

    def __str__(self) -> str:
        """Format conflict for logging."""
        values_str = ", ".join(
            f"{src}={val}" for src, val in self.sources.items()
        )
        return (
            f"Conflict for {self.icao}.{self.field}: "
            f"{values_str} → resolved to {self.winner}={self.resolution}"
        )


@dataclass
class ReconciledAirport:
    """Reconciled airport data from multiple sources."""

    icao_code: str
    name: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[float] = None  # meters
    iata_code: Optional[str] = None

    # Data provenance
    sources: Set[str] = field(default_factory=set)
    primary_source: Optional[str] = None
    conflicts: List[ConflictLog] = field(default_factory=list)

    # Confidence scores
    coordinate_confidence: float = 1.0  # 0.0-1.0
    elevation_confidence: float = 1.0

    def has_conflicts(self) -> bool:
        """Check if any conflicts were found during reconciliation."""
        return len(self.conflicts) > 0

    def get_conflict_summary(self) -> str:
        """Get summary of conflicts."""
        if not self.conflicts:
            return "No conflicts"

        return f"{len(self.conflicts)} conflicts:\n" + "\n".join(
            f"  - {conflict}" for conflict in self.conflicts
        )


class AirportReconciliationService:
    """Service for reconciling airport data from multiple sources.

    Priority order:
    1. OpenAIP (most comprehensive, community-maintained)
    2. GIFTs internal database
    3. AviationWeather.gov API
    4. Fallback/default values
    """

    def __init__(
        self,
        openaip_client: Optional[OpenAIPClient] = None,
        aviation_weather_client: Optional[AviationWeatherClient] = None,
        gifts_data_path: Optional[Path] = None
    ):
        """Initialize reconciliation service.

        Args:
            openaip_client: OpenAIP client instance
            aviation_weather_client: AviationWeather client instance
            gifts_data_path: Path to GIFTs airport data
        """
        self.openaip = openaip_client or OpenAIPClient()
        self.aviation_weather = aviation_weather_client or AviationWeatherClient()
        self.gifts_data_path = gifts_data_path or Path("data/af-airports.csv")

        # Cache for GIFTs data
        self._gifts_cache: Dict[str, Dict] = {}
        self._gifts_loaded = False

        # Reconciliation statistics
        self.stats = {
            "total_queries": 0,
            "openaip_hits": 0,
            "gifts_hits": 0,
            "aviation_weather_hits": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0
        }

    def _load_gifts_data(self) -> None:
        """Load GIFTs airport data from CSV."""
        if self._gifts_loaded:
            return

        if not self.gifts_data_path.exists():
            logger.warning(f"GIFTs airport data not found: {self.gifts_data_path}")
            self._gifts_loaded = True
            return

        try:
            import csv

            with open(self.gifts_data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Handle both field name formats
                    icao = (row.get('icao_code') or row.get('icao', '')).strip().upper()
                    if not icao:
                        continue

                    # Convert elevation from feet to meters if needed
                    elevation = self._safe_float(row.get('elevation_ft') or row.get('elevation'))
                    if elevation:
                        elevation = elevation * 0.3048  # feet to meters

                    self._gifts_cache[icao] = {
                        'icao': icao,
                        'name': row.get('name', '').strip(),
                        'country': row.get('iso_country', row.get('country', '')).strip(),
                        'latitude': self._safe_float(row.get('latitude_deg') or row.get('latitude')),
                        'longitude': self._safe_float(row.get('longitude_deg') or row.get('longitude')),
                        'elevation': elevation
                    }

            logger.info(f"Loaded {len(self._gifts_cache)} airports from GIFTs database")

        except Exception as e:
            logger.warning(f"Failed to load GIFTs data: {e}")

        self._gifts_loaded = True

    def _safe_float(self, value: any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def get_airport(self, icao: str) -> Optional[ReconciledAirport]:
        """Get reconciled airport data for ICAO code.

        Args:
            icao: ICAO station identifier

        Returns:
            ReconciledAirport with best-effort data or None if not found
        """
        self.stats["total_queries"] += 1
        icao = icao.upper()

        # Collect data from all sources
        sources_data = {}

        # Source 1: OpenAIP
        openaip_data = self.openaip.get_airport_by_icao(icao)
        if openaip_data:
            sources_data[DataSource.OPENAIP] = openaip_data
            self.stats["openaip_hits"] += 1

        # Source 2: GIFTs
        self._load_gifts_data()
        gifts_data = self._gifts_cache.get(icao)
        if gifts_data:
            sources_data[DataSource.GIFTS] = gifts_data
            self.stats["gifts_hits"] += 1

        # Source 3: AviationWeather (Note: Limited metadata from their API)
        # We could enhance this by parsing station lists, but for now skip
        # aviation_weather_data = self._fetch_aviation_weather_metadata(icao)
        # if aviation_weather_data:
        #     sources_data[DataSource.AVIATION_WEATHER] = aviation_weather_data
        #     self.stats["aviation_weather_hits"] += 1

        # If no data found, return None
        if not sources_data:
            return None

        # Reconcile data
        return self._reconcile(icao, sources_data)

    def _reconcile(
        self,
        icao: str,
        sources_data: Dict[DataSource, any]
    ) -> ReconciledAirport:
        """Reconcile data from multiple sources.

        Args:
            icao: ICAO code
            sources_data: Data from each source

        Returns:
            ReconciledAirport with merged data
        """
        # Priority order
        priority_order = [
            DataSource.OPENAIP,
            DataSource.GIFTS,
            DataSource.AVIATION_WEATHER
        ]

        # Determine primary source (highest priority with data)
        primary_source = None
        for source in priority_order:
            if source in sources_data:
                primary_source = source
                break

        if not primary_source:
            # No data found
            return None

        # Start with primary source data
        primary_data = sources_data[primary_source]

        # Initialize reconciled airport
        reconciled = ReconciledAirport(
            icao_code=icao,
            name=self._get_field(primary_data, 'name', ''),
            country=self._get_field(primary_data, 'country', ''),
            latitude=self._get_field(primary_data, 'latitude', None),
            longitude=self._get_field(primary_data, 'longitude', None),
            elevation=self._get_field(primary_data, 'elevation', None),
            iata_code=self._get_field(primary_data, 'iata_code', None),
            sources=set(source.name for source in sources_data.keys()),
            primary_source=primary_source.name
        )

        # Check for conflicts and merge
        conflicts = []

        # Compare each field across sources
        for field_name in ['name', 'country', 'latitude', 'longitude', 'elevation']:
            conflict = self._check_field_conflict(
                icao, field_name, sources_data, priority_order
            )
            if conflict:
                conflicts.append(conflict)
                self.stats["conflicts_detected"] += 1

        if conflicts:
            reconciled.conflicts = conflicts
            self.stats["conflicts_resolved"] += len(conflicts)

            # Log conflicts
            for conflict in conflicts:
                logger.debug(str(conflict))

        # Calculate confidence scores
        reconciled.coordinate_confidence = self._calculate_coordinate_confidence(
            sources_data, reconciled.latitude, reconciled.longitude
        )
        reconciled.elevation_confidence = self._calculate_elevation_confidence(
            sources_data, reconciled.elevation
        )

        return reconciled

    def _get_field(self, data: any, field: str, default: any) -> any:
        """Get field from data object (handles both dict and object)."""
        if isinstance(data, dict):
            return data.get(field, default)
        else:
            return getattr(data, field, default)

    def _check_field_conflict(
        self,
        icao: str,
        field: str,
        sources_data: Dict[DataSource, any],
        priority_order: List[DataSource]
    ) -> Optional[ConflictLog]:
        """Check if field has conflicting values across sources.

        Args:
            icao: ICAO code
            field: Field name
            sources_data: Data from each source
            priority_order: Source priority order

        Returns:
            ConflictLog if conflict found, None otherwise
        """
        # Collect values from all sources
        values = {}
        for source, data in sources_data.items():
            value = self._get_field(data, field, None)
            if value is not None:
                values[source.name] = value

        # No conflict if only one source or all agree
        if len(values) <= 1:
            return None

        unique_values = set(str(v) for v in values.values())
        if len(unique_values) == 1:
            return None  # All sources agree

        # Conflict detected - resolve by priority
        winner = None
        winner_value = None
        for source in priority_order:
            if source in sources_data:
                value = self._get_field(sources_data[source], field, None)
                if value is not None:
                    winner = source.name
                    winner_value = value
                    break

        return ConflictLog(
            icao=icao,
            field=field,
            sources=values,
            resolution=str(winner_value),
            winner=winner
        )

    def _calculate_coordinate_confidence(
        self,
        sources_data: Dict[DataSource, any],
        final_lat: Optional[float],
        final_lon: Optional[float]
    ) -> float:
        """Calculate confidence score for coordinates.

        Confidence is higher when:
        - Multiple sources agree
        - Data comes from high-priority source

        Returns:
            Confidence score (0.0-1.0)
        """
        if final_lat is None or final_lon is None:
            return 0.0

        # Count sources with coordinates
        coords_count = 0
        agreeing_count = 0

        tolerance = 0.01  # ~1km tolerance

        for source, data in sources_data.items():
            lat = self._get_field(data, 'latitude', None)
            lon = self._get_field(data, 'longitude', None)

            if lat is not None and lon is not None:
                coords_count += 1

                # Check if agrees with final value
                if (abs(lat - final_lat) < tolerance and
                    abs(lon - final_lon) < tolerance):
                    agreeing_count += 1

        if coords_count == 0:
            return 0.0

        # Base confidence on agreement ratio
        agreement_ratio = agreeing_count / coords_count

        # Boost for OpenAIP source
        if DataSource.OPENAIP in sources_data:
            agreement_ratio = min(1.0, agreement_ratio + 0.2)

        return agreement_ratio

    def _calculate_elevation_confidence(
        self,
        sources_data: Dict[DataSource, any],
        final_elevation: Optional[float]
    ) -> float:
        """Calculate confidence score for elevation.

        Returns:
            Confidence score (0.0-1.0)
        """
        if final_elevation is None:
            return 0.0

        # Count sources with elevation
        elev_count = 0
        agreeing_count = 0

        tolerance = 10.0  # 10 meter tolerance

        for source, data in sources_data.items():
            elev = self._get_field(data, 'elevation', None)

            if elev is not None:
                elev_count += 1

                # Check if agrees with final value
                if abs(elev - final_elevation) < tolerance:
                    agreeing_count += 1

        if elev_count == 0:
            return 0.0

        agreement_ratio = agreeing_count / elev_count

        # Boost for OpenAIP source
        if DataSource.OPENAIP in sources_data:
            agreement_ratio = min(1.0, agreement_ratio + 0.2)

        return agreement_ratio

    def get_statistics(self) -> Dict[str, any]:
        """Get reconciliation statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            **self.stats,
            "gifts_airports_loaded": len(self._gifts_cache),
            "openaip_available": self.openaip is not None,
            "conflict_rate": (
                self.stats["conflicts_detected"] / self.stats["total_queries"]
                if self.stats["total_queries"] > 0 else 0.0
            )
        }
