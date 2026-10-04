"""Live map cache keeps three reports and does not convert them."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.routers.live_map import get_live_map_cache, router, set_live_map_cache
from src.services.live_map_cache import (
    LiveMapCache,
    LiveMapReport,
    apply_refresh,
    cache_from_env,
    engine_for_url,
    live_map_reports,
)


def _cache() -> LiveMapCache:
    return LiveMapCache(engine_for_url(None))


def _report(
    *,
    minutes: int,
    tac: str = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
    product: str = "metar",
    place_key: str = "KJFK",
    latitude: float | None = 40.64,
    longitude: float | None = -73.78,
) -> LiveMapReport:
    return LiveMapReport(
        place_key=place_key,
        product=product,
        observed_at=datetime(2026, 10, 3, 12, 0, tzinfo=UTC) + timedelta(minutes=minutes),
        tac=tac,
        latitude=latitude,
        longitude=longitude,
    )


def test_naive_time_is_rejected() -> None:
    cache = _cache()
    with pytest.raises(ValueError, match="timezone"):
        cache.store(
            LiveMapReport(
                place_key="KJFK",
                product="metar",
                observed_at=datetime(2026, 10, 3, 12, 0),
                tac="METAR KJFK",
                latitude=1.0,
                longitude=2.0,
            )
        )


def test_store_keeps_three_newest_and_replaces_the_same_time() -> None:
    cache = _cache()
    for minute in (1, 2, 3, 4):
        cache.store(_report(minutes=minute, tac=f"M{minute}"))
    replaced = _report(minutes=4, tac="replaced")
    cache.store(replaced)
    places = cache.query(west=-80, south=40, east=-70, north=41, products={"metar"})
    reports = places[0]["reports"]
    assert [item["tac"] for item in reports] == ["replaced", "M3", "M2"]


def test_query_filters_box_product_and_missing_coordinates() -> None:
    cache = _cache()
    cache.store(_report(minutes=1))
    cache.store(_report(minutes=1, product="taf", tac="TAF KJFK", place_key="KJFK"))
    cache.store(_report(minutes=1, place_key="NZWN", latitude=-41.3, longitude=174.8, tac="METAR NZWN"))
    cache.store(_report(minutes=1, place_key="NONE", latitude=None, longitude=None, tac="METAR NONE"))
    places = cache.query(west=-80, south=40, east=-70, north=41, products={"metar"})
    assert [place["place_key"] for place in places] == ["KJFK"]
    assert cache.query(west=-80, south=40, east=-70, north=41, products=set()) == []


def test_query_ignores_reports_beyond_three() -> None:
    cache = _cache()
    cache.store(_report(minutes=1, tac="one"))
    with cache._engine.begin() as conn:
        for minute in (2, 3, 4):
            conn.execute(
                live_map_reports.insert().values(
                    place_key="KJFK",
                    product="metar",
                    observed_at=_report(minutes=minute).observed_at.isoformat(),
                    tac=f"extra{minute}",
                    latitude=40.64,
                    longitude=-73.78,
                )
            )
    places = cache.query(west=-80, south=40, east=-70, north=41, products={"metar"})
    assert len(places[0]["reports"]) == 3


def test_refresh_skips_when_busy_and_clears_after_failure() -> None:
    cache = _cache()
    assert cache.begin_refresh() is True
    assert apply_refresh(cache, [_report(minutes=1)]) == "skipped"
    cache.end_refresh()

    def boom(_report: LiveMapReport) -> None:
        raise RuntimeError("store failed")

    cache.store = boom  # type: ignore[method-assign]
    with pytest.raises(RuntimeError, match="store failed"):
        apply_refresh(cache, [_report(minutes=1)])
    assert cache.begin_refresh() is True


def test_query_returns_geometry_and_ignores_bad_json() -> None:
    cache = _cache()
    cache.store(
        _report(
            minutes=1,
            tac="SIGMET",
            product="sigmet",
            place_key="sigmet-1",
        )
    )
    stored = LiveMapReport(
        place_key="sigmet-1",
        product="sigmet",
        observed_at=datetime(2026, 10, 3, 12, 2, tzinfo=UTC),
        tac="SIGMET NEWER",
        latitude=40.64,
        longitude=-73.78,
        geometry_kind="circle",
        coordinates=((40.0, -74.0), (41.0, -73.0), (40.0, -72.0)),
        radius_m=1000.0,
        issues=("Translation failed.",),
        translation_status="failed",
    )
    cache.store(stored)
    cache.store(_report(minutes=3, tac="OTHER", product="sigmet", place_key="sigmet-2"))
    with cache._engine.begin() as conn:
        conn.execute(
            live_map_reports.update()
            .where(live_map_reports.c.tac == "SIGMET")
            .values(geometry_json='{"no": 1}', issues_json='{"no": 1}')
        )
        conn.execute(
            live_map_reports.update().where(live_map_reports.c.tac == "OTHER").values(geometry_json='{"no": 1}')
        )
    places = cache.query(west=-80, south=40, east=-70, north=41, products={"sigmet"})
    newest = places[0]["reports"][0]
    assert newest["issues"] == ["Translation failed."]
    assert places[0]["geometry"]["kind"] == "circle"
    assert places[0]["geometry"]["radius_m"] == 1000.0
    assert places[0]["geometry"]["coordinates"][0] == [40.0, -74.0]
    older = places[0]["reports"][1]
    assert older["issues"] == []


def test_refresh_stores() -> None:
    cache = _cache()
    assert apply_refresh(cache, [_report(minutes=1, tac="stored")]) == "stored"
    places = cache.query(west=-80, south=40, east=-70, north=41, products={"metar"})
    assert places[0]["reports"][0]["tac"] == "stored"


def test_postgres_engine_skips_table_create() -> None:
    class _Dialect:
        name = "postgresql"

    class _Engine:
        dialect = _Dialect()

    cache = LiveMapCache(_Engine())  # type: ignore[arg-type]
    assert cache.begin_refresh() is True
    assert cache.begin_refresh() is False


def test_ready_translation_survives_the_same_report() -> None:
    cache = _cache()
    report = _report(minutes=1, tac="METAR KJFK")
    assert cache.status_of(report) is None
    cache.store(report)
    assert cache.status_of(report) == "pending"
    cache.set_translation(report, "<iwxxm/>", ["kept"], "ready")
    cache.store(report)
    assert cache.status_of(report) == "ready"
    places = cache.query(west=-80, south=40, east=-70, north=41, products={"metar"})
    assert places[0]["reports"][0]["iwxxm"] == "<iwxxm/>"
    assert places[0]["reports"][0]["issues"] == ["kept"]
    changed = _report(minutes=1, tac="METAR KJFK CHANGED")
    cache.store(changed)
    assert cache.status_of(changed) == "pending"


def test_ready_row_with_empty_fields_stays_ready() -> None:
    cache = _cache()
    report = _report(minutes=2, tac="METAR KJFK EMPTY")
    cache.store(report)
    with cache._engine.begin() as conn:
        conn.execute(
            live_map_reports.update()
            .where(live_map_reports.c.tac == "METAR KJFK EMPTY")
            .values(translation_status="ready", iwxxm=None, issues_json=None)
        )
    cache.store(report)
    assert cache.status_of(report) == "ready"
    with cache._engine.begin() as conn:
        conn.execute(
            live_map_reports.update()
            .where(live_map_reports.c.tac == "METAR KJFK EMPTY")
            .values(translation_status=None)
        )
    assert cache.status_of(report) is None


def test_engine_rewrites_postgres_urls() -> None:
    asyncpg = engine_for_url("postgresql+asyncpg://u:p@localhost/db?ssl=require")
    assert asyncpg.url.drivername == "postgresql+psycopg"
    assert "sslmode=require" in str(asyncpg.url)
    asyncpg.dispose()
    psycopg2 = engine_for_url("postgresql+psycopg2://u:p@localhost/db")
    assert psycopg2.url.drivername == "postgresql+psycopg"
    psycopg2.dispose()
    plain = engine_for_url("postgresql://u:p@localhost/db?sslmode=require")
    assert plain.url.drivername == "postgresql+psycopg"
    assert str(plain.url).count("sslmode") == 1
    plain.dispose()


def test_engine_url_and_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    memory = engine_for_url("  ")
    assert memory.dialect.name == "sqlite"
    path = tmp_path / "map.sqlite"
    monkeypatch.setenv("LIVE_MAP_CACHE_URL", f"sqlite:///{path}")
    first = cache_from_env()
    first.store(_report(minutes=1, tac="persisted"))
    second = cache_from_env()
    places = second.query(west=-80, south=40, east=-70, north=41, products={"metar"})
    assert places[0]["reports"][0]["tac"] == "persisted"


def test_read_live_map_route(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LIVE_MAP_CACHE_URL", raising=False)
    set_live_map_cache(None)
    cache = get_live_map_cache()
    assert get_live_map_cache() is cache
    cache.store(_report(minutes=1, tac="on map"))
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    ok = client.get("/api/v1/live-map", params={"west": -80, "south": 40, "east": -70, "north": 41})
    assert ok.status_code == 200
    assert ok.json()["places"][0]["reports"][0]["tac"] == "on map"
    blank = client.get(
        "/api/v1/live-map",
        params={"west": -80, "south": 40, "east": -70, "north": 41, "products": " , "},
    )
    assert blank.status_code == 200
    bad_box = client.get(
        "/api/v1/live-map",
        params={"west": 10, "south": 0, "east": 0, "north": 1},
    )
    assert bad_box.status_code == 400
    world = client.get(
        "/api/v1/live-map",
        params={"west": -284, "south": -80, "east": 284, "north": 80},
    )
    assert world.status_code == 200
    east_only = client.get(
        "/api/v1/live-map",
        params={"west": -170, "south": -80, "east": 190, "north": 80},
    )
    assert east_only.status_code == 200
    wide = client.get(
        "/api/v1/live-map",
        params={"west": -180, "south": -90, "east": 180, "north": 90},
    )
    assert wide.status_code == 200
    flipped = client.get(
        "/api/v1/live-map",
        params={"west": -10, "south": 20, "east": 10, "north": 0},
    )
    assert flipped.status_code == 400
    bad_layer = client.get(
        "/api/v1/live-map",
        params={"west": -80, "south": 40, "east": -70, "north": 41, "products": "spacewx"},
    )
    assert bad_layer.status_code == 400
    set_live_map_cache(None)
