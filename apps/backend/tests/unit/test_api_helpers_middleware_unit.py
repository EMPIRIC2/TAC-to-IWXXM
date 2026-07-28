"""Unit tests for API helper functions and middleware behavior."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from src import api as api_module


class _FakeUploadFile:
    def __init__(self, payload: bytes, filename: str | None = None):
        self._payload = payload
        self.filename = filename

    async def read(self, _size: int) -> bytes:
        return self._payload


@pytest.mark.parametrize(
    "manual_text,expected",
    [
        ("", []),
        ("  ", []),
        ("METAR A", ["METAR A"]),
        ("METAR A\n\n METAR B ", ["METAR A", "METAR B"]),
    ],
)
def test_split_manual_entries_cases(manual_text: str, expected: list[str]) -> None:
    assert api_module.split_manual_entries(manual_text) == expected


@pytest.mark.parametrize(
    "value,max_length,expected",
    [
        (None, 4, None),
        ("", 4, None),
        ("   ", 4, None),
        (" kjfk ", 4, "KJFK"),
        ("abcdef", 4, "ABCD"),
    ],
)
def test_normalize_code_cases(value: str | None, max_length: int, expected: str | None) -> None:
    assert api_module.normalize_code(value, max_length) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, "basic"),
        ("schema", "schema"),
        ("SCHEMATRON", "schematron"),
        ("icao-opmet", "icao_opmet"),
        ("invalid", "basic"),
    ],
)
def test_normalize_validation_level_cases(value: str | None, expected: str) -> None:
    assert api_module.normalize_validation_level(value) == expected


@pytest.mark.parametrize(
    "filename,content,expected",
    [
        ("sample.xml", "text", True),
        ("SAMPLE.XML", "text", True),
        ("sample.xml.txt", "text", False),
        (None, "   <root/>", True),
        ("sample.txt", "plain", False),
    ],
)
def test_is_xml_input_cases(filename: str | None, content: str, expected: bool) -> None:
    assert api_module.is_xml_input(filename, content) is expected


@pytest.mark.asyncio
async def test_read_uploaded_text_cases() -> None:
    import gzip

    content, error = await api_module.read_uploaded_text(_FakeUploadFile(b"METAR KJFK"))
    assert content == "METAR KJFK"
    assert error is None

    content, error = await api_module.read_uploaded_text(_FakeUploadFile(b""))
    assert content is None
    assert error == "empty file"

    too_big = b"x" * ((10 * 1024 * 1024) + 1)
    content, error = await api_module.read_uploaded_text(_FakeUploadFile(too_big))
    assert content is None
    assert "file too large" in error

    content, error = await api_module.read_uploaded_text(_FakeUploadFile(b"\xff\xfe"))
    assert content is None
    assert "UTF-8" in error

    content, error = await api_module.read_uploaded_text(_FakeUploadFile(b"   \n\t  "))
    assert content is None
    assert error == "empty file"

    # Valid small gzip of TAC text
    gz_ok = gzip.compress(b"METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=")
    content, error = await api_module.read_uploaded_text(_FakeUploadFile(gz_ok, filename="metar.txt.gz"))
    assert error is None
    assert content is not None and content.startswith("METAR KJFK")

    # High-ratio bomb: tiny gzip that expands past 10 MiB → reject via max_length
    bomb = gzip.compress(b"A" * (11 * 1024 * 1024), compresslevel=9)
    assert len(bomb) < 10 * 1024 * 1024
    content, error = await api_module.read_uploaded_text(_FakeUploadFile(bomb, filename="bomb.gz"))
    assert content is None
    assert error is not None and "decompressed file too large" in error


@pytest.mark.asyncio
async def test_read_uploaded_text_corrupt_gzip() -> None:
    content, error = await api_module.read_uploaded_text(_FakeUploadFile(b"\x1f\x8bCorruptNotGzip", filename="bad.gz"))
    assert content is None
    assert error is not None and "gzip decompress failed" in error


def test_manual_entries_with_offsets_crlf() -> None:
    pairs = api_module.manual_entries_with_offsets("METAR AA\r\nMETAR BB\r\n")
    assert [e for e, _ in pairs] == ["METAR AA", "METAR BB"]
    assert pairs[0][1] == 0
    assert pairs[1][1] == len("METAR AA\r\n")


@pytest.mark.asyncio
async def test_convert_request_logging_middleware_passthrough_paths() -> None:
    calls = {"count": 0}

    async def fake_app(scope, _receive, send):
        calls["count"] += 1
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = api_module.ConvertRequestLoggingMiddleware(fake_app)

    sent = []

    async def fake_send(message):
        sent.append(message)

    async def fake_receive():
        return {"type": "http.request"}

    # Non-http scope branch.
    await middleware({"type": "websocket"}, fake_receive, fake_send)

    # HTTP scope but non-convert path branch.
    await middleware({"type": "http", "path": "/health", "method": "GET", "headers": []}, fake_receive, fake_send)

    # /api/v1/convert path branch.
    await middleware(
        {"type": "http", "path": "/api/v1/convert", "method": "OPTIONS", "headers": []}, fake_receive, fake_send
    )

    assert calls["count"] == 3
    assert any(msg.get("type") == "http.response.start" for msg in sent)


def test_add_translation_centre_headers_and_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    def ok_info() -> dict[str, str]:
        return {
            "translationCentreDesignator": "NOAA-MDL",
            "translationCentreName": "NOAA Centre",
            "icaoLocationIndicator": "KWBC",
        }

    monkeypatch.setattr(api_module, "get_translation_centre_info", ok_info)
    client = TestClient(api_module.app)
    response = client.get("/health")

    assert response.headers["x-translation-centre"] == "NOAA-MDL"
    assert response.headers["x-translation-centre-name"] == "NOAA Centre"
    assert response.headers["x-icao-location-indicator"] == "KWBC"

    def failing_info() -> dict[str, str]:
        raise RuntimeError("no centre configured")

    monkeypatch.setattr(api_module, "get_translation_centre_info", failing_info)
    response2 = client.get("/health")
    assert response2.status_code == 200


def test_custom_openapi_caches_schema() -> None:
    previous = api_module.app.openapi_schema
    try:
        api_module.app.openapi_schema = None
        first = api_module.custom_openapi()
        second = api_module.custom_openapi()

        assert first is second
        assert not first.get("components", {}).get("securitySchemes")
    finally:
        api_module.app.openapi_schema = previous


def test_health_degraded_when_converter_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_convert(*_args: Any, **_kwargs: Any):
        raise RuntimeError("converter unavailable")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_convert)

    response = api_module.health()

    assert response.status == "degraded"
    assert response.tac2iwxxm_available is False
