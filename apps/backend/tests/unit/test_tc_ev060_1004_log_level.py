"""TC-EV060-1004 / UJ-063: conversion log_level sets logger verbosity (#1004).

Spec: docs/test-plan.md TC-EV060-1004-001..002; [Corpus: product §F29]
[Corpus: api] [Corpus: tests].
"""

from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.observability import (
    _REQUEST_LOG_LEVEL,
    RequestLogLevelFilter,
    SecretRedactFilter,
    _reset_request_log_level,
    set_request_log_level,
)
from src.utilities.security import verify_supabase_token

TAC_SAMPLE = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="
FAKE_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.secret-token-value"


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _convert(client: TestClient, log_level: str, headers: dict[str, str] | None = None):
    return client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, TAC_SAMPLE),
            "product": (None, "METAR"),
            "log_level": (None, log_level),
        },
        headers=headers or {},
    )


def test_tc_ev060_1004_001_debug_emits_more_than_error(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="src.routers.conversion"):
        error_resp = _convert(client, "ERROR")
        assert error_resp.status_code == 200, error_resp.text[:400]
        error_records = [
            r for r in caplog.records if r.name.startswith("src.routers.conversion") and r.levelno >= logging.ERROR
        ]
        caplog.clear()
        debug_resp = _convert(client, "DEBUG")
        assert debug_resp.status_code == 200, debug_resp.text[:400]
        debug_records = [
            r for r in caplog.records if r.name.startswith("src.routers.conversion") and r.levelno <= logging.DEBUG
        ]
    assert len(debug_records) > len(error_records)


def test_tc_ev060_1004_002_debug_does_not_dump_secrets(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        response = _convert(
            client,
            "DEBUG",
            headers={"Authorization": f"Bearer {FAKE_JWT}"},
        )
    assert response.status_code == 200, response.text[:400]
    blob = caplog.text
    assert FAKE_JWT not in blob
    assert "secret-token-value" not in blob
    assert "Bearer eyJ" not in blob


def test_tc_ev060_1004_invalid_log_level_defaults_to_info() -> None:
    class _State:
        pass

    class _Request:
        state = _State()

    request = _Request()
    try:
        name = set_request_log_level(request, "NOPE")  # type: ignore[arg-type]
        assert name == "INFO"
    finally:
        _reset_request_log_level(request)  # type: ignore[arg-type]


def test_tc_ev060_1004_secret_redact_filter_strips_jwt() -> None:
    filt = SecretRedactFilter()
    record = logging.LogRecord(
        name="src.api",
        level=logging.DEBUG,
        pathname=__file__,
        lineno=1,
        msg=f"Authorization: Bearer {FAKE_JWT}",
        args=(),
        exc_info=None,
    )
    assert filt.filter(record) is True
    assert FAKE_JWT not in str(record.msg)
    assert "[REDACTED" in str(record.msg)


def test_tc_ev060_1004_secret_redact_filter_leaves_plain_messages() -> None:
    filt = SecretRedactFilter()
    record = logging.LogRecord(
        name="src.api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="plain convert message",
        args=(),
        exc_info=None,
    )
    assert filt.filter(record) is True
    assert record.msg == "plain convert message"


def test_tc_ev060_1004_secret_redact_filter_tolerates_getmessage_errors() -> None:
    filt = SecretRedactFilter()
    record = logging.LogRecord(
        name="src.api",
        level=logging.DEBUG,
        pathname=__file__,
        lineno=1,
        msg="ok",
        args=(),
        exc_info=None,
    )

    def _boom() -> str:
        raise RuntimeError("boom")

    record.getMessage = _boom  # type: ignore[method-assign]
    assert filt.filter(record) is True


def test_tc_ev060_1004_request_filter_drops_below_context_level() -> None:
    filt = RequestLogLevelFilter()
    info = logging.LogRecord(
        name="src.api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="info",
        args=(),
        exc_info=None,
    )
    error = logging.LogRecord(
        name="src.api",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="error",
        args=(),
        exc_info=None,
    )
    assert filt.filter(info) is True
    token = _REQUEST_LOG_LEVEL.set(logging.ERROR)
    try:
        assert filt.filter(info) is False
        assert filt.filter(error) is True
    finally:
        _REQUEST_LOG_LEVEL.reset(token)


def test_tc_ev060_1004_none_log_level_defaults_to_info() -> None:
    class _State:
        pass

    class _Request:
        state = _State()

    request = _Request()
    try:
        assert set_request_log_level(request, None) == "INFO"  # type: ignore[arg-type]
    finally:
        _reset_request_log_level(request)  # type: ignore[arg-type]
