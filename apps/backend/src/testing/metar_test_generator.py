"""Dynamic METAR test generator for comprehensive coverage.

Generates diverse test cases using live data from AviationWeather.gov,
OpenAIP, and WMO codelists.
"""
import json
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..clients.aviation_weather_client import AviationWeatherClient
from ..clients.openaip_client import OpenAIPClient
from ..clients.wmo_codelists_client import WMOCodelistsClient
from ..services.airport_reconciliation import AirportReconciliationService

logger = logging.getLogger(__name__)


@dataclass
class METARTestCase:
    """A single METAR test case with metadata."""

    station_id: str
    raw_metar: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country: Optional[str] = None
    elevation: Optional[float] = None

    # Meteorological features (extracted)
    weather_phenomena: List[str] = field(default_factory=list)
    cloud_types: List[str] = field(default_factory=list)
    cloud_amounts: List[str] = field(default_factory=list)
    visibility: Optional[str] = None
    temperature: Optional[float] = None

    # Test metadata
    region: Optional[str] = None
    timestamp: Optional[datetime] = None
    source: str = "aviation_weather"

    def has_weather(self) -> bool:
        """Check if METAR has significant weather."""
        return len(self.weather_phenomena) > 0

    def has_clouds(self) -> bool:
        """Check if METAR has cloud information."""
        return len(self.cloud_amounts) > 0

    def complexity_score(self) -> int:
        """Calculate complexity score (higher = more complex)."""
        score = 0
        score += len(self.weather_phenomena) * 2
        score += len(self.cloud_types) * 2
        score += len(self.cloud_amounts)
        if self.visibility:
            score += 1
        if self.temperature:
            score += 1
        return score


@dataclass
class CoverageReport:
    """Coverage tracking for generated test cases."""

    total_cases: int = 0
    unique_stations: Set[str] = field(default_factory=set)
    countries: Set[str] = field(default_factory=set)
    regions: Set[str] = field(default_factory=set)

    # Meteorological coverage
    weather_phenomena: Set[str] = field(default_factory=set)
    cloud_types: Set[str] = field(default_factory=set)
    cloud_amounts: Set[str] = field(default_factory=set)

    # Complexity distribution
    simple_cases: int = 0  # score 0-2
    medium_cases: int = 0  # score 3-6
    complex_cases: int = 0  # score 7+

    def add_test_case(self, test_case: METARTestCase) -> None:
        """Add a test case to coverage tracking."""
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
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
                "complex": self.complex_cases
            }
        }


