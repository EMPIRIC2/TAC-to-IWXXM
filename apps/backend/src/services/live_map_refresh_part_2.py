"""Part 2 of ``live_map_refresh.py`` (line-cap split)."""

from __future__ import annotations

import asyncio
import os

from .live_map_cache import LiveMapCache
from .live_map_refresh_part_1 import (
    REFRESH_TILES,
    FetchTile,
    Tile,
    Translate,
    _tasks,
    fetch_bbox,
    import_limit,
    logger,
    pause_seconds,
    reports_from_feed,
    translate_report,
)


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
    """
    if os.getenv("LIVE_MAP_REFRESH", "").strip() != "1":
        return None
    stop = asyncio.Event()
    task = asyncio.create_task(refresh_until(cache, fetch_bbox, stop, REFRESH_TILES, pause_seconds(), translate_report))
    _tasks[id(stop)] = task
    return stop
