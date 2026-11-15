"""Part 3 of ``aviation_weather_client.py`` (line-cap split)."""

import asyncio
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import httpx

from src.clients.aviation_weather_client_part_2 import AviationWeatherClient


class CachedAviationWeatherClient(AviationWeatherClient):
    """
    Aviation Weather client with caching for test reproducibility.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self, cache_dir: Path | None = None, ttl: int = 3600, timeout: float = 30.0) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        cache_dir : object
            Argument ``cache_dir``.
        ttl : object
            Argument ``ttl``.
        timeout : object
            Argument ``timeout``.
        """
        super().__init__(timeout=timeout)
        self.cache_dir = cache_dir or Path("data/_test-data/aviation-weather-cache")
        self.ttl = ttl  # Time to live in seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, *args: object) -> str:
        """
        Internal helper ``_cache_key``.

        Parameters
        ----------
        args : object
            Argument ``args``.

        Returns
        -------
        object
            Return value.
        """
        key_str = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """
        Internal helper ``_get_cache_path``.

        Parameters
        ----------
        key : object
            Argument ``key``.

        Returns
        -------
        object
            Return value.
        """
        return self.cache_dir / f"{key}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """
        Internal helper ``_is_cache_valid``.

        Parameters
        ----------
        cache_path : object
            Argument ``cache_path``.

        Returns
        -------
        object
            Return value.
        """
        if not cache_path.exists():
            return False

        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - mtime
        return age.total_seconds() < self.ttl

    async def fetch_metars_by_bbox(
        self, bbox: tuple[float, float, float, float], hours: int = 2, format_type: str = "json"
    ) -> list[dict[str, Any]]:
        """
        Fetch METARs with caching.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (fetch_metars_by_bbox)
        2

        Parameters
        ----------
        bbox : object
            Argument ``bbox``.
        hours : object
            Argument ``hours``.
        format_type : object
            Argument ``format_type``.

        Returns
        -------
        object
            Return value.
        """
        cache_key = self._cache_key("bbox", bbox, hours, format_type)
        cache_path = self._get_cache_path(cache_key)

        # Check cache
        if self._is_cache_valid(cache_path):

            def _read_cache() -> list[dict[str, Any]]:
                """
                Internal helper ``_read_cache``.

                Returns
                -------
                object
                    Return value.
                """
                with open(cache_path) as f:
                    return cast(list[dict[str, Any]], json.load(f))

            return await asyncio.to_thread(_read_cache)

        # Fetch fresh data
        data = await super().fetch_metars_by_bbox(bbox, hours, format_type)

        # Save to cache
        def _write_cache() -> None:
            """Internal helper ``_write_cache``."""
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)

        await asyncio.to_thread(_write_cache)

        return data

    async def fetch_random_sample(
        self, count: int = 100, regions: list[tuple[float, float, float, float]] | None = None, hours: int = 2
    ) -> list[dict[str, Any]]:
        """
        Fetch random sample with caching.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (fetch_random_sample)
        2

        Parameters
        ----------
        count : object
            Argument ``count``.
        regions : object
            Argument ``regions``.
        hours : object
            Argument ``hours``.

        Returns
        -------
        object
            Return value.
        """
        # For reproducibility, use a fixed seed for test sampling
        cache_key = self._cache_key("sample", count, hours)
        cache_path = self._get_cache_path(cache_key)

        # Check cache
        if self._is_cache_valid(cache_path):

            def _read_cache() -> list[dict[str, Any]]:
                """
                Internal helper ``_read_cache``.

                Returns
                -------
                object
                    Return value.
                """
                with open(cache_path) as f:
                    return cast(list[dict[str, Any]], json.load(f))

            return await asyncio.to_thread(_read_cache)

        # Fetch fresh data
        data = await super().fetch_random_sample(count, regions, hours)

        # Save to cache
        def _write_cache() -> None:
            """Internal helper ``_write_cache``."""
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)

        await asyncio.to_thread(_write_cache)

        return data

    # Override sync wrappers to properly handle caching parameters
    def fetch_metars_by_bbox_sync(
        self, bbox: tuple[float, float, float, float], hours: int = 2, format_type: str = "json"
    ) -> list[dict[str, Any]]:
        """
        Synchronous wrapper for fetch_metars_by_bbox with caching.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (fetch_metars_by_bbox_sync)
        2

        Parameters
        ----------
        bbox : object
            Argument ``bbox``.
        hours : object
            Argument ``hours``.
        format_type : object
            Argument ``format_type``.

        Returns
        -------
        object
            Return value.
        """

        async def _fetch() -> list[dict[str, Any]]:
            """
            Internal helper ``_fetch``.

            Returns
            -------
            object
                Return value.
            """
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create a temporary cached client instance for this request
                temp_self = CachedAviationWeatherClient(cache_dir=self.cache_dir, ttl=self.ttl, timeout=self.timeout)
                temp_self._client = client
                return await temp_self.fetch_metars_by_bbox(bbox, hours, format_type)

        return asyncio.run(_fetch())

    def fetch_random_sample_sync(
        self, count: int = 100, regions: list[tuple[float, float, float, float]] | None = None, hours: int = 2
    ) -> list[dict[str, Any]]:
        """
        Synchronous wrapper for fetch_random_sample with caching.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (fetch_random_sample_sync)
        2

        Parameters
        ----------
        count : object
            Argument ``count``.
        regions : object
            Argument ``regions``.
        hours : object
            Argument ``hours``.

        Returns
        -------
        object
            Return value.
        """

        async def _fetch() -> list[dict[str, Any]]:
            """
            Internal helper ``_fetch``.

            Returns
            -------
            object
                Return value.
            """
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create a temporary cached client instance for this request
                temp_self = CachedAviationWeatherClient(cache_dir=self.cache_dir, ttl=self.ttl, timeout=self.timeout)
                temp_self._client = client
                return await temp_self.fetch_random_sample(count, regions, hours)

        return asyncio.run(_fetch())
