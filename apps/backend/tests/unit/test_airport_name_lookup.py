"""Per-station OpenAIP name lookup. [Corpus: product §F3] [Corpus: product §F9]"""

from __future__ import annotations

import httpx
import pytest
from src.services.airport_name_lookup import (
    clear_airport_name_cache,
    lookup_airport_name,
)

_KJFK = {
    "items": [
        {"name": "SOME OTHER", "icaoCode": "KABC"},
        {"name": "  JOHN F KENNEDY INTL  ", "icaoCode": "kjfk"},
    ]
}


class _Response:
    def __init__(self, payload: object, status: int = 200) -> None:
        self._payload = payload
        self.status_code = status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://api.core.openaip.net/api/airports")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("lookup failed", request=request, response=response)

    def json(self) -> object:
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


@pytest.fixture(autouse=True)
def _clean_cache() -> None:
    clear_airport_name_cache()


def test_lookup_returns_exact_icao_name(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def _get(url: str, **kwargs: object) -> _Response:
        calls.append(url)
        assert kwargs["params"] == {"search": "KJFK", "limit": 10}
        headers = kwargs["headers"]
        assert isinstance(headers, dict)
        assert headers["x-openaip-api-key"] == "test-key"
        return _Response(_KJFK)

    monkeypatch.setenv("OPENAIP_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "get", _get)
    assert lookup_airport_name(" kjfk ") == "JOHN F KENNEDY INTL"
    assert lookup_airport_name("KJFK") == "JOHN F KENNEDY INTL"
    assert len(calls) == 1


def test_lookup_remembers_a_confirmed_miss(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    def _get(url: str, **kwargs: object) -> _Response:
        calls["n"] += 1
        return _Response({"items": [{"name": "Elsewhere", "icaoCode": "EGLL"}]})

    monkeypatch.setenv("OPENAIP_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "get", _get)
    assert lookup_airport_name("ZZ99") is None
    assert lookup_airport_name("ZZ99") is None
    assert calls["n"] == 1


def test_lookup_does_not_remember_a_failed_request(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    def _get(url: str, **kwargs: object) -> _Response:
        calls["n"] += 1
        return _Response({}, status=503)

    monkeypatch.setenv("OPENAIP_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "get", _get)
    assert lookup_airport_name("KJFK") is None
    assert lookup_airport_name("KJFK") is None
    assert calls["n"] == 2


def test_lookup_skips_without_a_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAIP_API_KEY", raising=False)

    def _get(url: str, **kwargs: object) -> _Response:
        raise AssertionError("must not call OpenAIP without a key")

    monkeypatch.setattr(httpx, "get", _get)
    assert lookup_airport_name("KJFK") is None


def test_lookup_rejects_a_non_station_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAIP_API_KEY", "test-key")
    assert lookup_airport_name("12") is None
    assert lookup_airport_name("1234") is None


def test_lookup_ignores_a_bad_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    payloads: list[object] = [
        ["not", "an", "object"],
        {"items": None},
        {"items": [{"icaoCode": 1, "name": "Nope"}]},
    ]

    def _get(url: str, **kwargs: object) -> _Response:
        return _Response(payloads.pop(0))

    monkeypatch.setenv("OPENAIP_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "get", _get)
    assert lookup_airport_name("KJFK") is None
    assert lookup_airport_name("EGLL") is None
    assert lookup_airport_name("YSSY") is None


def test_lookup_ignores_items_that_are_not_objects(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAIP_API_KEY", "test-key")

    def _get(url: str, **kwargs: object) -> _Response:
        return _Response({"items": ["KJFK", {"icaoCode": "KJFK", "name": "   "}]})

    monkeypatch.setattr(httpx, "get", _get)
    assert lookup_airport_name("KJFK") is None


def test_lookup_ignores_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAIP_API_KEY", "test-key")

    def _get(url: str, **kwargs: object) -> _Response:
        return _Response(ValueError("bad json"))

    monkeypatch.setattr(httpx, "get", _get)
    assert lookup_airport_name("KJFK") is None
