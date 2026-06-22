"""Unit tests for live fixture helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from tests.live_fixtures import login_with_backoff, obtain_live_api_token, wake_live_api


def test_wake_live_api_returns_on_first_200(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIVE_API_URL", "https://api.example.com")
    response = MagicMock()
    response.status_code = 200
    with patch("tests.live_fixtures.httpx.get", return_value=response) as mock_get:
        url = wake_live_api()
    assert url == "https://api.example.com"
    mock_get.assert_called_once()


def test_login_with_backoff_extracts_session_token() -> None:
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"session": {"access_token": "jwt-token"}}
    with patch("tests.live_fixtures.httpx.post", return_value=response):
        token = login_with_backoff("https://api.example.com", "a@b.com", "secret")
    assert token == "jwt-token"


def test_obtain_live_api_token_skips_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LIVE_API_URL", "https://api.example.com")
    monkeypatch.delenv("ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    response = MagicMock()
    response.status_code = 200
    with (
        patch("tests.live_fixtures.httpx.get", return_value=response),
        pytest.raises(pytest.skip.Exception),
    ):
        obtain_live_api_token()


def test_obtain_live_api_token_returns_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIVE_API_URL", "https://api.example.com")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "secret")

    health = MagicMock()
    health.status_code = 200
    login = MagicMock()
    login.status_code = 200
    login.json.return_value = {"access_token": "live-jwt"}

    with (
        patch("tests.live_fixtures.httpx.get", return_value=health),
        patch("tests.live_fixtures.httpx.post", return_value=login),
    ):
        assert obtain_live_api_token() == "live-jwt"
