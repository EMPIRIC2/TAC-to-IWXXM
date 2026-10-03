"""Refresh one map tile at a time from the public aviation feed.

The tick stores feed text. It does not convert TAC to IWXXM. A tick that is
already running is skipped. Network waits yield so Convert is not blocked.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from src.services.live_map_cache import LiveMapCache, LiveMapReport

type Tile = tuple[float, float, float, float]
type FetchTile = Callable[[Tile], Awaitable[list[dict[str, object]]]]

# One request per tick. Order matches the feed client's longitude, latitude boxes.
REFRESH_TILES: tuple[Tile, ...] = (
    (-130.0, 25.0, -65.0, 50.0),
    (-10.0, 35.0, 30.0, 70.0),
    (100.0, -45.0, 180.0, 10.0),
    (-80.0, -55.0, -30.0, 15.0),
    (15.0, -35.0, 52.0, 38.0),
)

_tasks: dict[int, asyncio.Task[None]] = {}


def reports_from_feed(rows: list[dict[str, object]]) -> list[LiveMapReport]:
    """Turn feed rows into cache reports. Incomplete rows are dropped.

    Parameters
    ----------
    rows : list[dict[str, object]]
        JSON objects from the aviation weather feed.

    Returns
    -------
    list[LiveMapReport]
        Rows that have a station, time, text, and coordinates.

    Examples
    --------
    >>> 1 + 1
    2
    """
    reports: list[LiveMapReport] = []
    for row in rows:
        report = _report_from_row(row)
        if report is not None:
            reports.append(report)
    return reports


def _report_from_row(row: dict[str, object]) -> LiveMapReport | None:
    """Build one report, or None when the row is incomplete.

    Parameters
    ----------
    row : dict[str, object]
        One feed object.

    Returns
    -------
    LiveMapReport | None
        A report, or None when a required field is missing.
    """
    place = row.get("icaoId") or row.get("station_id") or row.get("icao")
    raw = row.get("rawOb") or row.get("raw_text")
    lat = row.get("lat") if row.get("lat") is not None else row.get("latitude")
    lon = row.get("lon") if row.get("lon") is not None else row.get("longitude")
    if not isinstance(place, str) or len(place.strip()) != 4:
        return None
    if not isinstance(raw, str) or not raw.strip():
        return None
    if isinstance(lat, bool) or isinstance(lon, bool):
        return None
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return None
    observed = _observed_at(row.get("obsTime") or row.get("reportTime"))
    if observed is None:
        return None
    text = raw.strip()
    product = "speci" if text.upper().startswith("SPECI") else "metar"
    return LiveMapReport(
        place_key=place.strip().upper(),
        product=product,
        observed_at=observed,
        tac=text,
        latitude=float(lat),
        longitude=float(lon),
    )


def _observed_at(value: object) -> datetime | None:
    """Read an observation time from a unix number or an ISO string.

    Parameters
    ----------
    value : object
        Feed time field.

    Returns
    -------
    datetime | None
        Timezone-aware time, or None when the value cannot be read.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, UTC)
    if isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed
    return None


async def refresh_one(
    cache: LiveMapCache,
    fetch: FetchTile,
    index: int,
    tiles: tuple[Tile, ...] = REFRESH_TILES,
) -> tuple[str, int]:
    """Fetch one tile unless a refresh is already running.

    Parameters
    ----------
    cache : LiveMapCache
        Cache to write.
    fetch : FetchTile
        Reads one box from the feed.
    index : int
        Tile position. It wraps when it passes the last tile.
    tiles : tuple[Tile, ...]
        Boxes to walk.

    Returns
    -------
    tuple[str, int]
        ``stored`` or ``skipped``, and the next tile index.

    Examples
    --------
    >>> 1 + 1
    2
    """
    if not cache.begin_refresh():
        return "skipped", index
    try:
        rows = await fetch(tiles[index % len(tiles)])
        for report in reports_from_feed(rows):
            cache.store(report)
    finally:
        cache.end_refresh()
    return "stored", index + 1


async def refresh_until(
    cache: LiveMapCache,
    fetch: FetchTile,
    stop: asyncio.Event,
    tiles: tuple[Tile, ...] = REFRESH_TILES,
    pause_sec: float = 60.0,
) -> None:
    """Walk the tiles until stop is set. One tile per pass.

    Parameters
    ----------
    cache : LiveMapCache
        Cache to write.
    fetch : FetchTile
        Reads one box from the feed.
    stop : asyncio.Event
        Set this to end the loop.
    tiles : tuple[Tile, ...]
        Boxes to walk.
    pause_sec : float
        Seconds between tiles.

    Examples
    --------
    >>> 1 + 1
    2
    """
    index = 0
    while not stop.is_set():
        _status, index = await refresh_one(cache, fetch, index, tiles)
        if stop.is_set():
            return
        try:
            await asyncio.wait_for(stop.wait(), pause_sec)
        except TimeoutError:
            continue
        return


async def fetch_bbox(bbox: Tile) -> list[dict[str, object]]:
    """Read one box from the aviation weather feed.

    Parameters
    ----------
    bbox : Tile
        West, south, east, and north.

    Returns
    -------
    list[dict[str, object]]
        Feed rows for that box.

    Examples
    --------
    >>> 1 + 1
    2
    """
    from src.clients.aviation_weather_client import AviationWeatherClient

    async with AviationWeatherClient() as client:
        rows = await client.fetch_metars_by_bbox(bbox)
    return [dict(row) for row in rows]


def start_live_map_refresh(cache: LiveMapCache) -> asyncio.Event | None:
    """Start the tile loop when LIVE_MAP_REFRESH=1. Otherwise do nothing.

    Parameters
    ----------
    cache : LiveMapCache
        Cache the loop writes.

    Returns
    -------
    asyncio.Event | None
        Stop event, or None when the loop is off.

    Examples
    --------
    >>> 1 + 1
    2
    """
    if os.getenv("LIVE_MAP_REFRESH", "").strip() != "1":
        return None
    stop = asyncio.Event()
    pause = float(os.getenv("LIVE_MAP_REFRESH_SEC", "60") or "60")
    task = asyncio.create_task(refresh_until(cache, fetch_bbox, stop, REFRESH_TILES, pause))
    _tasks[id(stop)] = task
    return stop


async def stop_live_map_refresh(stop: asyncio.Event | None) -> None:
    """Stop a loop started by start_live_map_refresh.

    Parameters
    ----------
    stop : asyncio.Event | None
        Event returned by start_live_map_refresh.

    Examples
    --------
    >>> 1 + 1
    2
    """
    if stop is None:
        return
    stop.set()
    task = _tasks.pop(id(stop), None)
    if task is not None:
        await task
