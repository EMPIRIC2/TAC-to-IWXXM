"""Unit tests for API CORS helper configuration functions."""

from __future__ import annotations

import metar_shared.config_loader as config_loader
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


def test_get_cors_origins_from_config_and_relaxation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)

    origins = api_module.get_cors_origins()

    assert "http://localhost:18000" in origins
    assert "http://127.0.0.1:18000" in origins
    assert "http://localhost:5173" in origins


def test_get_cors_origins_defaults_use_config_frontend_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "false")

    origins = api_module.get_cors_origins()

    assert "http://localhost:18000" in origins


def test_get_cors_origins_defaults_with_relaxation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")

    origins = api_module.get_cors_origins()

    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins


def test_get_cors_origins_warns_when_deprecated_env_conflicts_with_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("METAR_CORS_ORIGINS", "http://ignored.example")
    monkeypatch.setattr(
        config_loader,
        "get_cors_origins_from_config",
        lambda env=None: ["http://from-config.example"],
    )

    with pytest.warns(DeprecationWarning, match="ignored when config"):
        origins = api_module.get_cors_origins()

    assert "http://from-config.example" in origins
    assert "http://ignored.example" not in origins


def test_get_cors_origins_uses_deprecated_env_when_config_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("METAR_CORS_ORIGINS", "http://legacy.example,http://legacy2.example")
    monkeypatch.setattr(config_loader, "get_cors_origins_from_config", lambda env=None: [])

    with pytest.warns(DeprecationWarning, match="deprecated"):
        origins = api_module.get_cors_origins()

    assert "http://legacy.example" in origins
    assert "http://legacy2.example" in origins


def test_get_cors_origins_falls_back_to_localhost_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.delenv("FRONTEND_URL", raising=False)
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "false")
    monkeypatch.setattr(config_loader, "get_cors_origins_from_config", lambda env=None: [])
    monkeypatch.setattr(config_loader, "get_frontend_url_from_config", lambda env=None: "")

    origins = api_module.get_cors_origins()

    assert "http://localhost:18000" in origins
    assert "http://localhost:3000" in origins


def test_get_cors_origins_uses_config_frontend_url_when_cors_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.delenv("FRONTEND_URL", raising=False)
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "false")
    monkeypatch.setattr(config_loader, "get_cors_origins_from_config", lambda env=None: [])
    monkeypatch.setattr(
        config_loader,
        "get_frontend_url_from_config",
        lambda env=None: "http://frontend-config.example",
    )

    origins = api_module.get_cors_origins()

    assert "http://frontend-config.example" in origins


def test_get_cors_origins_prefers_frontend_url_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("FRONTEND_URL", "http://frontend-env.example")
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "false")
    monkeypatch.setattr(config_loader, "get_cors_origins_from_config", lambda env=None: [])
    monkeypatch.setattr(config_loader, "get_frontend_url_from_config", lambda env=None: "")

    origins = api_module.get_cors_origins()

    assert "http://frontend-env.example" in origins


def test_get_cors_allowed_headers_strict_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "false")

    assert api_module.get_cors_allowed_headers() == ["Authorization", "Content-Type"]


def test_get_cors_allowed_headers_relaxed_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")

    assert api_module.get_cors_allowed_headers() == ["*"]
