"""One map tile is refreshed at a time, and incomplete feed rows are dropped."""

from __future__ import annotations

import asyncio

import pytest
from src.services import database
from src.services.live_map_cache import LiveMapCache, engine_for_url
from src.services.live_map_refresh import (
    fetch_bbox,
    import_limit,
    refresh_one,
    refresh_region,
    refresh_until,
    reports_from_feed,
    start_live_map_refresh,
    stop_live_map_refresh,
    translate_report,
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
async def test_refresh_until_returns_when_the_pause_ends(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = _cache()
    stop = asyncio.Event()

    async def fetch(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        return []

    async def finish(awaitable: object, _timeout: float) -> None:
        close = getattr(awaitable, "close", None)
        if close is not None:
            close()
        stop.set()

    monkeypatch.setattr(asyncio, "wait_for", finish)
    await refresh_until(cache, fetch, stop, ((1, 2, 3, 4),), 30)


@pytest.mark.asyncio
async def test_fetch_bbox_uses_the_feed_client(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Client:
        async def __aenter__(self) -> _Client:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def fetch_map_rows(
            self,
            bbox: tuple[float, float, float, float],
        ) -> list[dict[str, str]]:
            assert bbox == (1.0, 2.0, 3.0, 4.0)
            return [{"icaoId": "KJFK"}]

    monkeypatch.setattr(
        "src.clients.aviation_weather_client.AviationWeatherClient",
        lambda timeout=30.0: _Client(),
    )
    assert await fetch_bbox((1.0, 2.0, 3.0, 4.0)) == [{"icaoId": "KJFK"}]


def test_polygon_rows_keep_a_centroid_and_station_rows_stay_points() -> None:
    reports = reports_from_feed(
        [
            {
                "_feed": "isigmet",
                "rawSigmet": "WSUS31 KZNY 031200 SIGMET",
                "validTimeFrom": "2026-10-03T12:00:00Z",
                "coords": [
                    {"lat": 40.0, "lon": -74.0},
                    {"lat": 41.0, "lon": -73.0},
                    {"lat": 40.0, "lon": -72.0},
                ],
            },
            {
                "_feed": "taf",
                "icaoId": "KJFK",
                "rawTAF": "TAF KJFK 031200Z 0312/0412 18010KT",
                "lat": 40.64,
                "lon": -73.78,
                "issueTime": 1_700_000_000,
            },
            {
                "_feed": "airsigmet",
                "rawAirSigmet": "short",
                "validTimeFrom": "2026-10-03T12:00:00Z",
            },
        ]
    )
    kinds = {report.product: report.geometry_kind for report in reports}
    assert kinds["sigmet"] == "polygon"
    assert kinds["taf"] == "point"
    sigmet = next(report for report in reports if report.product == "sigmet")
    assert sigmet.latitude == pytest.approx(40.3333333333)
    assert len(sigmet.place_key) <= 64
    shapes = reports_from_feed(
        [
            {
                "_feed": "gairmet",
                "rawAirSigmet": "line",
                "validTimeFrom": "2026-10-03T12:00:00Z",
                "geom": {
                    "type": "LineString",
                    "coordinates": ((-74.0, 40.0), (-73.0, 41.0)),
                },
            },
            {
                "_feed": "airsigmet",
                "rawAirSigmet": "poly",
                "validTimeFrom": "2026-10-03T12:00:00Z",
                "geom": {
                    "type": "Polygon",
                    "coordinates": [[[-74.0, 40.0], [-73.0, 41.0], [-72.0, 40.0]]],
                },
            },
            {
                "_feed": "airsigmet",
                "rawAirSigmet": "skip",
                "validTimeFrom": "2026-10-03T12:00:00Z",
                "coords": [{"lat": True, "lon": 1}, "nope", {"lat": "x", "lon": 1}],
                "geom": {"type": "Point"},
            },
            {
                "_feed": "isigmet",
                "rawSigmet": "text only",
                "validTimeFrom": "not-a-time",
                "coords": "POLYGON",
            },
            {
                "_feed": "airsigmet",
                "icaoId": "KKCI",
                "rawAirSigmet": "point fallback",
                "lat": 40.0,
                "lon": -100.0,
                "validTimeFrom": "2026-10-03T12:00:00Z",
                "geom": {"type": "Point"},
            },
        ]
    )
    assert {report.geometry_kind for report in shapes} == {"line", "polygon", "point"}


def test_convective_sigmet_on_the_airmet_feed_is_a_sigmet() -> None:
    reports = reports_from_feed(
        [
            {
                "_feed": "airsigmet",
                "rawAirSigmet": "WSUS31 KKCI 051455\nCONVECTIVE SIGMET 27E\nVALID UNTIL 1655Z\n",
                "lat": 42.0,
                "lon": -75.0,
                "validTimeFrom": "2026-10-05T14:55:00Z",
            },
            {
                "_feed": "airsigmet",
                "rawAirSigmet": "WAUS41 KKCI 051455\nAIRMET SIERRA FOR IFR\n",
                "lat": 41.0,
                "lon": -74.0,
                "validTimeFrom": "2026-10-05T14:55:00Z",
            },
        ]
    )
    assert [report.product for report in reports] == ["sigmet", "airmet"]


def test_gairmet_feed_is_its_own_product() -> None:
    reports = reports_from_feed(
        [
            {
                "_feed": "gairmet",
                "rawAirSigmet": "G-AIRMET SIERRA FOR IFR",
                "lat": 40.0,
                "lon": -75.0,
                "validTimeFrom": "2026-10-05T14:55:00Z",
            },
            {
                "_feed": "airsigmet",
                "rawAirSigmet": "WSUS31 KKCI 051455\nCONVECTIVE SIGMET 27E\n",
                "lat": 42.0,
                "lon": -75.0,
                "validTimeFrom": "2026-10-05T14:55:00Z",
            },
        ]
    )
    assert [report.product for report in reports] == ["gairmet", "sigmet"]


def test_import_limit_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIVE_MAP_IMPORT_LIMIT", "0")
    assert import_limit() == 1
    monkeypatch.setenv("LIVE_MAP_IMPORT_LIMIT", "nope")
    assert import_limit() == 40
    monkeypatch.setenv("LIVE_MAP_IMPORT_LIMIT", "")
    assert import_limit() == 40


def test_translate_report_records_success_and_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Ok:
        ok = True
        xml = "<iwxxm/>"

    class _Bad:
        ok = False
        xml = None

    def convert(_tac: str, *, product: str) -> object:
        if product == "VAA":
            raise RuntimeError("down")
        if product == "METAR":
            return _Ok()
        return _Bad()

    monkeypatch.setattr("src.services.live_map_refresh.convert_mod.convert", convert)
    assert translate_report("METAR KJFK", "metar") == ("<iwxxm/>", [])
    assert translate_report("VAA", "vaa") == (None, ["Translation failed."])
    assert translate_report("TAF KJFK", "taf") == (None, ["Translation failed."])


@pytest.mark.asyncio
async def test_refresh_translates_only_the_import_limit() -> None:
    cache = _cache()
    calls: list[str] = []

    def translate(tac: str, product: str) -> tuple[str | None, list[str]]:
        calls.append(tac)
        if product == "metar" and tac.endswith("FAIL"):
            return None, ["Translation failed."]
        return "<iwxxm/>", []

    async def fetch(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        return [
            _row(icaoId="KJFK", rawOb="METAR KJFK ONE"),
            _row(icaoId="KBOS", rawOb="METAR KBOS TWO"),
            _row(icaoId="KORD", rawOb="METAR KORD FAIL"),
        ]

    status, _index = await refresh_one(cache, fetch, 0, translate=translate, limit=2)
    assert status == "stored"
    assert calls == ["METAR KJFK ONE", "METAR KBOS TWO"]
    places = cache.query(west=-180, south=-90, east=180, north=90, products={"metar"})
    by_key = {place["place_key"]: place for place in places}
    assert set(by_key) == {"KJFK", "KBOS", "KORD"}
    assert by_key["KJFK"]["reports"][0]["iwxxm"] == "<iwxxm/>"
    assert by_key["KORD"]["reports"][0]["iwxxm"] is None
    assert by_key["KORD"]["reports"][0]["issues"] == []
    await refresh_one(cache, fetch, 0, translate=translate)
    assert len(calls) == 5


@pytest.mark.asyncio
async def test_refresh_region_finishes_the_area_and_keeps_ready_rows() -> None:
    cache = _cache()
    calls: list[str] = []

    def translate(tac: str, product: str) -> tuple[str | None, list[str]]:
        calls.append(tac)
        if product == "metar" and tac.endswith("FAIL") and calls.count(tac) == 1:
            return None, ["Translation failed."]
        return "<iwxxm/>", []

    async def fetch(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        return [
            _row(icaoId="KJFK", rawOb="METAR KJFK ONE"),
            _row(icaoId="KBOS", rawOb="METAR KBOS TWO"),
            _row(icaoId="KORD", rawOb="METAR KORD FAIL"),
        ]

    status, index = await refresh_region(cache, fetch, 0, translate=translate)
    assert status == "stored"
    assert index == 1
    assert calls == ["METAR KJFK ONE", "METAR KBOS TWO", "METAR KORD FAIL"]
    status, index = await refresh_region(cache, fetch, 0, translate=translate)
    assert status == "stored"
    assert index == 1
    assert calls[-1] == "METAR KORD FAIL"
    assert calls.count("METAR KJFK ONE") == 1
    places = cache.query(west=-180, south=-90, east=180, north=90, products={"metar"})
    by_key = {place["place_key"]: place for place in places}
    assert by_key["KORD"]["reports"][0]["iwxxm"] == "<iwxxm/>"


@pytest.mark.asyncio
async def test_refresh_region_skips_when_busy_and_uses_the_default_translator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache = _cache()
    cache.begin_refresh()

    async def fetch(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        return [_row()]

    skipped, index = await refresh_region(cache, fetch, 4)
    assert skipped == "skipped"
    assert index == 4
    cache.end_refresh()

    def translate(tac: str, _product: str) -> tuple[str | None, list[str]]:
        return f"<done>{tac}</done>", []

    monkeypatch.setattr("src.services.live_map_refresh.translate_report", translate)

    async def boom(_bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        raise RuntimeError("down")

    with pytest.raises(RuntimeError, match="down"):
        await refresh_region(cache, boom, 0)
    assert cache.begin_refresh() is True
    cache.end_refresh()
    status, index = await refresh_region(cache, fetch, 0)
    assert status == "stored"
    assert index == 1
    places = cache.query(west=-180, south=-90, east=180, north=90, products={"metar"})
    stored = places[0]["reports"][0]["iwxxm"]
    assert stored is not None
    assert stored.startswith("<done>")


@pytest.mark.asyncio
async def test_refresh_until_drains_before_the_next_area() -> None:
    cache = _cache()
    seen: list[tuple[float, float, float, float]] = []
    stop = asyncio.Event()

    async def fetch(bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
        seen.append(bbox)
        if len(seen) == 2:
            stop.set()
        return [_row(rawOb=f"METAR KJFK {len(seen)}")]

    def translate(_tac: str, _product: str) -> tuple[str | None, list[str]]:
        return "<iwxxm/>", []

    await refresh_until(cache, fetch, stop, pause_sec=0.01, translate=translate, drain=True)
    assert len(seen) == 2
    assert seen[0] != seen[1]


@pytest.mark.asyncio
async def test_start_is_off_unless_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = _cache()
    monkeypatch.delenv("LIVE_MAP_REFRESH", raising=False)
    assert start_live_map_refresh(cache) is None
    await stop_live_map_refresh(None)

    monkeypatch.setenv("LIVE_MAP_REFRESH", "1")
    monkeypatch.setenv("LIVE_MAP_REFRESH_SECONDS", "nope")
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
