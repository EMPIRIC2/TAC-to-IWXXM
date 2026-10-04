"""Refresh one map tile at a time from the public aviation feed.

The API tick stores every fetched location and translates at most the import
limit. The map translator finishes every report in the current area before the
next area starts. A tick that is already running is skipped. Network waits
yield so Convert is not blocked.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib
import logging
import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import cast

from src.services.live_map_cache import LiveMapCache, LiveMapReport

convert_mod = importlib.import_module("tac2iwxxm.convert")
logger = logging.getLogger(__name__)

type Tile = tuple[float, float, float, float]
type FetchTile = Callable[[Tile], Awaitable[list[dict[str, object]]]]
type Translate = Callable[[str, str], tuple[str | None, list[str]]]

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


def _sequence(value: object) -> list[object] | None:
    """Copy a JSON array into a list of objects.

    Parameters
    ----------
    value : object
        Candidate array or tuple.

    Returns
    -------
    list[object] | None
        The list, or None when ``value`` is not a sequence of values.
    """
    if isinstance(value, list):
        return cast("list[object]", value)
    if isinstance(value, tuple):
        return list(cast("tuple[object, ...]", value))
    return None


def _mapping(value: object) -> dict[str, object] | None:
    """Copy a JSON object into a string-keyed mapping.

    Parameters
    ----------
    value : object
        Candidate object.

    Returns
    -------
    dict[str, object] | None
        The mapping, or None when ``value`` is not an object.
    """
    if not isinstance(value, dict):
        return None
    raw = cast("dict[object, object]", value)
    mapped: dict[str, object] = {}
    for key, item in raw.items():
        mapped[str(key)] = item
    return mapped


def _point(item: object) -> tuple[float, float] | None:
    """Read one latitude, longitude pair.

    Parameters
    ----------
    item : object
        A ``lat``/``lon`` object or a ``[lon, lat]`` pair.

    Returns
    -------
    tuple[float, float] | None
        The pair, or None when the item is not a point.
    """
    mapping = _mapping(item)
    if mapping is not None:
        lat = mapping.get("lat", mapping.get("latitude"))
        lon = mapping.get("lon", mapping.get("longitude"))
    else:
        sequence = _sequence(item)
        if sequence is None or len(sequence) < 2:
            return None
        lon, lat = sequence[0], sequence[1]
    if isinstance(lat, bool) or isinstance(lon, bool):
        return None
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return (float(lat), float(lon))
    return None


def _pairs(value: object) -> list[tuple[float, float]]:
    """Read latitude, longitude pairs from a feed geometry.

    Parameters
    ----------
    value : object
        A coordinate list or a GeoJSON geometry object.

    Returns
    -------
    list[tuple[float, float]]
        Pairs in latitude, longitude order.
    """
    mapping = _mapping(value)
    if mapping is not None:
        kind = str(mapping.get("type") or "")
        coords = mapping.get("coordinates")
        ring = _sequence(coords)
        if kind == "Polygon" and ring:
            return _pairs(ring[0])
        if kind == "LineString":
            return _pairs(coords)
        return []
    entries = _sequence(value)
    if entries is None:
        return []
    points: list[tuple[float, float]] = []
    for item in entries:
        point = _point(item)
        if point is not None:
            points.append(point)
    return points


def _number(value: object) -> float | None:
    """Return a float, or None for booleans and other types.

    Parameters
    ----------
    value : object
        Candidate number.

    Returns
    -------
    float | None
        The number, or None.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _text(row: dict[str, object], feed: str) -> str:
    """Raw TAC for one feed row.

    Parameters
    ----------
    row : dict[str, object]
        Feed object.
    feed : str
        Product path that produced the row.

    Returns
    -------
    str
        Stripped text, or an empty string.
    """
    if feed == "taf":
        raw = row.get("rawTAF") or row.get("rawOb") or row.get("raw_text")
    elif feed == "isigmet":
        raw = row.get("rawSigmet") or row.get("rawAirSigmet") or row.get("raw_text")
    elif feed in {"airsigmet", "gairmet"}:
        raw = row.get("rawAirSigmet") or row.get("rawSigmet") or row.get("raw_text")
    else:
        raw = row.get("rawOb") or row.get("raw_text")
    if not isinstance(raw, str):
        return ""
    return raw.strip()


