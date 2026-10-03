"""One map tile is refreshed at a time, and incomplete feed rows are dropped."""

from __future__ import annotations

import asyncio

import pytest
from src.services import database
from src.services.live_map_cache import LiveMapCache, engine_for_url
from src.services.live_map_refresh import (
    fetch_bbox,
    refresh_one,
    refresh_until,
    reports_from_feed,
    start_live_map_refresh,
    stop_live_map_refresh,
)


def _cache() -> LiveMapCache:
    return LiveMapCache(engine_for_url(None))


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "icaoId": "KJFK",
        "rawOb": "METAR KJFK 031200Z 18012KT 10SM FEW040 15/07 A3005=",
        "lat": 40.64,
        "lon": -73.78,
        "obsTime": 1_700_000_000,
    }
    row.update(overrides)
    return row


def test_feed_rows_keep_metar_and_speci_and_drop_the_rest() -> None:
    reports = reports_from_feed(
        [
            _row(),
            _row(
                icaoId="KBOS",
                rawOb="SPECI KBOS 031205Z 20008KT",
                obsTime="2026-10-03T12:05:00Z",
            ),
            _row(
                icaoId="EGLL",
                raw_text="METAR EGLL 031200Z 27010KT",
                lat=None,
                latitude=51.47,
                lon=None,
                longitude=-0.46,
                obsTime="2026-10-03T12:00:00",
            ),
            _row(icao="KSEA", station_id=None, icaoId=None, rawOb="METAR KSEA"),
            {
                "station_id": "KORD",
                "raw_text": "METAR KORD 031200Z 18010KT",
                "latitude": 41.97,
                "longitude": -87.9,
                "reportTime": 1_700_000_100,
            },
            _row(icaoId="XX", rawOb="METAR XX"),
            _row(icaoId="KDEN", rawOb="  "),
            _row(lat=True, lon=False),
            _row(lat="40", lon="-73"),
            _row(obsTime=None, reportTime=None),
            _row(obsTime="not-a-time"),
            _row(obsTime=True),
            {"icaoId": "NOP"},
        ]
    )
    products = {report.place_key: report.product for report in reports}
    assert products["KJFK"] == "metar"
    assert products["KBOS"] == "speci"
    assert products["EGLL"] == "metar"
    assert products["KSEA"] == "metar"
    assert products["KORD"] == "metar"
    assert "KDEN" not in products


@pytest.mark.asyncio
async def test_refresh_one_stores_then_skips_and_clears_on_failure() -> None:
    cache = _cache()

    async def fetch(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        return [_row()]

    status, index = await refresh_one(cache, fetch, 0)
    assert status == "stored"
    assert index == 1
    places = cache.query(west=-80, south=40, east=-70, north=41, products={"metar"})
    assert places[0]["reports"][0]["tac"].startswith("METAR KJFK")

    assert cache.begin_refresh() is True
    skipped, same = await refresh_one(cache, fetch, 1)
    assert skipped == "skipped"
    assert same == 1
    cache.end_refresh()

    async def boom(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        raise RuntimeError("feed down")

    with pytest.raises(RuntimeError, match="feed down"):
        await refresh_one(cache, boom, 5)
    assert cache.begin_refresh() is True


@pytest.mark.asyncio
async def test_refresh_until_walks_a_second_tile_after_the_pause() -> None:
    cache = _cache()
    seen: list[tuple[float, float, float, float]] = []
    stop = asyncio.Event()

    async def fetch(bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        seen.append(bbox)
        if len(seen) == 2:
            stop.set()
        return []

    await refresh_until(cache, fetch, stop, ((1, 2, 3, 4), (5, 6, 7, 8)), 0)
    assert seen == [(1, 2, 3, 4), (5, 6, 7, 8)]


@pytest.mark.asyncio
async def test_refresh_until_stops_before_the_loop_and_during_the_pause() -> None:
    cache = _cache()
    stop = asyncio.Event()
    stop.set()

    async def unused(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        raise AssertionError("a stopped loop does not fetch")

    await refresh_until(cache, unused, stop, ((1, 2, 3, 4),), 30)

    stop.clear()

    async def fetch(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        asyncio.get_running_loop().call_soon(stop.set)
        return []

    await refresh_until(cache, fetch, stop, ((1, 2, 3, 4),), 30)
    await stop_live_map_refresh(asyncio.Event())


@pytest.mark.asyncio
async def test_fetch_bbox_uses_the_feed_client(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Client:
        async def __aenter__(self) -> _Client:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def fetch_metars_by_bbox(
            self,
            bbox: tuple[float, float, float, float],
            hours: int = 2,
            format_type: str = "json",
        ) -> list[dict[str, str]]:
            assert bbox == (1.0, 2.0, 3.0, 4.0)
            assert hours == 2
            assert format_type == "json"
            return [{"icaoId": "KJFK"}]

    monkeypatch.setattr(
        "src.clients.aviation_weather_client.AviationWeatherClient",
        lambda timeout=30.0: _Client(),
    )
    assert await fetch_bbox((1.0, 2.0, 3.0, 4.0)) == [{"icaoId": "KJFK"}]


@pytest.mark.asyncio
async def test_start_is_off_unless_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = _cache()
    monkeypatch.delenv("LIVE_MAP_REFRESH", raising=False)
    assert start_live_map_refresh(cache) is None
    await stop_live_map_refresh(None)

    monkeypatch.setenv("LIVE_MAP_REFRESH", "1")
    monkeypatch.setenv("LIVE_MAP_REFRESH_SEC", "")

    async def idle(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr("src.services.live_map_refresh.refresh_until", idle)
    stop = start_live_map_refresh(cache)
    assert stop is not None
    await stop_live_map_refresh(stop)


@pytest.mark.asyncio
async def test_api_lifespan_refreshes_only_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi import FastAPI

    async def ready() -> None:
        return None

    monkeypatch.setattr(database, "init_db_engine", ready)
    monkeypatch.setattr(database, "create_tables", ready)
    monkeypatch.setattr(database, "close_db_engine", ready)
    monkeypatch.delenv("LIVE_MAP_REFRESH", raising=False)
    async with database.database_lifespan(FastAPI()):
        assert True

    monkeypatch.setenv("LIVE_MAP_REFRESH", "1")
    monkeypatch.setenv("LIVE_MAP_REFRESH_SEC", "0")

    async def idle(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr("src.services.live_map_refresh.refresh_until", idle)
    async with database.database_lifespan(FastAPI()):
        assert True
