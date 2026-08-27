"""
Service for managing OpenAIP airport data caching and access.

Provides hybrid access: primarily uses cached local data for performance,
with optional live API fallback for missing airports or cache refresh.
"""

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

logger = logging.getLogger(__name__)


class OpenAIPService:
    """Service for accessing OpenAIP airport data with intelligent caching."""

    def __init__(self, cache_file: Path | None = None, api_key: str | None = None) -> None:
        """
        Initialize OpenAIP service.

        Args:
            cache_file: Path to openaip_cache.json file
            api_key: Optional OpenAIP API key for live fallback
        """
        if cache_file is None:
            cache_file = Path(__file__).parent.parent / "data" / "openaip_cache.json"

        self.cache_file = cache_file
        self.api_key = api_key
        self._cache: dict[str, dict[str, Any]] | None = None
        self._cache_timestamp: datetime | None = None
        self._live_cache: dict[str, dict[str, Any]] = {}  # In-memory cache for live API calls
        self._load_cache()

    def _load_cache(self) -> bool:
        """Load cache from file."""
        if not self.cache_file.exists():
            logger.warning(f"Cache file not found: {self.cache_file}")
            return False

        try:
            with open(self.cache_file) as f:
                raw = json.load(f)
            if not isinstance(raw, dict):
                return False
            data = cast(dict[str, Any], raw)

            # Extract metadata and airports
            metadata = cast(dict[str, Any], data.get("_metadata", {}))
            airports_raw = data.get("airports", data)
            self._cache = cast(dict[str, dict[str, Any]], airports_raw if isinstance(airports_raw, dict) else {})
            self._cache_timestamp = datetime.fromisoformat(
                metadata.get("fetched_at", datetime.now(UTC).replace(tzinfo=None).isoformat())
            )

            logger.info(
                f"Loaded OpenAIP cache with {len(self._cache or {})} airports (last updated: {self._cache_timestamp})"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to load OpenAIP cache: {e}")
            self._cache = {}
            return False

    def get_airport(self, icao: str) -> dict[str, Any] | None:
        """
        Get airport data by ICAO code.

        Searches in order:
        1. Local cache (file-based)
        2. In-memory cache (from live API calls)
        3. Live API (if api_key available)

        Args:
            icao: 4-letter ICAO airport code

        Returns:
            Airport data dict or None if not found
        """
        icao = icao.upper().strip()

        # Check file cache
        if self._cache and icao in self._cache:
            return self._cache[icao]

        # Check live cache (5-minute expiry)
        if icao in self._live_cache:
            cached_entry = self._live_cache[icao]
            if cached_entry.get("_cached_at"):
                cached_at = datetime.fromisoformat(cached_entry["_cached_at"])
                if datetime.now(UTC).replace(tzinfo=None) - cached_at < timedelta(minutes=5):
                    return cached_entry.get("data")

        # Try live API if available
        if self.api_key and (airport := self._fetch_from_api(icao)):
            self._live_cache[icao] = {
                "data": airport,
                "_cached_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            }
            return airport

        return None

    def _fetch_from_api(self, icao: str) -> dict[str, Any] | None:
        """
        Fetch a single airport from OpenAIP API (fallback).

        Args:
            icao: 4-letter ICAO airport code

        Returns:
            Airport data or None
        """
        try:
            import requests
        except ImportError:
            logger.warning("requests library not available for live API access")
            return None

        try:
            url = "https://api.openaip.net/api/airports"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {"icaoCode": icao}

            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = cast(dict[str, Any], response.json())
                if items := data.get("items"):
                    return items[0]
        except Exception as e:
            logger.debug(f"Live API fetch failed for {icao}: {e}")

        return None

    def validate_airport(self, icao: str) -> bool:
        """
        Check if airport exists in OpenAIP data.

        Args:
            icao: 4-letter ICAO code

        Returns:
            True if airport found, False otherwise
        """
        return self.get_airport(icao) is not None

    def get_all_airports(self) -> dict[str, dict[str, Any]]:
        """
        Get all cached airports (for bulk operations).

        Returns:
            Dictionary of all cached airports keyed by ICAO
        """
        return self._cache or {}

    def cache_freshness(self) -> timedelta | None:
        """
        Get how old the cache is.

        Returns:
            Timedelta of cache age, or None if not loaded
        """
        if self._cache_timestamp:
            return datetime.now(UTC).replace(tzinfo=None) - self._cache_timestamp
        return None

    def is_cache_stale(self, max_age_days: int = 7) -> bool:
        """
        Check if cache is older than max_age_days.

        Args:
            max_age_days: Maximum acceptable cache age in days

        Returns:
            True if cache is stale
        """
        if freshness := self.cache_freshness():
            return freshness > timedelta(days=max_age_days)
        return True

    def suggest_refresh(self) -> str:
        """Get refresh suggestion message."""
        if self.is_cache_stale():
            freshness = self.cache_freshness()
            age_days = int(freshness.days) if freshness is not None else 0
            return (
                f"OpenAIP cache is {age_days} days old. "
                f"Refresh with: python3 scripts/fetch_openaip_airports.py --refresh"
            )
        return ""
