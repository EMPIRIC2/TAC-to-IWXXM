"""FR-045 live-map evaluation snapshot unit tests."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.routers.live_map import router, set_live_map_cache
from src.services.live_map_cache import LiveMapCache, LiveMapReport, engine_for_url
from src.services.live_map_eval import (
    build_snapshot_from_places,
    compute_and_store,
    eval_interval_seconds,
    refresh_enabled,
    start_live_map_eval,
    stop_live_map_eval,
)
from src.services.live_map_eval_store import (
    LiveMapEvalStore,
    empty_snapshot,
    get_live_map_eval_store,
    set_live_map_eval_store,
)


@pytest.fixture
def eval_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Router-only app — avoid full API lifespan / DB connect hangs."""
    store = LiveMapEvalStore()
    store.enable_memory_only()
    set_live_map_eval_store(store)
    monkeypatch.setenv("LIVE_MAP_EVAL_REFRESH_ENABLED", "false")
    monkeypatch.setenv("LIVE_MAP_EVAL_INTERVAL_SEC", "0")
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    yield client
    set_live_map_eval_store(None)
    set_live_map_cache(None)


def test_empty_snapshot_shape() -> None:
    body = empty_snapshot(computed_at=datetime(2026, 11, 24, 12, 0, tzinfo=UTC))
    assert body["partial_decode_count"] == 0
    assert body["iwxxm_validation"] == {"pass": 0, "fail": 0, "skip": 0}
    assert "metar" in body["products"]


def test_eval_interval_defaults_and_floor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LIVE_MAP_EVAL_INTERVAL_SEC", raising=False)
    assert eval_interval_seconds() == 900
    monkeypatch.setenv("LIVE_MAP_EVAL_INTERVAL_SEC", "nope")
    assert eval_interval_seconds() == 900
    monkeypatch.setenv("LIVE_MAP_EVAL_INTERVAL_SEC", "30")
    assert eval_interval_seconds() == 60


def test_build_snapshot_counts_issues_and_iwxxm() -> None:
    places = [
        {
            "place_key": "KJFK",
            "product": "metar",
            "reports": [
                {
                    "observed_at": "2026-11-24T12:00:00Z",
                    "tac": "METAR KJFK ...",
                    "iwxxm": None,
                    "issues": ["MISSING_VIS: no visibility", ""],
                },
                "skip-me",
            ],
        },
        {
            "place_key": "EGLL",
            "product": "metar",
            "reports": [
                {
                    "observed_at": "2026-11-24T12:00:00Z",
                    "tac": "METAR EGLL ...",
                    "iwxxm": "<iwxxm/>",
                    "issues": [],
                }
            ],
        },
        {
            "place_key": "KORD",
            "product": "metar",
            "reports": [
                {
                    "observed_at": "2026-11-24T12:00:00Z",
                    "tac": "METAR KORD ...",
                    "iwxxm": None,
                    "issues": None,
                }
            ],
        },
        {"place_key": "X", "product": "metar", "reports": "bad"},
        {"place_key": "Y", "product": "unknown", "reports": []},
    ]
    body = build_snapshot_from_places(places, computed_at=datetime(2026, 11, 24, 12, 0, tzinfo=UTC))
    assert body["lint_count"] == 2
    assert body["convert_failure_count"] == 1
    assert body["iwxxm_validation"]["pass"] == 1
    assert body["iwxxm_validation"]["fail"] == 1
    assert body["iwxxm_validation"]["skip"] == 1
    assert body["partial_decode_count"] == 1
    assert body["top_lint_codes"][0]["code"] == "MISSING_VIS"
    assert any(row["code"] == "ISSUE" for row in body["failure_locations"])


def test_get_eval_returns_zeros(eval_client: TestClient) -> None:
    resp = eval_client.get("/api/v1/live-map/eval")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["lint_count"] == 0
    assert payload["failure_locations"] == []


def test_refresh_disabled_returns_404(eval_client: TestClient) -> None:
    resp = eval_client.post("/api/v1/live-map/eval/refresh")
    assert resp.status_code == 404


def test_refresh_enabled_writes_snapshot(eval_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIVE_MAP_EVAL_REFRESH_ENABLED", "true")
    assert refresh_enabled() is True
    cache = LiveMapCache(engine_for_url(None))
    set_live_map_cache(cache)
    cache.store(
        LiveMapReport(
            place_key="KJFK",
            product="metar",
            observed_at=datetime.now(tz=UTC),
            tac="METAR KJFK 241200Z 18005KT 10SM FEW050 20/10 A2992=",
            latitude=40.64,
            longitude=-73.78,
            iwxxm="<x/>",
            issues=(),
            translation_status="ready",
        )
    )
    resp = eval_client.post("/api/v1/live-map/eval/refresh")
    assert resp.status_code == 200
    assert resp.json()["iwxxm_validation"]["pass"] >= 1
    got = eval_client.get("/api/v1/live-map/eval")
    assert got.json()["iwxxm_validation"]["pass"] >= 1


def test_compute_and_store_empty_cache() -> None:
    store = LiveMapEvalStore()
    store.enable_memory_only()
    cache = LiveMapCache(engine_for_url(None))
    payload = compute_and_store(cache=cache, store=store)
    assert payload["lint_count"] == 0


def test_compute_and_store_uses_process_singletons(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = LiveMapEvalStore()
    store.enable_memory_only()
    set_live_map_eval_store(store)
    cache = LiveMapCache(engine_for_url(None))
    set_live_map_cache(cache)
    monkeypatch.setenv("LIVE_MAP_EVAL_INTERVAL_SEC", "0")
    payload = compute_and_store()
    assert payload["lint_count"] == 0
    set_live_map_eval_store(None)
    set_live_map_cache(None)


@pytest.mark.asyncio
async def test_start_stop_eval_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.services import live_map_eval as eval_mod

    monkeypatch.setenv("LIVE_MAP_EVAL_INTERVAL_SEC", "0")
    assert start_live_map_eval() is None
    await stop_live_map_eval(None)

    monkeypatch.setenv("LIVE_MAP_EVAL_INTERVAL_SEC", "60")

    async def idle(_stop: asyncio.Event) -> None:
        return None

    monkeypatch.setattr(eval_mod, "_eval_loop", idle)
    stop = start_live_map_eval()
    assert stop is not None
    again = start_live_map_eval()
    assert again is stop
    await stop_live_map_eval(stop)


@pytest.mark.asyncio
async def test_eval_loop_timeout_then_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.services import live_map_eval as eval_mod
    from src.services.live_map_eval import _eval_loop

    calls = {"n": 0}

    def fake_compute(**_kwargs: object) -> dict[str, object]:
        calls["n"] += 1
        return empty_snapshot()

    monkeypatch.setattr(eval_mod, "compute_and_store", fake_compute)
    monkeypatch.setattr(eval_mod, "eval_interval_seconds", lambda: 60)

    stop = asyncio.Event()
    waits = {"n": 0}

    async def wait_for(awaitable: object, **_kwargs: object) -> object:
        if asyncio.iscoroutine(awaitable):
            awaitable.close()
        waits["n"] += 1
        if waits["n"] == 1:
            raise TimeoutError
        stop.set()
        return None

    monkeypatch.setattr(eval_mod.asyncio, "wait_for", wait_for)
    await _eval_loop(stop)
    assert calls["n"] >= 1


@pytest.mark.asyncio
async def test_stop_eval_cancels_hung_task(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.services import live_map_eval as eval_mod

    gate = asyncio.Event()

    async def never() -> None:
        await gate.wait()

    hung = asyncio.create_task(never(), name="hung-eval")
    eval_mod._eval_task = hung
    stop = asyncio.Event()
    eval_mod._eval_stop = stop

    async def fast_wait(awaitable: object, **_kwargs: object) -> object:
        del awaitable
        raise TimeoutError

    monkeypatch.setattr(eval_mod.asyncio, "wait_for", fast_wait)
    await stop_live_map_eval(stop)
    assert hung.cancelled() or hung.done()


def test_store_memory_roundtrip() -> None:
    store = LiveMapEvalStore()
    store.enable_memory_only()
    body = empty_snapshot(computed_at=datetime(2026, 11, 24, 12, 0, tzinfo=UTC))
    store.write_snapshot(body)
    assert store.read_latest()["computed_at"].startswith("2026-11-24")


def test_store_configure_and_db_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    store = LiveMapEvalStore()
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.delenv("LIVE_MAP_CACHE_URL", raising=False)
    store.configure_from_env()
    assert store._use_db is False

    engine = MagicMock()
    begin_cm = MagicMock()
    conn = MagicMock()
    begin_cm.__enter__.return_value = conn
    begin_cm.__exit__.return_value = False
    engine.begin.return_value = begin_cm

    connect_cm = MagicMock()
    connect_cm.__enter__.return_value = conn
    connect_cm.__exit__.return_value = False
    engine.connect.return_value = connect_cm

    row = MagicMock()
    row.__getitem__.side_effect = lambda i: {"lint_count": 9} if i == 0 else None
    conn.execute.return_value.fetchone.return_value = row

    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setattr(
        "src.services.station_health_postgres_url.sync_database_url",
        lambda _raw: "postgresql://u:p@localhost/db",
    )
    monkeypatch.setattr(
        "sqlalchemy.create_engine",
        lambda *_a, **_k: engine,
    )
    store.configure_from_env()
    assert store._use_db is True
    written = store.write_snapshot(empty_snapshot(computed_at=datetime(2026, 11, 24, 12, 0, tzinfo=UTC)))
    assert written["lint_count"] == 0
    assert store.read_latest()["lint_count"] == 9

    # Missing computed_at uses now(); string / non-dict payload shapes.
    store.write_snapshot({"window_hours": 24, "lint_count": 0})
    conn.execute.return_value.fetchone.return_value = None
    assert store.read_latest()["window_hours"] == 24
    conn.execute.return_value.fetchone.return_value = ('{"lint_count": 2}',)
    assert store._read_db() == {"lint_count": 2}
    conn.execute.return_value.fetchone.return_value = (123,)
    assert store._read_db() is None
    conn.execute.side_effect = RuntimeError("missing table")
    assert store._read_db() is None


def test_store_configure_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    store = LiveMapEvalStore()
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")

    def boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("no engine")

    monkeypatch.setattr(
        "src.services.station_health_postgres_url.sync_database_url",
        lambda _raw: "postgresql://u:p@localhost/db",
    )
    monkeypatch.setattr("sqlalchemy.create_engine", boom)
    store.configure_from_env()
    assert store._use_db is False


def test_get_live_map_eval_store_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    set_live_map_eval_store(None)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("LIVE_MAP_CACHE_URL", raising=False)
    first = get_live_map_eval_store()
    second = get_live_map_eval_store()
    assert first is second
    set_live_map_eval_store(None)
