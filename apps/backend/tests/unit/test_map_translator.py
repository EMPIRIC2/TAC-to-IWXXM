"""The map translator drains one area and does not serve HTTP."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest
from src.map_translator import listen_for_stop, main, serve


@pytest.mark.asyncio
async def test_listen_sets_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    handlers: list[Callable[[], None]] = []

    class _Loop:
        def add_signal_handler(self, _sig: int, callback: Callable[[], None]) -> None:
            handlers.append(callback)

    monkeypatch.setattr(asyncio, "get_running_loop", lambda: _Loop())
    stop = asyncio.Event()
    listen_for_stop(stop)
    assert len(handlers) == 2
    handlers[0]()
    assert stop.is_set()


@pytest.mark.asyncio
async def test_listen_ignores_unsupported_loops(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Loop:
        def add_signal_handler(self, _sig: int, _callback: object) -> None:
            raise NotImplementedError

    monkeypatch.setattr(asyncio, "get_running_loop", lambda: _Loop())
    listen_for_stop(asyncio.Event())


@pytest.mark.asyncio
async def test_serve_drains(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    async def fake(*_args: object, **kwargs: object) -> None:
        seen.update(kwargs)

    monkeypatch.setattr("src.map_translator.refresh_until", fake)
    monkeypatch.setattr("src.map_translator.listen_for_stop", lambda _stop: None)
    monkeypatch.setattr("src.map_translator.cache_from_env", lambda: object())
    monkeypatch.setenv("LIVE_MAP_REFRESH_SECONDS", "120")
    await serve()
    assert seen["drain"] is True
    assert seen["pause_sec"] == 120.0


def test_main_runs_serve(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"yes": False}

    async def fake() -> None:
        called["yes"] = True

    monkeypatch.setattr("src.map_translator.serve", fake)
    main()
    assert called["yes"] is True
