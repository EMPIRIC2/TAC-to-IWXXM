"""Lookup tests use a copied OurAirports fixture and never open the live host."""

from __future__ import annotations

import csv
import socket
from pathlib import Path

import httpx
import pytest
import reference_lookup.lookup as lookup_mod
import reference_lookup.pytest_plugin as plugin
from reference_lookup import SourceUnavailable, lookup_coordinate, set_coordinate_source
from reference_lookup.lookup import CsvCoordinateSource, LiveOurAirportsSource

FIXTURES = Path(__file__).resolve().parent / "fixtures"
NAVAIDS = (FIXTURES / "navaids.csv").read_text(encoding="utf-8")
AIRPORTS = (FIXTURES / "airports.csv").read_text(encoding="utf-8")


def _fixture_source() -> CsvCoordinateSource:
    return CsvCoordinateSource(NAVAIDS, AIRPORTS)


def test_fixture_resolves_srq_and_ksrq() -> None:
    source = _fixture_source()
    lat, lon = source.lookup("srq")
    assert lat == pytest.approx(27.39780044555664)
    assert lon == pytest.approx(-82.5542984008789)
    airport_lat, airport_lon = source.lookup("KSRQ")
    assert airport_lat == pytest.approx(27.394631)
    assert airport_lon == pytest.approx(-82.554359)


def test_ambiguous_ident_is_unavailable() -> None:
    source = _fixture_source()
    with pytest.raises(SourceUnavailable):
        source.lookup("AAL")


def test_missing_and_bad_shape_are_unavailable() -> None:
    source = _fixture_source()
    with pytest.raises(SourceUnavailable):
        source.lookup("ZZZ")
    with pytest.raises(SourceUnavailable):
        source.lookup("SR")
    with pytest.raises(SourceUnavailable):
        source.lookup("SRQ-")


def test_blank_ident_and_empty_coordinate_are_skipped() -> None:
    navaids = "ident,latitude_deg,longitude_deg\n,1,2\nEMP,,\n"
    airports = "ident,latitude_deg,longitude_deg\n"
    source = CsvCoordinateSource(navaids, airports)
    with pytest.raises(SourceUnavailable):
        source.lookup("EMP")


def test_bad_coordinate_and_missing_columns() -> None:
    with pytest.raises(SourceUnavailable):
        CsvCoordinateSource("ident,latitude_deg,longitude_deg\nABC,nope,1\n", "ident,latitude_deg,longitude_deg\n")
    with pytest.raises(SourceUnavailable):
        CsvCoordinateSource("name\n", "ident,latitude_deg,longitude_deg\n")


def test_pytest_default_does_not_download() -> None:
    set_coordinate_source(None)
    with pytest.raises(SourceUnavailable):
        lookup_coordinate("SRQ")


def test_injected_source_and_unexpected_error() -> None:
    set_coordinate_source(_fixture_source())
    try:
        assert lookup_coordinate("SRQ")[0] == pytest.approx(27.39780044555664)
    finally:
        set_coordinate_source(None)

    class Boom:
        def lookup(self, ident: str) -> tuple[float, float]:
            raise RuntimeError(ident)

    set_coordinate_source(Boom())
    try:
        with pytest.raises(SourceUnavailable):
            lookup_coordinate("SRQ")
    finally:
        set_coordinate_source(None)


def test_live_source_is_process_wide(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(lookup_mod, "_live", None)
    try:
        first = lookup_mod.live_source()
        assert lookup_mod.current_source() is first
        assert lookup_mod.live_source() is first
    finally:
        monkeypatch.setattr(lookup_mod, "_live", None)


def _response(url: str, status: int, text: str) -> httpx.Response:
    return httpx.Response(status, text=text, request=httpx.Request("GET", url))


def _handler(calls: list[str]) -> httpx.MockTransport:
    def respond(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if str(request.url).endswith("navaids.csv"):
            return httpx.Response(200, text=NAVAIDS)
        if str(request.url).endswith("airports.csv"):
            return httpx.Response(200, text=AIRPORTS)
        return httpx.Response(404, text="missing")

    return httpx.MockTransport(respond)


def test_live_download_is_cached() -> None:
    calls: list[str] = []
    client = httpx.Client(transport=_handler(calls))
    source = LiveOurAirportsSource(client)
    assert source.lookup("SRQ")[0] == pytest.approx(27.39780044555664)
    assert source.lookup("KSRQ")[0] == pytest.approx(27.394631)
    assert len(calls) == 2


def test_live_http_error_and_timeout() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="down")

    source = LiveOurAirportsSource(httpx.Client(transport=httpx.MockTransport(fail)))
    with pytest.raises(SourceUnavailable):
        source.lookup("SRQ")

    def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out")

    source = LiveOurAirportsSource(httpx.Client(transport=httpx.MockTransport(timeout)))
    with pytest.raises(SourceUnavailable):
        source.lookup("SRQ")


def test_default_client_downloads_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    class FakeClient:
        def __init__(self, timeout: float) -> None:
            assert timeout == lookup_mod.TIMEOUT_SECONDS

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *_args: object) -> bool:
            calls.append("closed")
            return False

        def get(self, url: str) -> httpx.Response:
            calls.append(url)
            if url.endswith("navaids.csv"):
                return _response(url, 200, NAVAIDS)
            return _response(url, 200, AIRPORTS)

    monkeypatch.setattr(lookup_mod.httpx, "Client", FakeClient)
    source = LiveOurAirportsSource()
    assert source.lookup("SRQ")[1] == pytest.approx(-82.5542984008789)
    assert calls[-1] == "closed"
    assert sum(1 for item in calls if item.endswith(".csv")) == 2


def test_read_wraps_csv_and_unicode_errors() -> None:
    class FakeClient:
        def get(self, url: str) -> httpx.Response:
            return _response(url, 200, "ident,latitude_deg,longitude_deg\n")

        def raise_for_status(self) -> None:
            return None

    def boom(*_args: object, **_kwargs: object) -> csv.DictReader:
        raise csv.Error("bad")

    original = lookup_mod.csv.DictReader
    lookup_mod.csv.DictReader = boom  # type: ignore[method-assign, assignment]
    try:
        with pytest.raises(SourceUnavailable):
            lookup_mod._read(FakeClient())  # type: ignore[arg-type]
    finally:
        lookup_mod.csv.DictReader = original  # type: ignore[method-assign]

    class BadText:
        def raise_for_status(self) -> None:
            return None

        @property
        def text(self) -> str:
            raise UnicodeError("bad")

    class BadClient:
        def get(self, url: str) -> BadText:
            return BadText()

    with pytest.raises(SourceUnavailable):
        lookup_mod._read(BadClient())  # type: ignore[arg-type]


def test_socket_guard_blocks_ourairports_and_allows_other_hosts(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(RuntimeError, match=r"unit test called davidmegginson\.github\.io"):
        socket.create_connection(("davidmegginson.github.io", 443))
    monkeypatch.setattr(plugin, "_original_create_connection", lambda *_args, **_kwargs: "ok")
    assert socket.create_connection(("example.com", 80)) == "ok"
    assert plugin._guarded_create_connection("example.com") == "ok"
