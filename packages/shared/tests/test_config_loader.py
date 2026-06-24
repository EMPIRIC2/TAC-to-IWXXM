"""Tests for metar_shared.config_loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.config_loader import (
    config_path,
    get_config_env,
    get_cors_origins_from_config,
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
    from metar_shared.config_loader import get_supabase_url_from_config

    url = get_supabase_url_from_config("prod")
    assert url.startswith("https://")


def test_get_cors_origins_from_config_local() -> None:
    origins = get_cors_origins_from_config("local")
    assert "http://localhost:18000" in origins


def test_get_frontend_url_from_config_prod() -> None:
    from metar_shared.config_loader import get_frontend_url_from_config

    url = get_frontend_url_from_config("prod")
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


def _write_config(tmp_path: Path, profile: str, payload: object) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / f"{profile}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_get_supabase_url_from_config_handles_missing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from metar_shared.config_loader import get_supabase_url_from_config

    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT", tmp_path, raising=False
    )
    assert get_supabase_url_from_config("missing") == ""


def test_get_supabase_url_from_config_handles_invalid_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from metar_shared.config_loader import get_supabase_url_from_config

    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT", tmp_path, raising=False
    )
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "broken.json").write_text("{not-json", encoding="utf-8")
    assert get_supabase_url_from_config("broken") == ""


def test_get_supabase_url_from_config_rejects_non_object_supabase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from metar_shared.config_loader import get_supabase_url_from_config

    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT", tmp_path, raising=False
    )
    _write_config(tmp_path, "bad", {"supabase": "not-a-dict"})
    assert get_supabase_url_from_config("bad") == ""


def test_get_cors_origins_from_config_rejects_non_object_api(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT", tmp_path, raising=False
    )
    _write_config(tmp_path, "bad", {"api": []})
    assert get_cors_origins_from_config("bad") == []


def test_get_cors_origins_from_config_rejects_non_list_cors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT", tmp_path, raising=False
    )
    _write_config(tmp_path, "bad", {"api": {"corsOrigins": "not-a-list"}})
    assert get_cors_origins_from_config("bad") == []


def test_get_cors_origins_from_config_filters_blank_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT", tmp_path, raising=False
    )
    _write_config(
        tmp_path,
        "local",
        {"api": {"corsOrigins": ["http://localhost:18000", "", "  "]}},
    )
    assert get_cors_origins_from_config("local") == ["http://localhost:18000"]


def test_get_frontend_url_from_config_rejects_non_object_api(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from metar_shared.config_loader import get_frontend_url_from_config

    monkeypatch.setattr(
        "metar_shared.config_loader._REPO_ROOT", tmp_path, raising=False
    )
    _write_config(tmp_path, "bad", {"api": None})
    assert get_frontend_url_from_config("bad") == ""
