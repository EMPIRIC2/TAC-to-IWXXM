"""Unit tests for aviation weather clients."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from src.clients.aviation_weather_client import (
    AviationWeatherAPIError,
    AviationWeatherClient,
    CachedAviationWeatherClient,
)


class _DummyResponse:
    def __init__(self, text: str, status_code: int = 200, json_payload=None):
        self.text = text
        self.status_code = status_code
        self._json_payload = json_payload

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://example.test")
            response = httpx.Response(self.status_code, text=self.text, request=request)
            raise httpx.HTTPStatusError("boom", request=request, response=response)

    def json(self):
        if isinstance(self._json_payload, Exception):
            raise self._json_payload
        return self._json_payload


@pytest.mark.asyncio
async def test_context_manager_sets_and_closes_client(monkeypatch: pytest.MonkeyPatch) -> None:
    closed = {"value": False}

    class _FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def aclose(self):
            closed["value"] = True

    monkeypatch.setattr("src.clients.aviation_weather_client.httpx.AsyncClient", _FakeAsyncClient)

    async with AviationWeatherClient(timeout=12.0) as client:
        assert client._client is not None
        assert client._client.timeout == 12.0

    assert closed["value"] is True


@pytest.mark.asyncio
async def test_context_manager_exit_without_client_is_noop() -> None:
    client = AviationWeatherClient()

    await client.__aexit__(None, None, None)

    assert client._client is None


@pytest.mark.asyncio
async def test_fetch_metar_batch_handles_parallel_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AviationWeatherClient()
    client._client = AsyncMock()
    client.BATCH_SIZE = 2

    async def fake_fetch_format(batch, format_type, _hours):
        if format_type == "raw":
            return {batch[0]: "RAW"}
        raise RuntimeError("iwxxm failed")

    sleep_calls = []

    async def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(client, "_fetch_format", fake_fetch_format)
    monkeypatch.setattr("src.clients.aviation_weather_client.asyncio.sleep", fake_sleep)

    result = await client.fetch_metar_batch(["KJFK", "KBOS", "KLAX"], hours=2.0)

    assert result["KJFK"] == ("RAW", None)
    assert result["KBOS"] == (None, None)
    assert result["KLAX"] == ("RAW", None)
    assert sleep_calls == [client.RATE_LIMIT_DELAY]


@pytest.mark.asyncio
async def test_fetch_metar_batch_requires_initialized_client() -> None:
    client = AviationWeatherClient()

    with pytest.raises(RuntimeError, match="Client not initialized"):
        await client.fetch_metar_batch(["KJFK"])


@pytest.mark.asyncio
async def test_fetch_metar_batch_handles_raw_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AviationWeatherClient()
    client._client = AsyncMock()

    async def fake_fetch_format(batch, format_type, _hours):
        if format_type == "raw":
            raise RuntimeError("raw failed")
        return {batch[0]: "<xml/>"}

    monkeypatch.setattr(client, "_fetch_format", fake_fetch_format)

    result = await client.fetch_metar_batch(["KJFK"])

    assert result == {"KJFK": (None, "<xml/>")}


@pytest.mark.asyncio
async def test_fetch_format_success_and_error_paths() -> None:
    client = AviationWeatherClient()

    with pytest.raises(RuntimeError, match="Client not initialized"):
        await client._fetch_format(["KJFK"], "raw", 1.0)

    request = httpx.Request("GET", "https://example.test")

    async def status_404(*_args, **_kwargs):
        response = httpx.Response(404, request=request, text="not found")
        raise httpx.HTTPStatusError("404", request=request, response=response)

    async def status_500(*_args, **_kwargs):
        response = httpx.Response(500, request=request, text="server error")
        raise httpx.HTTPStatusError("500", request=request, response=response)

    async def request_fail(*_args, **_kwargs):
        raise httpx.RequestError("down", request=request)

    client._client = SimpleNamespace(get=status_404)
    assert await client._fetch_format(["KJFK"], "raw", 1.0) == {}

    client._client = SimpleNamespace(get=status_500)
    with pytest.raises(AviationWeatherAPIError, match="HTTP 500"):
        await client._fetch_format(["KJFK"], "raw", 1.0)

    client._client = SimpleNamespace(get=request_fail)
    with pytest.raises(AviationWeatherAPIError, match="Request failed"):
        await client._fetch_format(["KJFK"], "raw", 1.0)


@pytest.mark.asyncio
async def test_fetch_format_success_parses_response(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AviationWeatherClient()
    response = _DummyResponse("METAR KJFK 101851Z", status_code=200)
    captured = {}

    async def fake_get(url, params=None):
        captured["url"] = url
        captured["params"] = params
        return response

    monkeypatch.setattr(client, "_parse_response", lambda content, format_type, station_ids: {station_ids[0]: content})
    client._client = SimpleNamespace(get=fake_get)

    result = await client._fetch_format(["KJFK"], "raw", 2.5)

    assert result == {"KJFK": "METAR KJFK 101851Z"}
    assert captured["url"].endswith("/metar")
    assert captured["params"] == {"ids": "KJFK", "format": "raw", "hours": 2.5}


@pytest.mark.asyncio
async def test_fetch_metars_by_bbox_json_raw_and_errors() -> None:
    client = AviationWeatherClient()

    with pytest.raises(RuntimeError, match="Client not initialized"):
        await client.fetch_metars_by_bbox((-1, -1, 1, 1))

    async def get_empty(*_args, **_kwargs):
        return _DummyResponse("[]", status_code=200, json_payload=[])

    async def get_json(*_args, **_kwargs):
        return _DummyResponse('[{"icaoId": "KJFK"}]', status_code=200, json_payload=[{"icaoId": "KJFK"}])

    async def get_invalid_json(*_args, **_kwargs):
        return _DummyResponse("not-json", status_code=200, json_payload=ValueError("bad json"))

    async def get_raw(*_args, **_kwargs):
        return _DummyResponse("METAR KJFK 101851Z\n\nSPECI KBOS 101900Z", status_code=200)

    request = httpx.Request("GET", "https://example.test")

    async def get_404(*_args, **_kwargs):
        response = httpx.Response(404, request=request, text="missing")
        raise httpx.HTTPStatusError("404", request=request, response=response)

    async def get_req_err(*_args, **_kwargs):
        raise httpx.RequestError("net", request=request)

    client._client = SimpleNamespace(get=get_json)
    assert await client.fetch_metars_by_bbox((-1, -1, 1, 1), format_type="json") == [{"icaoId": "KJFK"}]

    client._client = SimpleNamespace(get=get_empty)
    assert await client.fetch_metars_by_bbox((-1, -1, 1, 1), format_type="json") == []

    client._client = SimpleNamespace(get=get_invalid_json)
    assert await client.fetch_metars_by_bbox((-1, -1, 1, 1), format_type="json") == []

    client._client = SimpleNamespace(get=get_raw)
    raw = await client.fetch_metars_by_bbox((-1, -1, 1, 1), format_type="raw")
    assert raw == [{"rawOb": "METAR KJFK 101851Z"}, {"rawOb": "SPECI KBOS 101900Z"}]

    client._client = SimpleNamespace(get=get_404)
    assert await client.fetch_metars_by_bbox((-1, -1, 1, 1), format_type="json") == []

    client._client = SimpleNamespace(get=get_req_err)
    with pytest.raises(AviationWeatherAPIError, match="Request failed"):
        await client.fetch_metars_by_bbox((-1, -1, 1, 1), format_type="json")


def test_parse_response_and_extract_station_paths() -> None:
    client = AviationWeatherClient()

    raw = client._parse_response(
        "METAR KJFK 101851Z\nKBOS 101900Z\nTOKEN\nSPECI KLAX 101930Z",
        "raw",
        ["KJFK", "KBOS", "KLAX"],
    )
    assert set(raw.keys()) == {"KJFK", "KBOS", "KLAX"}

    iwxxm_multi = "<?xml version='1.0'?><doc designator=\"KJFK\"/><?xml version='1.0'?><doc><icaoId>KBOS</icaoId></doc>"
    iwxxm_result = client._parse_response(iwxxm_multi, "iwxxm", ["KJFK", "KBOS"])
    assert set(iwxxm_result.keys()) == {"KJFK", "KBOS"}

    iwxxm_single = client._parse_response(
        "<doc><icaoId>KSEA</icaoId></doc>",
        "iwxxm",
        ["KSEA", "KJFK"],
    )
    assert iwxxm_single == {"KSEA": "<doc><icaoId>KSEA</icaoId></doc>"}

    assert client._parse_response("<doc><icaoId>EGLL</icaoId></doc>", "iwxxm", ["KSEA"]) == {}
    assert client._parse_response("", "iwxxm", ["KSEA"]) == {}

    assert client._extract_station_from_xml('<doc designator="KLAX"/>') == "KLAX"
    assert client._extract_station_from_xml("<doc><icaoId>KSEA</icaoId></doc>") == "KSEA"
    assert client._extract_station_from_xml("<doc/>") is None


@pytest.mark.asyncio
async def test_fetch_random_sample_defaults_and_count_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AviationWeatherClient()

    async def fake_fetch(_bbox, hours, format_type):
        assert hours == 3
        assert format_type == "json"
        return [{"rawOb": "A"}, {"rawOb": "B"}, {"rawOb": "C"}]

    monkeypatch.setattr(client, "fetch_metars_by_bbox", fake_fetch)

    sample = await client.fetch_random_sample(count=2, regions=[(0, 0, 1, 1)], hours=3)
    assert len(sample) == 2


@pytest.mark.asyncio
async def test_fetch_random_sample_continues_when_region_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AviationWeatherClient()
    calls = {"n": 0}

    async def fake_fetch(_bbox, hours=None, format_type=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("bad region")
        return [{"rawOb": "OK"}]

    monkeypatch.setattr(client, "fetch_metars_by_bbox", fake_fetch)

    sample = await client.fetch_random_sample(count=10, regions=[(0, 0, 1, 1), (1, 1, 2, 2)])
    assert sample == [{"rawOb": "OK"}]


@pytest.mark.asyncio
async def test_fetch_random_sample_uses_default_regions_and_returns_all(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AviationWeatherClient()
    seen_regions = []

    async def fake_fetch(bbox, hours=None, format_type=None):
        seen_regions.append((bbox, hours, format_type))
        return [{"rawOb": f"{bbox[0]}"}]

    monkeypatch.setattr(client, "fetch_metars_by_bbox", fake_fetch)

    sample = await client.fetch_random_sample(count=10, regions=None, hours=4)

    assert len(seen_regions) == 5
    assert all(hours == 4 and format_type == "json" for _bbox, hours, format_type in seen_regions)
    assert len(sample) == 5


def test_sync_wrappers_use_asyncio_run(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AviationWeatherClient()

    async def fake_bbox(self, bbox, hours, format_type):
        return [{"bbox": bbox, "hours": hours, "format": format_type}]

    async def fake_sample(self, count, regions, hours):
        return [{"count": count, "hours": hours, "regions": regions}]

    monkeypatch.setattr(AviationWeatherClient, "fetch_metars_by_bbox", fake_bbox)
    monkeypatch.setattr(AviationWeatherClient, "fetch_random_sample", fake_sample)

    bbox_result = client.fetch_metars_by_bbox_sync((0, 0, 1, 1), hours=4, format_type="json")
    sample_result = client.fetch_random_sample_sync(count=5, regions=[(0, 0, 1, 1)], hours=6)

    assert bbox_result[0]["hours"] == 4
    assert sample_result[0]["count"] == 5


def test_cached_client_key_path_and_cache_validity(tmp_path: Path) -> None:
    client = CachedAviationWeatherClient(cache_dir=tmp_path, ttl=10)

    key = client._cache_key("bbox", (1, 2, 3, 4), 2, "json")
    path = client._get_cache_path(key)

    assert len(key) == 32
    assert path == tmp_path / f"{key}.json"

    assert client._is_cache_valid(path) is False

    path.write_text("[]", encoding="utf-8")
    assert client._is_cache_valid(path) is True

    stale_time = (datetime.now() - timedelta(seconds=100)).timestamp()
    os.utime(path, (stale_time, stale_time))
    assert client._is_cache_valid(path) is False


@pytest.mark.asyncio
async def test_cached_fetch_uses_cache_and_writes_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    client = CachedAviationWeatherClient(cache_dir=tmp_path, ttl=3600)

    async def fake_super_bbox(self, bbox, hours, format_type):
        return [{"bbox": list(bbox), "hours": hours, "format": format_type}]

    async def fake_super_sample(self, count, regions, hours):
        return [{"count": count, "hours": hours, "regions": regions or []}]

    monkeypatch.setattr(AviationWeatherClient, "fetch_metars_by_bbox", fake_super_bbox)
    monkeypatch.setattr(AviationWeatherClient, "fetch_random_sample", fake_super_sample)

    first_bbox = await client.fetch_metars_by_bbox((1, 2, 3, 4), hours=2, format_type="json")
    first_sample = await client.fetch_random_sample(count=3, regions=[(0, 0, 1, 1)], hours=2)

    assert first_bbox[0]["hours"] == 2
    assert first_sample[0]["count"] == 3

    # Cache hit path should load persisted JSON and not call parent methods.
    monkeypatch.setattr(
        AviationWeatherClient, "fetch_metars_by_bbox", AsyncMock(side_effect=AssertionError("should not call"))
    )
    monkeypatch.setattr(
        AviationWeatherClient, "fetch_random_sample", AsyncMock(side_effect=AssertionError("should not call"))
    )

    second_bbox = await client.fetch_metars_by_bbox((1, 2, 3, 4), hours=2, format_type="json")
    second_sample = await client.fetch_random_sample(count=3, regions=[(0, 0, 1, 1)], hours=2)

    assert second_bbox == first_bbox
    assert second_sample[0]["count"] == first_sample[0]["count"]
    assert second_sample[0]["hours"] == first_sample[0]["hours"]


def test_cached_sync_wrappers(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    client = CachedAviationWeatherClient(cache_dir=tmp_path, ttl=3600)

    async def fake_bbox(self, bbox, hours, format_type):
        return [{"bbox": bbox, "hours": hours, "format": format_type}]

    async def fake_sample(self, count, regions, hours):
        return [{"count": count, "regions": regions, "hours": hours}]

    monkeypatch.setattr(CachedAviationWeatherClient, "fetch_metars_by_bbox", fake_bbox)
    monkeypatch.setattr(CachedAviationWeatherClient, "fetch_random_sample", fake_sample)

    assert client.fetch_metars_by_bbox_sync((0, 0, 1, 1), hours=2, format_type="json")[0]["format"] == "json"
    assert client.fetch_random_sample_sync(count=4, regions=[(1, 1, 2, 2)], hours=5)[0]["count"] == 4
