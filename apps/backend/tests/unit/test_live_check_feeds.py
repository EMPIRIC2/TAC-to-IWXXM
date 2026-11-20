"""Unit tests for live-check feed fetcher (no network).

[Corpus: product §F6] [Corpus: tests §TC-LIVE-FEEDS] [Corpus: api]
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from dissemination.allowlist import EgressDenied
from live_check_test_support import (
    ALLOW as _ALLOW,
)
from live_check_test_support import (
    FakeResponse as _FakeResponse,
)
from src.services.live_check import LiveCheckError, set_live_check_service
from src.services.live_check_feeds import FeedFetcher


def test_noaa_missing_station_and_http_error() -> None:
    def http_get(url: str, *, params=None, headers=None):
        if (params or {}).get("format") == "raw":
            return _FakeResponse("EGLL 231751Z 18012KT=")
        return _FakeResponse("", status_code=500)

    fetcher = FeedFetcher(http_get=http_get, allowlist=_ALLOW)  # type: ignore[arg-type]
    with pytest.raises(LiveCheckError, match="noaa returned no") as exc:
        fetcher.fetch("noaa", "KJFK", "METAR")
    assert exc.value.status_code == 404


def test_met_no_missing_station() -> None:
    fetcher = FeedFetcher(
        http_get=lambda *_a, **_k: _FakeResponse("EGLL 231520Z CAVOK="),  # type: ignore[arg-type,return-value]
        allowlist=_ALLOW,
    )
    with pytest.raises(LiveCheckError, match="met_no returned no") as exc:
        fetcher.fetch("met_no", "ENGM", "METAR")
    assert exc.value.status_code == 404


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
    ("payload", "detail"),
    [
        ({"files": []}, "empty"),
        ({"files": [{"filename": ""}]}, "filename"),
        ({"files": [{"filename": "x.txt"}]}, "download URL"),
    ],
)
def test_knmi_listing_failures(payload: dict[str, object], detail: str) -> None:
    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return _FakeResponse(json_payload=payload)
        if url.endswith("/url"):
            return _FakeResponse(json_payload={})
        return _FakeResponse("")

    fetcher = FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    with pytest.raises(LiveCheckError, match=detail) as exc:
        fetcher.fetch("knmi", "EHRD", "METAR")
    assert exc.value.status_code in {404, 502}


def test_knmi_download_host_rejected() -> None:
    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return _FakeResponse(json_payload={"files": [{"filename": "m.txt"}]})
        if url.endswith("/url"):
            return _FakeResponse(json_payload={"temporaryDownloadUrl": "http://evil.example/m.txt"})
        return _FakeResponse("")

    fetcher = FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    with pytest.raises(LiveCheckError, match="download host") as exc:
        fetcher.fetch("knmi", "EHRD", "METAR")
    assert exc.value.status_code == 403


def test_knmi_station_not_in_file() -> None:
    body = (
        '<?xml version="1.0" ?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0">'
        "<!-- METAR EHAM 231555Z AUTO 27007KT -->"
        "</iwxxm:METAR>"
    )

    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return _FakeResponse(json_payload={"files": [{"filename": "m.txt"}]})
        if url.endswith("/url"):
            return _FakeResponse(json_payload={"temporaryDownloadUrl": "https://cdn.example.test/m.txt"})
        return _FakeResponse(body)

    fetcher = FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    with pytest.raises(LiveCheckError, match="no METAR") as exc:
        fetcher.fetch("knmi", "EHRD", "METAR")
    assert exc.value.status_code == 404


def test_get_text_http_error_and_missing_host() -> None:
    fetcher = FeedFetcher(
        http_get=lambda *_a, **_k: _FakeResponse("", status_code=503),  # type: ignore[arg-type,return-value]
        allowlist=_ALLOW,
    )
    with pytest.raises(LiveCheckError, match="feed request failed") as exc:
        fetcher._get_text("https://aviationweather.gov/api/data/metar")
    assert exc.value.status_code == 502
    with pytest.raises(LiveCheckError, match="missing host"):
        fetcher._assert_host("not-a-url")


def test_assert_host_rejects_egress_denied() -> None:
    from dissemination.allowlist import parse_allowlist

    fetcher = FeedFetcher(
        http_get=lambda *_a, **_k: _FakeResponse(""),  # type: ignore[arg-type,return-value]
        allowlist=parse_allowlist("api.met.no"),
    )
    with pytest.raises(LiveCheckError, match="not allowlisted") as exc:
        fetcher._assert_host("https://aviationweather.gov/api/data/metar")
    assert exc.value.status_code == 403


def test_knmi_suffix_download_allowlisted() -> None:
    body = (
        '<?xml version="1.0" ?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0">'
        "<!-- METAR EHRD 231555Z AUTO 27007KT -->"
        "</iwxxm:METAR>"
    )

    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return _FakeResponse(json_payload={"files": [{"filename": "m.txt"}]})
        if url.endswith("/url"):
            return _FakeResponse(json_payload={"temporaryDownloadUrl": "https://data.blob.core.windows.net/m.txt"})
        return _FakeResponse(body)

    fetcher = FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    tac, xml = fetcher.fetch("knmi", "EHRD", "METAR")
    assert "EHRD" in tac
    assert xml is not None


def test_get_json_non_object_and_http_error() -> None:
    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return _FakeResponse(json_payload=["not", "an", "object"])
        return _FakeResponse("", status_code=502)

    fetcher = FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    with pytest.raises(LiveCheckError, match="non-object") as exc:
        fetcher.fetch("knmi", "EHRD", "METAR")
    assert exc.value.status_code == 502


def test_knmi_download_http_scheme_denied() -> None:
    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return _FakeResponse(json_payload={"files": [{"filename": "m.txt"}]})
        if url.endswith("/url"):
            return _FakeResponse(json_payload={"temporaryDownloadUrl": "http://api.dataplatform.knmi.nl/m.txt"})
        return _FakeResponse("")

    fetcher = FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    with pytest.raises(LiveCheckError, match="download host") as exc:
        fetcher.fetch("knmi", "EHRD", "METAR")
    assert exc.value.status_code == 403


def test_knmi_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    body = (
        '<?xml version="1.0" ?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0">'
        "<!-- METAR EHRD 231555Z AUTO 27007KT -->"
        "</iwxxm:METAR>"
    )
    monkeypatch.setenv("KNMI_OPEN_DATA_API_KEY", "env-key")

    seen_auth: list[str] = []

    def http_get(url: str, *, params=None, headers=None):
        if headers and headers.get("Authorization"):
            seen_auth.append(str(headers["Authorization"]))
        if url.endswith("/files"):
            return _FakeResponse(json_payload={"files": [{"filename": "m.txt"}]})
        if url.endswith("/url"):
            return _FakeResponse(json_payload={"temporaryDownloadUrl": "https://cdn.example.test/m.txt"})
        return _FakeResponse(body)

    fetcher = FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key=None,
    )
    tac, _xml = fetcher.fetch("knmi", "EHRD", "METAR")
    assert "EHRD" in tac
    assert seen_auth == ["env-key", "env-key"]


def test_knmi_suffix_host_still_denied_on_egress(monkeypatch: pytest.MonkeyPatch) -> None:
    from dissemination.allowlist import EgressDenied
    from src.services import live_check_feeds as feeds

    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return _FakeResponse(json_payload={"files": [{"filename": "m.txt"}]})
        if url.endswith("/url"):
            return _FakeResponse(json_payload={"temporaryDownloadUrl": "https://data.blob.core.windows.net/m.txt"})
        return _FakeResponse("")

    def deny_blob_only(host: str, *, allowlist=None):
        if "blob.core.windows.net" in host:
            raise EgressDenied(host)

    monkeypatch.setattr(feeds, "validate_egress_host", deny_blob_only)
    fetcher = feeds.FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    with pytest.raises(LiveCheckError, match="download host denied") as exc:
        fetcher.fetch("knmi", "EHRD", "METAR")
    assert exc.value.status_code == 403


def test_knmi_non_suffix_download_host_rejected() -> None:
    def http_get(url: str, *, params=None, headers=None):
        if url.endswith("/files"):
            return _FakeResponse(json_payload={"files": [{"filename": "m.txt"}]})
        if url.endswith("/url"):
            return _FakeResponse(json_payload={"temporaryDownloadUrl": "https://evil.example/m.txt"})
        return _FakeResponse("")

    fetcher = FeedFetcher(
        http_get=http_get,  # type: ignore[arg-type]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    with pytest.raises(LiveCheckError, match="not allowlisted") as exc:
        fetcher.fetch("knmi", "EHRD", "METAR")
    assert exc.value.status_code == 403


def test_get_json_http_error() -> None:
    fetcher = FeedFetcher(
        http_get=lambda *_a, **_k: _FakeResponse("", status_code=503),  # type: ignore[arg-type,return-value]
        allowlist=_ALLOW,
        knmi_api_key="test-key",
    )
    with pytest.raises(LiveCheckError, match="feed request failed") as exc:
        fetcher.fetch("knmi", "EHRD", "METAR")
    assert exc.value.status_code == 502


def test_pacer_expires_old_hits() -> None:
    from src.services.live_check import _ProviderPacer

    pacer = _ProviderPacer()
    pacer.check("noaa", now=100.0)
    pacer.check("noaa", now=200.0)  # prior hit outside 60s window for default limits