class METARTestGenerator:
    """Generator for diverse METAR test cases.

    Uses live data from AviationWeather.gov and enriches with
    airport metadata from OpenAIP and GIFTs.
    """

    # World regions for diverse sampling
    WORLD_REGIONS = {
        "north_america": (-130, 25, -60, 60),
        "europe": (-10, 35, 40, 70),
        "asia_pacific": (100, -10, 150, 50),
        "south_america": (-80, -55, -35, 15),
        "africa": (-20, -35, 55, 35),
        "middle_east": (30, 10, 60, 45),
        "australia": (110, -45, 155, -10)
    }

    def __init__(
        self,
        aviation_weather_client: Optional[AviationWeatherClient] = None,
        openaip_client: Optional[OpenAIPClient] = None,
        wmo_client: Optional[WMOCodelistsClient] = None,
        reconciliation_service: Optional[AirportReconciliationService] = None,
        cache_dir: Optional[Path] = None
    ):
        """Initialize test generator.

        Args:
            aviation_weather_client: Client for fetching METARs
            openaip_client: Client for airport metadata
            wmo_client: Client for codelist validation
            reconciliation_service: Service for reconciling airport data
            cache_dir: Directory for caching generated tests
        """
        self.aviation_weather = aviation_weather_client or AviationWeatherClient()

        # Get data paths relative to backend directory
        backend_dir = Path(__file__).parent.parent.parent
        data_dir = backend_dir.parent / "data"

        self.openaip = openaip_client or OpenAIPClient(
            data_path=data_dir / "open-aip"
        )

        # Find IWXXM codelists directory
        schemas_dir = backend_dir.parent / "schemas" / "iwxxm" / "IWXXM"
        codelists_dirs = list(schemas_dir.glob("*/rule"))
        codelists_dir = sorted(codelists_dirs)[-1] if codelists_dirs else None

        self.wmo = wmo_client or (
            WMOCodelistsClient(codelists_dir) if codelists_dir else None
        )

        self.reconciliation = reconciliation_service or AirportReconciliationService(
            openaip_client=self.openaip,
            aviation_weather_client=self.aviation_weather,
            gifts_data_path=data_dir / "af-airports.csv"
        )

        self.cache_dir = cache_dir or Path("test-data/generated-tests")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.coverage = CoverageReport()

    def _parse_metar_features(self, raw_metar: str) -> Dict[str, Any]:
        """Extract meteorological features from raw METAR.

        Simple regex-based extraction for coverage tracking.
        """
        features = {
            "weather_phenomena": [],
            "cloud_types": [],
            "cloud_amounts": [],
            "visibility": None,
            "temperature": None
        }

        # Extract weather phenomena (simplified)
        weather_codes = [
            'RA', 'SN', 'DZ', 'FG', 'BR', 'HZ', 'TS', 'GR', 'GS',
            'TSRA', 'TSGR', 'FZRA', 'FZDZ', 'SHRA', 'SHSN', 'NSW'
        ]
        for code in weather_codes:
            if code in raw_metar:
                features["weather_phenomena"].append(code)

        # Extract cloud amounts
        cloud_amounts = ['FEW', 'SCT', 'BKN', 'OVC', 'CLR', 'SKC']
        for amount in cloud_amounts:
            if amount in raw_metar:
                features["cloud_amounts"].append(amount)

        # Extract cloud types
        cloud_types = ['CB', 'TCU']
        for ctype in cloud_types:
            if ctype in raw_metar:
                features["cloud_types"].append(ctype)

        # Extract visibility (simplified - just check for presence)
        if any(vis in raw_metar for vis in ['SM', 'KM', 'M ']):
            features["visibility"] = "present"

        # Extract temperature (check for temp/dewpoint pattern)
        import re
        temp_pattern = r'\s(\d{2}|M\d{2})/(\d{2}|M\d{2})\s'
        if re.search(temp_pattern, raw_metar):
            features["temperature"] = "present"

        return features

    def _enrich_with_metadata(
        self,
        metar_data: Dict[str, Any]
    ) -> METARTestCase:
        """Enrich METAR data with airport metadata."""
        # Handle different field names from various APIs
        station_id = (metar_data.get('station_id') or
                     metar_data.get('icaoId') or
                     metar_data.get('icao') or '')

        raw_metar = metar_data.get('raw_text') or metar_data.get('rawOb') or ''

        # Parse meteorological features
        features = self._parse_metar_features(raw_metar)

        # Get airport metadata
        airport = self.reconciliation.get_airport(station_id)

        # Determine region from coordinates
        region = self._determine_region(
            metar_data.get('latitude') or metar_data.get('lat'),
            metar_data.get('longitude') or metar_data.get('lon')
        )

        return METARTestCase(
            station_id=station_id,
            raw_metar=raw_metar,
            latitude=airport.latitude if airport else (metar_data.get('latitude') or metar_data.get('lat')),
            longitude=airport.longitude if airport else (metar_data.get('longitude') or metar_data.get('lon')),
            country=airport.country if airport else metar_data.get('country'),
            elevation=airport.elevation if airport else (metar_data.get('elevation_m') or metar_data.get('elev')),
            weather_phenomena=features["weather_phenomena"],
            cloud_types=features["cloud_types"],
            cloud_amounts=features["cloud_amounts"],
            visibility=features["visibility"],
            temperature=features["temperature"],
            region=region,
            timestamp=datetime.now(),
            source="aviation_weather"
        )

    def _determine_region(self, lat: Optional[float], lon: Optional[float]) -> Optional[str]:
        """Determine world region from coordinates."""
        if lat is None or lon is None:
            return None

        for region_name, (min_lon, min_lat, max_lon, max_lat) in self.WORLD_REGIONS.items():
            if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                return region_name

        return "other"

    def diverse_sample(
        self,
        count: int = 200,
        hours: int = 3,
        use_cache: bool = True
    ) -> List[METARTestCase]:
        """Generate diverse sample of METARs from all world regions.

        Args:
            count: Target number of test cases
            hours: Hours back to search for METARs
            use_cache: Use cached results if available

        Returns:
            List of METARTestCase objects
        """
        cache_file = self.cache_dir / f"diverse_sample_{count}_{hours}h.json"

        # Check cache
        if use_cache and cache_file.exists():
            logger.info(f"Loading diverse sample from cache: {cache_file}")
            return self._load_from_cache(cache_file)

        logger.info(f"Generating diverse sample of {count} METARs...")

        # Fetch from all regions
        regions = list(self.WORLD_REGIONS.values())
        metars_per_region = count // len(regions) + 1

        all_test_cases = []

        for region_name, bbox in self.WORLD_REGIONS.items():
            logger.info(f"  Fetching from {region_name}...")
            try:
                metars = self.aviation_weather.fetch_metars_by_bbox_sync(
                    bbox=bbox,
                    hours=hours,
                    format_type='json'
                )

                # Sample if we have too many
                if len(metars) > metars_per_region:
                    metars = random.sample(metars, metars_per_region)

                # Enrich with metadata
                for metar_data in metars:
                    test_case = self._enrich_with_metadata(metar_data)
                    all_test_cases.append(test_case)
                    self.coverage.add_test_case(test_case)

                logger.info(f"    ✓ {len(metars)} METARs from {region_name}")

            except Exception as e:
                logger.warning(f"    ✗ Failed to fetch from {region_name}: {e}")
                continue

        # Random sample if we have too many
        if len(all_test_cases) > count:
            all_test_cases = random.sample(all_test_cases, count)

        # Save to cache
        self._save_to_cache(all_test_cases, cache_file)

        logger.info(f"Generated {len(all_test_cases)} diverse test cases")
        return all_test_cases

    def regional_sample(
        self,
        region: str,
        count: int = 50,
        hours: int = 3,
        use_cache: bool = True
    ) -> List[METARTestCase]:
        """Generate sample from specific region.

        Args:
            region: Region name (from WORLD_REGIONS)
            count: Number of test cases
            hours: Hours back to search
            use_cache: Use cached results

        Returns:
            List of METARTestCase objects
        """
        if region not in self.WORLD_REGIONS:
            raise ValueError(f"Unknown region: {region}")

        cache_file = self.cache_dir / f"regional_{region}_{count}_{hours}h.json"

        if use_cache and cache_file.exists():
            return self._load_from_cache(cache_file)

        logger.info(f"Generating regional sample: {region} ({count} cases)")

        bbox = self.WORLD_REGIONS[region]
        metars = self.aviation_weather.fetch_metars_by_bbox_sync(
            bbox=bbox,
            hours=hours,
            format_type='json'
        )

        # Sample if needed
        if len(metars) > count:
            metars = random.sample(metars, count)

        # Enrich
        test_cases = []
        for metar_data in metars:
            test_case = self._enrich_with_metadata(metar_data)
            test_cases.append(test_case)
            self.coverage.add_test_case(test_case)

        self._save_to_cache(test_cases, cache_file)
        return test_cases

    def phenomenon_coverage(
        self,
        required_phenomena: Optional[List[str]] = None,
        hours: int = 6,
        use_cache: bool = True
    ) -> List[METARTestCase]:
        """Generate test cases ensuring coverage of specific weather phenomena.

        Args:
            required_phenomena: List of weather codes to find (default: common set)
            hours: Hours back to search
            use_cache: Use cached results

        Returns:
            List of METARTestCase objects with required phenomena
        """
        if required_phenomena is None:
            required_phenomena = ['RA', 'SN', 'TS', 'FG', 'BR', 'CB', 'TCU']

        cache_file = self.cache_dir / f"phenomena_coverage_{hours}h.json"

        if use_cache and cache_file.exists():
            return self._load_from_cache(cache_file)

        logger.info(f"Generating phenomenon coverage for: {required_phenomena}")

        # Fetch from all regions
        all_metars = []
        for region_name, bbox in self.WORLD_REGIONS.items():
            try:
                metars = self.aviation_weather.fetch_metars_by_bbox_sync(
                    bbox=bbox,
                    hours=hours,
                    format_type='json'
                )
                all_metars.extend(metars)
            except Exception:
                continue

        # Find METARs with each phenomenon
        test_cases = []
        found_phenomena = {}  # Track which phenomena we've found

        for phenomenon in required_phenomena:
            found_phenomena[phenomenon] = []

        # First pass - find all phenomena
        for metar_data in all_metars:
            raw_metar = metar_data.get('raw_text') or metar_data.get('rawOb', '')

            # Check which required phenomena are present
            for phenomenon in required_phenomena:
                if phenomenon in raw_metar and phenomenon not in found_phenomena.get(phenomenon, []):
                    test_case = self._enrich_with_metadata(metar_data)
                    test_cases.append(test_case)
                    self.coverage.add_test_case(test_case)
                    found_phenomena[phenomenon].append(phenomenon)
                    logger.info(f"  ✓ Found {phenomenon}")
                    if len(test_cases) >= len(required_phenomena):
                        break

            if len(test_cases) >= len(required_phenomena):
                break

        found_count = sum(1 for v in found_phenomena.values() if v)
        logger.info(f"Found {found_count}/{len(required_phenomena)} phenomena")

        self._save_to_cache(test_cases, cache_file)
        return test_cases

    def _save_to_cache(self, test_cases: List[METARTestCase], cache_file: Path) -> None:
        """Save test cases to cache file."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "count": len(test_cases),
            "test_cases": [
                {
                    "station_id": tc.station_id,
                    "raw_metar": tc.raw_metar,
                    "latitude": tc.latitude,
                    "longitude": tc.longitude,
                    "country": tc.country,
                    "elevation": tc.elevation,
                    "weather_phenomena": tc.weather_phenomena,
                    "cloud_types": tc.cloud_types,
                    "cloud_amounts": tc.cloud_amounts,
                    "visibility": tc.visibility,
                    "temperature": tc.temperature,
                    "region": tc.region,
                    "source": tc.source
                }
                for tc in test_cases
            ]
        }

        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(test_cases)} test cases to {cache_file}")

    def _load_from_cache(self, cache_file: Path) -> List[METARTestCase]:
        """Load test cases from cache file."""
        with open(cache_file, 'r') as f:
            data = json.load(f)

        test_cases = []
        for tc_data in data["test_cases"]:
            test_case = METARTestCase(
                station_id=tc_data["station_id"],
                raw_metar=tc_data["raw_metar"],
                latitude=tc_data.get("latitude"),
                longitude=tc_data.get("longitude"),
                country=tc_data.get("country"),
                elevation=tc_data.get("elevation"),
                weather_phenomena=tc_data.get("weather_phenomena", []),
                cloud_types=tc_data.get("cloud_types", []),
                cloud_amounts=tc_data.get("cloud_amounts", []),
                visibility=tc_data.get("visibility"),
                temperature=tc_data.get("temperature"),
                region=tc_data.get("region"),
                source=tc_data.get("source", "cache")
            )
            test_cases.append(test_case)
            self.coverage.add_test_case(test_case)

        logger.info(f"Loaded {len(test_cases)} test cases from cache")
        return test_cases

    def get_coverage_report(self) -> CoverageReport:
        """Get current coverage report."""
        return self.coverage

    def save_coverage_report(self, output_file: Optional[Path] = None) -> None:
        """Save coverage report to JSON file."""
        if output_file is None:
            output_file = self.cache_dir / "coverage_report.json"

        with open(output_file, 'w') as f:
            json.dump(self.coverage.to_dict(), f, indent=2)

        logger.info(f"Saved coverage report to {output_file}")
