"""Unit tests for live-check service and router (no network).

[Corpus: product §F6] [Corpus: tests §TC-LIVE-FEEDS] [Corpus: api]
"""

from __future__ import annotations

import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
from dissemination.allowlist import parse_allowlist
from live_check_test_support import (
    ALLOW as _ALLOW,
)
from live_check_test_support import (
    TAC as _TAC,
)
from live_check_test_support import (
    XML as _XML,
)
from live_check_test_support import (
    FakeResponse as _FakeResponse,
)
from live_check_test_support import (
    fail_convert as _fail_convert,
)
from live_check_test_support import (
    ok_convert as _ok_convert,
)
from src.services.live_check import (
    LiveCheckError,
    LiveCheckService,
    profile_for_icao,
    set_live_check_service,
)
from src.services.live_check_models import ensure_product_keyword


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


def test_rate_limit_trips(monkeypatch: pytest.MonkeyPatch) -> None:
    def http_get(url: str, *, params=None, headers=None):
        return _FakeResponse(_TAC)

    from src.services import live_check_models as models

    monkeypatch.setitem(models._PROVIDER_LIMITS, "noaa", (1, 60.0))
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
    from src.services.live_check_feeds import FeedFetcher

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
    response = FeedFetcher._default_http_get(
        "https://aviationweather.gov/api/data/metar",
        params={"ids": "KJFK"},
    )
    assert response.status_code == 200
    assert seen["url"] == "https://aviationweather.gov/api/data/metar"


@pytest.mark.parametrize(
    ("product", "provider", "detail"),
    [
        ("SIGMET", "noaa", "METAR or TAF"),
        ("TAF", "knmi", "METAR only"),
    ],
)
def test_product_provider_validation(product: str, provider: str, detail: str) -> None:
    svc = LiveCheckService(convert_fn=_ok_convert, allowlist=_ALLOW)
    with pytest.raises(LiveCheckError, match=detail) as exc:
        svc.check(icao="EHRD", product=product, provider=provider)
    assert exc.value.status_code == 400


def test_get_live_check_service_singleton() -> None:
    from src.services.live_check import get_live_check_service

    set_live_check_service(None)
    first = get_live_check_service()
    second = get_live_check_service()
    assert first is second


def test_convert_uses_tac2iwxxm_when_not_injected(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    calls: list[int] = []

    def fake_convert(*_args: object, **_kwargs: object) -> SimpleNamespace:
        calls.append(1)
        return _ok_convert()

    monkeypatch.setitem(sys.modules, "tac2iwxxm", SimpleNamespace(convert=fake_convert))
    svc = LiveCheckService(convert_fn=None, allowlist=_ALLOW)
    xml, ok, _issues = svc._convert(_TAC, "METAR", "iwxxm_us")
    assert ok is True
    assert xml == _XML
    assert calls


@pytest.mark.parametrize(
    ("text", "product", "expected_prefix"),
    [
        ("KJFK 231751Z 18012KT", "METAR", "METAR KJFK"),
        ("METAR KJFK 231751Z 18012KT", "METAR", "METAR KJFK"),
        ("EGLL 231520Z CAVOK", "TAF", "TAF EGLL"),
    ],
)
def test_ensure_product_keyword(text: str, product: str, expected_prefix: str) -> None:
    assert ensure_product_keyword(text, product).startswith(expected_prefix)


@pytest.mark.parametrize(
    ("provider", "product", "url_part", "tac"),
    [
        ("noaa", "TAF", "aviationweather.gov/api/data/taf", "TAF KJFK 231730Z 2318/2424 18010KT="),
        ("met_no", "TAF", "api.met.no/weatherapi/tafmetar/1.0/taf.txt", "TAF ENGM 2315/2415 20005KT="),
    ],
)
def test_taf_success_paths(
    provider: str,
    product: str,
    url_part: str,
    tac: str,
) -> None:
    calls: list[str] = []

    def http_get(url: str, *, params=None, headers=None):
        calls.append(url)
        return _FakeResponse(tac)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
    )
    icao = "KJFK" if provider == "noaa" else "ENGM"
    result = svc.check(icao=icao, product=product, provider=provider)
    assert result.product == "TAF"
    assert result.convert_ok is True
    assert result.source_tac
    assert any(url_part in u for u in calls)


def test_noaa_iwxxm_soft_fail_keeps_tac() -> None:
    def http_get(url: str, *, params=None, headers=None):
        if (params or {}).get("format") == "iwxxm":
            return _FakeResponse("", status_code=500)
        return _FakeResponse(_TAC)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
    )
    result = svc.check(icao="KJFK", product="METAR", provider="noaa")
    assert result.source_tac == _TAC
    assert result.provider_iwxxm is None
    assert result.convert_ok is True


def test_cache_expires_and_refetches() -> None:
    hits = {"n": 0}

    def http_get(url: str, *, params=None, headers=None):
        hits["n"] += 1
        return _FakeResponse(_TAC)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
        cache_ttl_sec=0.01,
    )
    first = svc.check(icao="KJFK", product="METAR", provider="noaa")
    time.sleep(0.02)
    second = svc.check(icao="KJFK", product="METAR", provider="noaa")
    assert first.cached is False
    assert second.cached is False
    assert hits["n"] == 4  # raw+iwxxm twice


def test_set_live_check_service_clears_singleton() -> None:
    from src.services.live_check import get_live_check_service

    set_live_check_service(LiveCheckService(convert_fn=_ok_convert, allowlist=_ALLOW))
    assert get_live_check_service() is not None
    set_live_check_service(None)
    again = get_live_check_service()
    assert isinstance(again, LiveCheckService)


def test_icao_whitespace_normalized() -> None:
    def http_get(url: str, *, params=None, headers=None):
        return _FakeResponse(_TAC)

    svc = LiveCheckService(
        http_get=http_get,  # type: ignore[arg-type]
        convert_fn=_ok_convert,
        allowlist=_ALLOW,
    )
    result = svc.check(icao=" kjfk ", product="metar", provider="NOAA")
    assert result.icao == "KJFK"
    assert result.product == "METAR"
    assert result.provider == "noaa"
