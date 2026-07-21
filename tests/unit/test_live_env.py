"""Unit tests for live env var resolution."""

from __future__ import annotations

import pytest
from tests.live_env import live_api_url, live_frontend_url


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