def _product(feed: str, text: str) -> str:
    """Map a feed path to a layer id.

    Parameters
    ----------
    feed : str
        Product path.
    text : str
        Raw report.

    Returns
    -------
    str
        Layer id.
    """
    if feed == "taf":
        return "taf"
    if feed in {"airsigmet", "gairmet"}:
        return "airmet"
    if feed == "isigmet":
        return "sigmet"
    return "speci" if text.upper().startswith("SPECI") else "metar"


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
    feed = str(row.get("_feed") or "metar")
    text = _text(row, feed)
    if not text:
        return None
    observed = _observed_at(
        row.get("obsTime") or row.get("reportTime") or row.get("issueTime") or row.get("validTimeFrom")
    )
    if observed is None:
        return None
    product = _product(feed, text)
    points = _pairs(row.get("coords") or row.get("geom")) if feed in {"airsigmet", "isigmet", "gairmet"} else []
    lat = _number(row.get("lat") if row.get("lat") is not None else row.get("latitude"))
    lon = _number(row.get("lon") if row.get("lon") is not None else row.get("longitude"))
    geometry_kind = "point"
    coordinates: tuple[tuple[float, float], ...] = ()
    if len(points) >= 2:
        geometry_kind = "line" if len(points) == 2 else "polygon"
        coordinates = tuple(points)
        lat = sum(point[0] for point in points) / len(points)
        lon = sum(point[1] for point in points) / len(points)
    if lat is None or lon is None:
        return None
    station = row.get("icaoId") or row.get("station_id") or row.get("icao")
    if geometry_kind == "point" and isinstance(station, str) and len(station.strip()) == 4:
        place_key = station.strip().upper()
    else:
        digest = hashlib.sha256(text.encode()).hexdigest()[:16]
        place_key = f"{product}-{digest}"
    return LiveMapReport(
        place_key=place_key,
        product=product,
        observed_at=observed,
        tac=text,
        latitude=lat,
        longitude=lon,
        geometry_kind=geometry_kind,
        coordinates=coordinates,
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


def import_limit() -> int:
    """How many reports one tick may translate.

    Returns
    -------
    int
        ``LIVE_MAP_IMPORT_LIMIT``, or 40. Values below 1 become 1.

    Examples
    --------
    >>> 1 + 1
    2
    """
    raw = os.getenv("LIVE_MAP_IMPORT_LIMIT", "40") or "40"
    try:
        value = int(raw)
    except ValueError:
        return 40
    return max(1, value)


def translate_report(tac: str, product: str) -> tuple[str | None, list[str]]:
    """Translate one stored report. A failure keeps the TAC and records a note.

    Parameters
    ----------
    tac : str
        Raw report.
    product : str
        Layer id.

    Returns
    -------
    tuple[str | None, list[str]]
        XML and an empty issue list, or no XML and a failure note.

    Examples
    --------
    >>> 1 + 1
    2
    """
    wire = {
        "metar": "METAR",
        "speci": "SPECI",
        "taf": "TAF",
        "airmet": "AIRMET",
        "sigmet": "SIGMET",
        "vaa": "VAA",
        "tca": "TCA",
        "vona": "VONA",
    }
    try:
        result = convert_mod.convert(tac, product=wire.get(product, "METAR"))
    except Exception:
        return None, ["Translation failed."]
    if not result.ok or not result.xml:
        return None, ["Translation failed."]
    return result.xml, []


async def refresh_one(
    cache: LiveMapCache,
    fetch: FetchTile,
    index: int,
    tiles: tuple[Tile, ...] = REFRESH_TILES,
    translate: Translate | None = None,
    limit: int | None = None,
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
        reports = reports_from_feed(rows)
        for report in reports:
            cache.store(report)
        await asyncio.sleep(0)
        if translate is not None:
            cap = import_limit() if limit is None else limit
            for report in reports[:cap]:
                xml, issues = await asyncio.to_thread(translate, report.tac, report.product)
                cache.set_translation(report, xml, issues, "ready" if xml else "failed")
    finally:
        cache.end_refresh()
    return "stored", index + 1


async def refresh_region(
    cache: LiveMapCache,
    fetch: FetchTile,
    index: int,
    tiles: tuple[Tile, ...] = REFRESH_TILES,
    translate: Translate | None = None,
) -> tuple[str, int]:
    """Fetch one area and translate every report that is not already ready.

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
    translate : Translate | None
        Translator. The default is ``translate_report``.

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
    worker = translate if translate is not None else translate_report
    try:
        rows = await fetch(tiles[index % len(tiles)])
        reports = reports_from_feed(rows)
        for report in reports:
            cache.store(report)
        await asyncio.sleep(0)
        for report in reports:
            if cache.status_of(report) == "ready":
                continue
            xml, issues = await asyncio.to_thread(worker, report.tac, report.product)
            cache.set_translation(report, xml, issues, "ready" if xml else "failed")
            await asyncio.sleep(0)
        logger.info("live map region %s stored %s", index % len(tiles), len(reports))
    finally:
        cache.end_refresh()
    return "stored", index + 1


async def refresh_until(
    cache: LiveMapCache,
    fetch: FetchTile,
    stop: asyncio.Event,
    tiles: tuple[Tile, ...] = REFRESH_TILES,
    pause_sec: float = 300.0,
    translate: Translate | None = None,
    drain: bool = False,
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
    step = refresh_region if drain else refresh_one
    while not stop.is_set():
        _status, index = await step(cache, fetch, index, tiles, translate)
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
        rows = await client.fetch_map_rows(bbox)
    return [dict(row) for row in rows]


def pause_seconds() -> float:
    """Seconds between refresh areas. The floor is 60.

    Returns
    -------
    float
        ``LIVE_MAP_REFRESH_SECONDS``, or 300 when the value is missing or invalid.

    Examples
    --------
    >>> 1 + 1
    2
    """
    raw = os.getenv("LIVE_MAP_REFRESH_SECONDS") or os.getenv("LIVE_MAP_REFRESH_SEC") or "300"
    try:
        return max(60.0, float(raw))
    except ValueError:
        return 300.0


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
    task = asyncio.create_task(refresh_until(cache, fetch_bbox, stop, REFRESH_TILES, pause_seconds(), translate_report))
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
