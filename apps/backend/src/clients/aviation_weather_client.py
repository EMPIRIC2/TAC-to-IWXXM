"""Client for aviationweather.gov API."""

import asyncio
import hashlib
import json
import random
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Self, cast

import httpx


class AviationWeatherAPIError(Exception):
    """Aviation weather API error."""

    pass


class AviationWeatherClient:
    """Client for fetching METAR data from aviationweather.gov."""

    BASE_URL = "https://aviationweather.gov/api/data"
    BATCH_SIZE = 50  # Max stations per request to be respectful
    RATE_LIMIT_DELAY = 0.5  # Seconds between batches

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._client:
            await self._client.aclose()

    async def fetch_metar_batch(
        self,
        station_ids: list[str],
        hours: float = 1.5,
    ) -> dict[str, tuple[str | None, str | None]]:
        """Fetch METAR data for multiple stations.

        Args:
            station_ids: List of ICAO station identifiers
            hours: Hours back to search (default: 1.5)

        Returns:
            Dict mapping station_id -> (raw_tac, iwxxm_xml)
            Both values may be None if data unavailable
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        results: dict[str, tuple[str | None, str | None]] = {}

        # Process in batches to be respectful of the API
        for i in range(0, len(station_ids), self.BATCH_SIZE):
            batch = station_ids[i : i + self.BATCH_SIZE]

            # Fetch both raw TAC and IWXXM in parallel
            raw_result, iwxxm_result = await asyncio.gather(
                self._fetch_format(batch, "raw", hours),
                self._fetch_format(batch, "iwxxm", hours),
                return_exceptions=True,
            )

            raw_data: dict[str, Any] = raw_result if isinstance(raw_result, dict) else {}
            iwxxm_data: dict[str, Any] = iwxxm_result if isinstance(iwxxm_result, dict) else {}

            # Combine results
            for station_id in batch:
                raw_entry = raw_data.get(station_id)
                iwxxm_entry = iwxxm_data.get(station_id)
                results[station_id] = (raw_entry, iwxxm_entry)

            # Rate limiting between batches
            if i + self.BATCH_SIZE < len(station_ids):
                await asyncio.sleep(self.RATE_LIMIT_DELAY)

        return results

    async def _fetch_format(self, station_ids: list[str], format_type: str, hours: float) -> dict[str, str]:
        """Fetch data in a specific format.

        Args:
            station_ids: List of ICAO codes
            format_type: 'raw' or 'iwxxm'
            hours: Hours back

        Returns:
            Dict of station_id -> content
        """
        if not self._client:
            raise RuntimeError("Client not initialized")

        ids_param = ",".join(station_ids)

        try:
            response = await self._client.get(
                f"{self.BASE_URL}/metar",
                params={
                    "ids": ids_param,
                    "format": format_type,
                    "hours": hours,
                },
            )
            response.raise_for_status()

            # Parse the response - format depends on format_type
            return self._parse_response(response.text, format_type, station_ids)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # No data found - return empty dict
                return {}
            raise AviationWeatherAPIError(f"HTTP {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            raise AviationWeatherAPIError(f"Request failed: {e!s}") from e

    def _parse_response(self, content: str, format_type: str, requested_stations: list[str]) -> dict[str, str]:
        """Parse API response and extract per-station data.

        Args:
            content: Response content
            format_type: 'raw' or 'iwxxm'
            requested_stations: List of requested station IDs

        Returns:
            Dict mapping station_id -> content
        """
        results: dict[str, Any] = {}

        if format_type == "raw":
            # Raw format returns one METAR per line
            for line in content.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Extract station ID from METAR (4th token usually)
                parts = line.split()
                if len(parts) >= 2:
                    # Format is usually: METAR KJFK 101851Z ...
                    station_id = parts[1] if parts[0] in ["METAR", "SPECI"] else parts[0]
                    if station_id in requested_stations:
                        results[station_id] = line

        elif format_type == "iwxxm":
            # IWXXM format returns XML - may be wrapped or individual reports
            # For simplicity, if multiple stations, we try to split by XML declarations
            if "<?xml" in content:
                # Split by XML declarations for multiple reports
                xml_parts = content.split("<?xml")
                for part in xml_parts:
                    if not part.strip():
                        continue
                    xml_doc = "<?xml" + part if not part.startswith("<?xml") else part
                    # Try to extract station ID from XML
                    station_id = self._extract_station_from_xml(xml_doc)
                    if station_id and station_id in requested_stations:
                        results[station_id] = xml_doc.strip()
            else:
                # Single report or no data
                if content.strip():
                    station_id = self._extract_station_from_xml(content)
                    if station_id and station_id in requested_stations:
                        results[station_id] = content.strip()

        return results

    def _extract_station_from_xml(self, xml_content: str) -> str | None:
        """Extract ICAO station ID from IWXXM XML.

        Look for aerodrome designator in the XML.
        """
        import re

        # Look for designator="KJFK" or similar patterns
        match = re.search(r'designator="([A-Z]{4})"', xml_content)
        if match:
            return match.group(1)

        # Fallback: look for <icaoId> tags
        match = re.search(r"<.*?icaoId.*?>([A-Z]{4})</.*?icaoId.*?>", xml_content, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    async def fetch_metars_by_bbox(
        self, bbox: tuple[float, float, float, float], hours: int = 2, format_type: str = "json"
    ) -> list[dict[str, Any]]:
        """Fetch all METARs in a bounding box.

        Args:
            bbox: (min_lon, min_lat, max_lon, max_lat)
            hours: Hours back to search
            format_type: 'json' or 'raw'

        Returns:
            List of METAR records
        """
        if not self._client:
            raise RuntimeError("Client not initialized")

        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

        try:
            response = await self._client.get(
                f"{self.BASE_URL}/metar",
                params={
                    "bbox": bbox_str,
                    "format": format_type,
                    "hours": hours,
                },
            )
            response.raise_for_status()

            if format_type == "json":
                # Handle empty responses
                if not response.text or response.text.strip() in ["", "[]", "{}"]:
                    return []
                try:
                    return response.json()
                except Exception as e:
                    print(f"Warning: Failed to parse JSON response for bbox {bbox_str}: {e!s}")
                    return []
            else:
                # Parse raw format
                metars: list[Any] = []
                metars.extend({"rawOb": line.strip()} for line in response.text.strip().split("\n") if line.strip())
                return metars

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise AviationWeatherAPIError(f"HTTP {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            raise AviationWeatherAPIError(f"Request failed: {e!s}") from e

    async def fetch_random_sample(
        self, count: int = 100, regions: list[tuple[float, float, float, float]] | None = None, hours: int = 2
    ) -> list[dict[str, Any]]:
        """Fetch random sample of METARs for testing.

        Args:
            count: Number of METARs to fetch
            regions: List of bounding boxes to sample from
            hours: Hours back to search

        Returns:
            List of METAR records
        """
        if regions is None:
            # Default regions covering diverse areas
            regions = [
                (-130, 25, -65, 50),  # North America
                (-10, 35, 30, 70),  # Europe
                (100, -45, 180, 10),  # Asia-Pacific
                (-80, -55, -30, 15),  # South America
                (15, -35, 52, 38),  # Africa
            ]

        all_metars: list[Any] = []

        # Fetch from each region
        for bbox in regions:
            try:
                metars = await self.fetch_metars_by_bbox(bbox, hours=hours, format_type="json")
                all_metars.extend(metars)
            except Exception:
                # Continue even if one region fails
                continue

        # Random sample if we have more than requested
        if len(all_metars) > count:
            return random.sample(all_metars, count)

        return all_metars

    # Synchronous wrapper methods for convenience
    def fetch_metars_by_bbox_sync(
        self, bbox: tuple[float, float, float, float], hours: int = 2, format_type: str = "json"
    ) -> list[dict[str, Any]]:
        """Synchronous wrapper for fetch_metars_by_bbox."""

        async def _fetch() -> list[dict[str, Any]]:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create a temporary client instance for this request
                temp_self = self.__class__(timeout=self.timeout)
                temp_self._client = client
                return await temp_self.fetch_metars_by_bbox(bbox, hours, format_type)

        return asyncio.run(_fetch())

    def fetch_random_sample_sync(
        self, count: int = 100, regions: list[tuple[float, float, float, float]] | None = None, hours: int = 2
    ) -> list[dict[str, Any]]:
        """Synchronous wrapper for fetch_random_sample."""

        async def _fetch() -> list[dict[str, Any]]:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create a temporary client instance for this request
                temp_self = self.__class__(timeout=self.timeout)
                temp_self._client = client
                return await temp_self.fetch_random_sample(count, regions, hours)

        return asyncio.run(_fetch())


class CachedAviationWeatherClient(AviationWeatherClient):
    """Aviation Weather client with caching for test reproducibility."""

    def __init__(self, cache_dir: Path | None = None, ttl: int = 3600, timeout: float = 30.0) -> None:
        super().__init__(timeout=timeout)
        self.cache_dir = cache_dir or Path("test-data/aviation-weather-cache")
        self.ttl = ttl  # Time to live in seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, *args: object) -> str:
        """Generate cache key from arguments."""
        key_str = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get path to cache file."""
        return self.cache_dir / f"{key}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is still valid."""
        if not cache_path.exists():
            return False

        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - mtime
        return age.total_seconds() < self.ttl

    async def fetch_metars_by_bbox(
        self, bbox: tuple[float, float, float, float], hours: int = 2, format_type: str = "json"
    ) -> list[dict[str, Any]]:
        """Fetch METARs with caching."""
        cache_key = self._cache_key("bbox", bbox, hours, format_type)
        cache_path = self._get_cache_path(cache_key)

        # Check cache
        if self._is_cache_valid(cache_path):

            def _read_cache() -> list[dict[str, Any]]:
                with open(cache_path) as f:
                    return cast(list[dict[str, Any]], json.load(f))

            return await asyncio.to_thread(_read_cache)

        # Fetch fresh data
        data = await super().fetch_metars_by_bbox(bbox, hours, format_type)

        # Save to cache
        def _write_cache() -> None:
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)

        await asyncio.to_thread(_write_cache)

        return data

    async def fetch_random_sample(
        self, count: int = 100, regions: list[tuple[float, float, float, float]] | None = None, hours: int = 2
    ) -> list[dict[str, Any]]:
        """Fetch random sample with caching."""
        # For reproducibility, use a fixed seed for test sampling
        cache_key = self._cache_key("sample", count, hours)
        cache_path = self._get_cache_path(cache_key)

        # Check cache
        if self._is_cache_valid(cache_path):

            def _read_cache() -> list[dict[str, Any]]:
                with open(cache_path) as f:
                    return cast(list[dict[str, Any]], json.load(f))

            return await asyncio.to_thread(_read_cache)

        # Fetch fresh data
        data = await super().fetch_random_sample(count, regions, hours)

        # Save to cache
        def _write_cache() -> None:
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)

        await asyncio.to_thread(_write_cache)

        return data

    # Override sync wrappers to properly handle caching parameters
    def fetch_metars_by_bbox_sync(
        self, bbox: tuple[float, float, float, float], hours: int = 2, format_type: str = "json"
    ) -> list[dict[str, Any]]:
        """Synchronous wrapper for fetch_metars_by_bbox with caching."""

        async def _fetch() -> list[dict[str, Any]]:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create a temporary cached client instance for this request
                temp_self = CachedAviationWeatherClient(cache_dir=self.cache_dir, ttl=self.ttl, timeout=self.timeout)
                temp_self._client = client
                return await temp_self.fetch_metars_by_bbox(bbox, hours, format_type)

        return asyncio.run(_fetch())

    def fetch_random_sample_sync(
        self, count: int = 100, regions: list[tuple[float, float, float, float]] | None = None, hours: int = 2
    ) -> list[dict[str, Any]]:
        """Synchronous wrapper for fetch_random_sample with caching."""

        async def _fetch() -> list[dict[str, Any]]:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create a temporary cached client instance for this request
                temp_self = CachedAviationWeatherClient(cache_dir=self.cache_dir, ttl=self.ttl, timeout=self.timeout)
                temp_self._client = client
                return await temp_self.fetch_random_sample(count, regions, hours)

        return asyncio.run(_fetch())
