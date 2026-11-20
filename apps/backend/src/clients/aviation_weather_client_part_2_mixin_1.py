"""Mixin extracted from ``aviation_weather_client_part_2.py``::AviationWeatherClient."""

import asyncio
from typing import Any

import httpx


class _AviationWeatherClientMethodsMixin:
    timeout: float
    _client: object | None
    """Methods mixin for ``AviationWeatherClient``."""

    def fetch_metars_by_bbox_sync(
        self, bbox: tuple[float, float, float, float], hours: int = 2, format_type: str = "json"
    ) -> list[dict[str, Any]]:
        """
        Synchronous wrapper for fetch_metars_by_bbox.


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
                # Create a temporary client instance for this request
                temp_self = self.__class__(timeout=self.timeout)
                temp_self._client = client
                return await temp_self.fetch_metars_by_bbox(bbox, hours, format_type)

        return asyncio.run(_fetch())

    def fetch_random_sample_sync(
        self, count: int = 100, regions: list[tuple[float, float, float, float]] | None = None, hours: int = 2
    ) -> list[dict[str, Any]]:
        """
        Synchronous wrapper for fetch_random_sample.


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
                # Create a temporary client instance for this request
                temp_self = self.__class__(timeout=self.timeout)
                temp_self._client = client
                return await temp_self.fetch_random_sample(count, regions, hours)

        return asyncio.run(_fetch())
