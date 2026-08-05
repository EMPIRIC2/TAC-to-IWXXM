"""Unit tests for live env var resolution."""

from __future__ import annotations

import pytest
from tests.live_env import (
    doks_provisional,
    expected_api_base_url,
    live_api_host_headers,
    live_api_url,
    live_frontend_fetch_base,
    live_frontend_host_headers,
    live_frontend_url,
)


@pytest.fixture(autouse=True)
def _clear_live_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Clear every name live_env._first_non_empty may read so developer .env /
    # shell exports cannot leak into precedence tests.
    for key in (
        "LIVE_API_URL",
        "LIVE_FRONTEND_URL",
        "STAGING_API_URL",
        "STAGING_FRONTEND_ORIGIN",
        "STAGING_FRONTEND_URL",
        "E2E_API_URL",
        "E2E_BACKEND_URL",
        "E2E_FRONTEND_URL",
        "VITE_API_BASE_URL",
        "PLAYWRIGHT_DOKS_PROVISIONAL",
        "DOKS_PROVISIONAL",
        "DOKS_LB_IP",
        "DOKS_API_HOST",
        "DOKS_FE_HOST",
    ):
        monkeypatch.delenv(key, raising=False)


def test_live_api_url_prefers_live_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIVE_API_URL", "https://api.example.com/")
    monkeypatch.setenv("STAGING_API_URL", "https://staging.example.com")
    assert live_api_url() == "https://api.example.com"


def test_live_api_url_falls_back_to_staging(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STAGING_API_URL", "https://staging.example.com/")
    assert live_api_url() == "https://staging.example.com"


def test_live_frontend_url_falls_back_to_e2e(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("E2E_FRONTEND_URL", "https://frontend.example.com")
    assert live_frontend_url() == "https://frontend.example.com"


def test_doks_provisional_host_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLAYWRIGHT_DOKS_PROVISIONAL", "1")
    monkeypatch.setenv("DOKS_LB_IP", "10.0.0.9")
    monkeypatch.setenv("DOKS_API_HOST", "api.example.local")
    monkeypatch.setenv("DOKS_FE_HOST", "app.example.local")
    monkeypatch.setenv("LIVE_FRONTEND_URL", "http://app.example.local")
    monkeypatch.setenv("VITE_API_BASE_URL", "http://api.example.local")

    assert doks_provisional() is True
    assert live_api_host_headers() == {"Host": "api.example.local"}
    assert live_frontend_host_headers() == {"Host": "app.example.local"}
    assert live_frontend_fetch_base() == "http://10.0.0.9"
    assert expected_api_base_url() == "http://api.example.local"


def test_non_provisional_skips_host_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIVE_FRONTEND_URL", "https://app.example.com")
    assert doks_provisional() is False
    assert live_api_host_headers() == {}
    assert live_frontend_host_headers() == {}
    assert live_frontend_fetch_base() == "https://app.example.com"
