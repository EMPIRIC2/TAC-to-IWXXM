"""Unit tests for live-check API — no network.

[Corpus: product §F6] [Corpus: tests §TC-LIVE-FEEDS] [Corpus: api]
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from dissemination.allowlist import parse_allowlist
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.routers import live_check as live_check_router
from src.services.live_check import (
    LiveCheckError,
    LiveCheckService,
    profile_for_icao,
    set_live_check_service,
)

_ALLOW = parse_allowlist("aviationweather.gov,api.met.no,api.dataplatform.knmi.nl,cdn.example.test")

_TAC = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
_XML = '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'


def _ok_convert(*_a: Any, **_k: Any) -> SimpleNamespace:
    return SimpleNamespace(ok=True, xml=_XML, issues=())


def _fail_convert(*_a: Any, **_k: Any) -> SimpleNamespace:
    issue = SimpleNamespace(code="PARSE", message="bad group")
    return SimpleNamespace(ok=False, xml=None, issues=(issue,))


class _FakeResponse:
    def __init__(
        self,
        text: str = "",
        *,
        status_code: int = 200,
        json_payload: object | None = None,
    ) -> None:
        self.text = text
        self.status_code = status_code
        self._json_payload = json_payload

    def json(self) -> object:
        if self._json_payload is None:
            raise ValueError("no json")
        return self._json_payload


@pytest.fixture(autouse=True)
def _clear_service() -> None:
    set_live_check_service(None)
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        yield
    set_live_check_service(None)


@pytest.mark.parametrize(
    ("icao", "expected"),
    [
        ("KJFK", "iwxxm_us"),
        ("CYYZ", "ca_eccc"),
        ("EGLL", "annex3"),
        ("EHRD", "annex3"),
    ],
)
def test_profile_for_icao(icao: str, expected: str) -> None:
    assert profile_for_icao(icao) == expected


@pytest.mark.parametrize(
    ("provider", "detail_part"),
    [
        ("sadis", "not allowlisted"),
        ("aviation.met.no", "not allowlisted"),
        ("avwx", "not allowlisted"),
    ],
)
def test_disallowed_provider_rejected(provider: str, detail_part: str) -> None:
    svc = LiveCheckService(
        http_get=lambda *_a, **_k: _FakeResponse(),  # type: ignore[arg-type,return-value]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
    )
    with pytest.raises(LiveCheckError, match=detail_part) as exc:
        svc.check(icao="KJFK", product="METAR", provider=provider)
    assert exc.value.status_code == 400


def test_invalid_icao_rejected() -> None:
    svc = LiveCheckService(convert_fn=_ok_convert, allowlist=_ALLOW)
    with pytest.raises(LiveCheckError, match="four-letter") as exc:
        svc.check(icao="JFK", product="METAR", provider="noaa")
    assert exc.value.status_code == 400


def test_noaa_success_with_provider_iwxxm() -> None:
    calls: list[str] = []

    def http_get(url: str, *, params: dict[str, str] | None = None, headers=None):
        calls.append(url)
        fmt = (params or {}).get("format", "raw")
        if fmt == "iwxxm":
            return _FakeResponse(_XML)
        return _FakeResponse(_TAC)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
    )
    result = svc.check(icao="KJFK", product="METAR", provider="noaa")
    assert result.profile == "iwxxm_us"
    assert result.source_tac == _TAC
    assert result.our_iwxxm == _XML
    assert result.provider_iwxxm == _XML
    assert result.convert_ok is True
    assert result.cached is False
    assert result.attribution is not None
    assert "NOAA" in result.attribution
    assert all("aviationweather.gov" in u for u in calls)


def test_met_no_attribution_and_tac_only() -> None:
    def http_get(url: str, *, params=None, headers=None):
        assert "api.met.no" in url
        return _FakeResponse("ENGM 231520Z 20003KT CAVOK=")

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
    )
    result = svc.check(icao="ENGM", product="METAR", provider="met_no")
    assert result.profile == "annex3"
    assert result.provider_iwxxm is None
    assert result.attribution is not None
    assert "CC BY" in result.attribution
    assert "MET Norway" in result.attribution


def test_knmi_pair_and_attribution() -> None:
    body = (
        '<?xml version="1.0" ?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0">'
        "<!-- METAR EHRD 231555Z AUTO 27007KT 9999 NSC 19/14 Q1020 -->"
        "</iwxxm:METAR>"
    )
    responses = {
        "list": _FakeResponse(json_payload={"files": [{"filename": "metar_latest.txt"}]}),
        "url": _FakeResponse(json_payload={"temporaryDownloadUrl": "https://cdn.example.test/metar_latest.txt"}),
        "dl": _FakeResponse(body),
    }

    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return responses["list"]
        if url.endswith("/url"):
            return responses["url"]
        return responses["dl"]

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
        knmi_api_key="test-key-not-real",
    )
    result = svc.check(icao="EHRD", product="METAR", provider="knmi")
    assert result.source_tac.startswith("METAR EHRD")
    assert result.provider_iwxxm is not None
    assert "iwxxm:METAR" in result.provider_iwxxm
    assert result.attribution is not None
    assert "KNMI" in result.attribution
    assert "CC BY" in result.attribution


def test_knmi_missing_key_is_503() -> None:
    svc = LiveCheckService(
        http_get=lambda *_a, **_k: _FakeResponse(),  # type: ignore[arg-type,return-value]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
        knmi_api_key="",
    )
    with pytest.raises(LiveCheckError, match="not configured") as exc:
        svc.check(icao="EHRD", product="METAR", provider="knmi")
    assert exc.value.status_code == 503


def test_ssrf_blocks_non_allowlisted_host() -> None:
    def http_get(url: str, *, params=None, headers=None):
        return _FakeResponse(_TAC)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=parse_allowlist("api.met.no"),  # noaa host missing
    )
    with pytest.raises(LiveCheckError, match="not allowlisted") as exc:
        svc.check(icao="KJFK", product="METAR", provider="noaa")
    assert exc.value.status_code == 403


def test_cache_avoids_second_fetch() -> None:
    hits = {"n": 0}

    def http_get(url: str, *, params=None, headers=None):
        hits["n"] += 1
        return _FakeResponse(_TAC)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
        cache_ttl_sec=60.0,
    )
    first = svc.check(icao="KJFK", product="METAR", provider="noaa")
    second = svc.check(icao="KJFK", product="METAR", provider="noaa")
    assert first.cached is False
    assert second.cached is True
    assert hits["n"] == 2  # raw + iwxxm once


def test_convert_failure_still_returns_source() -> None:
    def http_get(url: str, *, params=None, headers=None):
        return _FakeResponse(_TAC)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_fail_convert,
        allowlist=_ALLOW,
    )
    result = svc.check(icao="KJFK", product="METAR", provider="noaa")
    assert result.convert_ok is False
    assert result.our_iwxxm is None
    assert result.source_tac == _TAC
    assert any("PARSE" in m for m in result.convert_issues)


def test_router_success_and_failure() -> None:
    def http_get(url: str, *, params=None, headers=None):
        return _FakeResponse(_TAC)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
    )
    set_live_check_service(svc)
    app = FastAPI()
    app.include_router(live_check_router.router)
    client = TestClient(app)

    ok = client.get("/api/v1/live-check", params={"icao": "KJFK", "provider": "noaa"})
    assert ok.status_code == 200
    body = ok.json()
    assert body["icao"] == "KJFK"
    assert body["profile"] == "iwxxm_us"
    assert body["source_tac"] == _TAC
    assert body["our_iwxxm"] == _XML

    bad = client.get(
        "/api/v1/live-check",
        params={"icao": "KJFK", "provider": "sadis"},
    )
    assert bad.status_code == 400
    assert "allowlisted" in bad.json()["detail"]


def test_rate_limit_trips(monkeypatch: pytest.MonkeyPatch) -> None:
    def http_get(url: str, *, params=None, headers=None):
        return _FakeResponse(_TAC)

    from src.services import live_check as mod

    monkeypatch.setitem(mod._PROVIDER_LIMITS, "noaa", (1, 60.0))
    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
        cache_ttl_sec=0.0,
    )
    svc.check(icao="KJFK", product="METAR", provider="noaa")
    with pytest.raises(LiveCheckError, match="rate limit") as exc:
        svc.check(icao="KJFK", product="METAR", provider="noaa")
    assert exc.value.status_code == 429


def test_default_http_get_uses_httpx(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    class _Client:
        def __init__(self, *args: object, **kwargs: object) -> None:
            seen["kwargs"] = kwargs

        def __enter__(self) -> _Client:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def get(self, url: str, **kwargs: object) -> httpx.Response:
            seen["url"] = url
            return httpx.Response(200, text="ok", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "Client", _Client)
    response = LiveCheckService._default_http_get(
        "https://aviationweather.gov/api/data/metar",
        params={"ids": "KJFK"},
    )
    assert response.status_code == 200
    assert seen["url"] == "https://aviationweather.gov/api/data/metar"
