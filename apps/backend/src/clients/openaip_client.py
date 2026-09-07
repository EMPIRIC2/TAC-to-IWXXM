"""Client for OpenAIP airport database."""

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import httpx


@dataclass
class Airport:
    """Standardized airport data model."""

    icao_code: str
    name: str
    country: str
    elevation: float | None = None  # meters
    geometry: dict[str, Any] | None = None  # GeoJSON Point
    iata_code: str | None = None
    runways: list[dict[str, Any]] = field(default_factory=list)
    frequencies: list[dict[str, Any]] = field(default_factory=list)
    source: str = "unknown"

    @property
    def lat_lon(self) -> tuple[float, float] | None:
        """Extract coordinates from GeoJSON geometry."""
        if not self.geometry:
            return None

        if self.geometry.get("type") == "Point":
            coords = self.geometry.get("coordinates", [])
            if len(coords) >= 2:
                # GeoJSON is [lon, lat]
                return (coords[1], coords[0])

        return None

    @property
    def latitude(self) -> float | None:
        """Get latitude."""
        coords = self.lat_lon
        return coords[0] if coords else None

    @property
    def longitude(self) -> float | None:
        """Get longitude."""
        coords = self.lat_lon
        return coords[1] if coords else None


class OpenAIPClient:
    """Client for OpenAIP airport database.

    Note: This client works with locally cached OpenAIP data.
    For live API access, you need an OpenAIP API key.
    """

    def __init__(self, data_path: Path | None = None, api_key: str | None = None) -> None:
        """Initialize OpenAIP client.

        Args:
            data_path: Path to local OpenAIP data cache
            api_key: OpenAIP API key for live queries
        """
        self.data_path = data_path or Path("data/open-aip")
        self.api_key = api_key
        self._cache: dict[str, Airport] = {}
        self._loaded = False

    def _load_local_data(self) -> None:
        """Load airport data from local cache."""
        if self._loaded:
            return

        # Look for GeoJSON files in data directory
        airport_files = list(self.data_path.glob("*_apt.geojson"))

        for file_path in airport_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    raw = json.load(f)
                if not isinstance(raw, dict):
                    continue
                data = cast(dict[str, Any], raw)

                # Parse GeoJSON FeatureCollection
                if data.get("type") == "FeatureCollection":
                    for feature in cast(list[dict[str, Any]], data.get("features", [])):
                        airport = self._parse_feature(feature)
                        if airport and airport.icao_code:
                            self._cache[airport.icao_code] = airport
            except Exception:
                # Skip files that can't be parsed
                continue

        self._loaded = True

    def _parse_feature(self, feature: dict[str, Any]) -> Airport | None:
        """Parse GeoJSON feature into Airport object."""
        properties = feature.get("properties", {})
        geometry = feature.get("geometry")

        # Extract ICAO code
        icao_code = properties.get("icaoCode") or properties.get("icao")
        if not icao_code:
            return None

        # Extract elevation (may be in different units)
        elevation = properties.get("elevation")
        if elevation:
            # Convert to meters if needed
            elevation_unit = properties.get("elevationUnit", "m")
            elevation = float(elevation) * 0.3048 if elevation_unit.lower() in ["ft", "feet"] else float(elevation)

        return Airport(
            icao_code=icao_code.upper(),
            name=properties.get("name", ""),
            country=properties.get("country", ""),
            elevation=elevation,
            geometry=geometry,
            iata_code=properties.get("iata"),
            source="openaip",
        )

    def get_airport_by_icao(self, icao: str) -> Airport | None:
        """Fetch airport metadata by ICAO code.

        Args:
            icao: ICAO station identifier

        Returns:
            Airport object or None if not found
        """
        self._load_local_data()
        return self._cache.get(icao.upper())

    def search_airports(
        self, country: str | None = None, bbox: tuple[float, float, float, float] | None = None, limit: int = 1000
    ) -> list[Airport]:
        """Search airports with filters.

        Args:
            country: ISO country code
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            limit: Maximum number of results

        Returns:
            List of matching airports
        """
        self._load_local_data()

        results: list[Any] = []
        for airport in self._cache.values():
            # Apply filters
            if country and airport.country.upper() != country.upper():
                continue

            if bbox and airport.lat_lon:
                lat, lon = airport.lat_lon
                min_lon, min_lat, max_lon, max_lat = bbox
                if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                    continue

            results.append(airport)

            if len(results) >= limit:
                break

        return results

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about loaded airport data.

        Returns:
            Dictionary with statistics
        """
        self._load_local_data()

        countries: set[str] = set()
        with_elevation = 0
        with_coordinates = 0

        for airport in self._cache.values():
            if airport.country:
                countries.add(airport.country)
            if airport.elevation is not None:
                with_elevation += 1
            if airport.lat_lon is not None:
                with_coordinates += 1

        return {
            "total_airports": len(self._cache),
            "countries": len(countries),
            "with_elevation": with_elevation,
            "with_coordinates": with_coordinates,
            "data_source": "local_cache",
        }


async def download_openaip_data(
    output_dir: Path, countries: list[str] | None = None, api_key: str | None = None
) -> None:
    """Download OpenAIP airport data for specified countries.

    Args:
        output_dir: Directory to save downloaded data
        countries: List of ISO country codes (default: major aviation countries)
        api_key: OpenAIP API key

    Note:
        This function requires an OpenAIP API key.
        Free tier available at https://www.openaip.net/
    """
    if not api_key:
        raise ValueError("OpenAIP API key required for downloads")

    if countries is None:
        # Default to major aviation countries
        countries = ["US", "CA", "GB", "DE", "FR", "AU", "JP"]

    await asyncio.to_thread(output_dir.mkdir, parents=True, exist_ok=True)

    base_url = "https://api.core.openaip.net/api/airports"

    async with httpx.AsyncClient(timeout=60.0) as client:
        for country in countries:
            try:
                response = await client.get(
                    base_url, params={"country": country}, headers={"x-openaip-api-key": api_key}
                )
                response.raise_for_status()

                # Save to file
                output_file = output_dir / f"{country}_apt.geojson"
                payload = response.json()

                def _write(out: Path = output_file, data: object = payload) -> None:
                    with open(out, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)

                await asyncio.to_thread(_write)

                print(f"Downloaded {country}: {output_file}")

                # Rate limiting
                await asyncio.sleep(1.0)

            except Exception as e:
                print(f"Failed to download {country}: {e}")
                continue
