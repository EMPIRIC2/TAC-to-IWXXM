"""Tests for metar_shared.config_loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.config_loader import (
    config_path,
    get_config_env,
    get_supabase_url_from_config,
    load_config,
)


def test_get_config_env_defaults_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METAR_CONFIG_ENV", raising=False)
    assert get_config_env() == "local"


def test_get_config_env_respects_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METAR_CONFIG_ENV", "prod")
    assert get_config_env() == "prod"


def test_config_path_points_at_repo_config() -> None:
    path = config_path("prod")
    assert path.name == "prod.json"
    assert path.parent.name == "config"


def test_load_config_prod_has_supabase_url() -> None:
    cfg = load_config("prod")
    assert cfg["environment"] == "prod"
    assert "supabase" in cfg
    assert cfg["supabase"]["url"].startswith("https://")


def test_load_config_missing_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "config" / "missing.json"
    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT",
        tmp_path,
        raising=False,
    )
    (tmp_path / "config").mkdir()
    missing.write_text(json.dumps({"environment": "missing"}), encoding="utf-8")
    assert load_config("missing")["environment"] == "missing"


def test_get_supabase_url_from_config_prod() -> None:
    url = get_supabase_url_from_config("prod")
    assert url.startswith("https://")


def test_load_config_file_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT",
        tmp_path,
        raising=False,
    )
    with pytest.raises(FileNotFoundError):
        load_config("nope")
