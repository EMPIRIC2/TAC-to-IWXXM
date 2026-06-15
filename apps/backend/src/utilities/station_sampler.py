"""Utility for sampling airport stations from the CSV database."""
import csv
import pathlib
import random
from typing import List, Optional


class StationSampler:
    """Sample airport stations from the af-airports.csv database."""

    def __init__(self, csv_path: Optional[pathlib.Path] = None):
        if csv_path is None:
            # Auto-detect CSV path
            csv_path = self._find_airports_csv()
        self.csv_path = csv_path
        self._airports_cache: Optional[List[dict]] = None

    @staticmethod
    def _find_airports_csv() -> pathlib.Path:
        """Find the airports CSV file."""
        candidates = [
            pathlib.Path("/app/data/af-airports.csv"),
            pathlib.Path("./data/af-airports.csv"),
        ]
        for parent in pathlib.Path(__file__).resolve().parents:
            candidates.append(parent / "data" / "af-airports.csv")

        for candidate in candidates:
            if candidate.exists():
                return candidate

        raise FileNotFoundError("Could not find af-airports.csv")

    def _load_airports(self) -> List[dict]:
        """Load and cache airport data."""
        if self._airports_cache is not None:
            return self._airports_cache

        airports = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Only include airports with valid ICAO codes
                icao = row.get('icao_code', '').strip()
                if icao and len(icao) == 4 and icao.isalpha():
                    airports.append({
                        'icao': icao,
                        'name': row.get('name', ''),
                        'country': row.get('country_name', ''),
                        'type': row.get('type', ''),
                        'scheduled_service': row.get('scheduled_service', '0'),
                    })

        self._airports_cache = airports
        return airports

    def sample_random_stations(
        self,
        count: int,
        large_airports_only: bool = False,
        scheduled_service_only: bool = True,
        seed: Optional[int] = None
    ) -> List[str]:
        """Sample random airport stations.

        Args:
            count: Number of stations to sample
            large_airports_only: Only include large_airport type
            scheduled_service_only: Only include airports with scheduled service
            seed: Random seed for reproducibility

        Returns:
            List of ICAO codes
        """
        airports = self._load_airports()

        # Filter
        filtered = airports
        if large_airports_only:
            filtered = [a for a in filtered if a['type'] == 'large_airport']
        if scheduled_service_only:
            filtered = [a for a in filtered if a['scheduled_service'] == '1']

        # Sample
        if seed is not None:
            random.seed(seed)

        sample_size = min(count, len(filtered))
        sampled = random.sample(filtered, sample_size)

        return [a['icao'] for a in sampled]

    def get_all_major_airports(
        self,
        large_only: bool = True,
        scheduled_service_only: bool = True
    ) -> List[str]:
        """Get all major airport ICAO codes.

        Args:
            large_only: Only large airports
            scheduled_service_only: Only scheduled service

        Returns:
            List of all matching ICAO codes
        """
        airports = self._load_airports()

        filtered = airports
        if large_only:
            filtered = [a for a in filtered if a['type'] == 'large_airport']
        if scheduled_service_only:
            filtered = [a for a in filtered if a['scheduled_service'] == '1']

        return [a['icao'] for a in filtered]

    def get_station_info(self, icao: str) -> Optional[dict]:
        """Get information about a specific station.

        Args:
            icao: ICAO code

        Returns:
            Airport info dict or None
        """
        airports = self._load_airports()
        for airport in airports:
            if airport['icao'] == icao:
                return airport
        return None
