"""Unit tests for API CORS helper configuration functions."""

from __future__ import annotations

import pytest

from src import api as api_module


@pytest.mark.parametrize("value", ["true", "1", "yes", "on", "TRUE", "Yes"])
def test_is_dev_cors_relaxation_enabled_true_variants(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", value)

    assert api_module.is_dev_cors_relaxation_enabled() is True


@pytest.mark.parametrize("value", ["false", "0", "", "off", "no"])
def test_is_dev_cors_relaxation_enabled_false_variants(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", value)

    assert api_module.is_dev_cors_relaxation_enabled() is False


def test_add_loopback_origin_variants_adds_missing_pairs() -> None:
    origins = ["http://localhost:8000", "http://127.0.0.1:3000"]

    expanded = api_module.add_loopback_origin_variants(origins)

    assert "http://127.0.0.1:8000" in expanded
    assert "http://localhost:3000" in expanded


def test_add_loopback_origin_variants_does_not_duplicate() -> None:
    origins = ["http://localhost:8000", "http://127.0.0.1:8000"]

    expanded = api_module.add_loopback_origin_variants(origins)

    assert expanded.count("http://localhost:8000") == 1
    assert expanded.count("http://127.0.0.1:8000") == 1


def test_get_cors_origins_from_env_and_relaxation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METAR_CORS_ORIGINS", "https://prod.example.com, http://localhost:5173")
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")

    origins = api_module.get_cors_origins()

    assert "https://prod.example.com" in origins
    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins


def test_get_cors_origins_defaults_use_frontend_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("FRONTEND_URL", "https://frontend.example.com")
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "false")

    origins = api_module.get_cors_origins()

    assert "https://frontend.example.com" in origins
    assert "http://localhost:3000" in origins


def test_get_cors_origins_defaults_with_relaxation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:8000")
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")

    origins = api_module.get_cors_origins()

    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins
