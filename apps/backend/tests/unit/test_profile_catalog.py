"""Unit tests for profile catalog loader (EV-933)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException
from src.services import profile_catalog as catalog_mod


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    catalog_mod.clear_catalog_cache()
    yield
    catalog_mod.clear_catalog_cache()


def test_load_profile_catalog_from_repo() -> None:
    resp = catalog_mod.load_profile_catalog()
    assert resp.profiles
    ids = {p.id for p in resp.profiles}
    assert "ICAO_2025" in ids


def test_catalog_path_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog = tmp_path / "c.yaml"
    catalog.write_text(
        "schema_version: 1\nprofiles:\n  - id: X\n    kind: semantic\n    products: []\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PROFILE_CATALOG_PATH", str(catalog))
    catalog_mod.clear_catalog_cache()
    resp = catalog_mod.load_profile_catalog()
    assert len(resp.profiles) == 1
    assert resp.profiles[0].id == "X"


def test_catalog_missing_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PROFILE_CATALOG_PATH", str(tmp_path / "missing.yaml"))
    catalog_mod.clear_catalog_cache()
    with pytest.raises(HTTPException) as exc:
        catalog_mod.load_profile_catalog()
    assert exc.value.status_code == 503


def test_catalog_malformed_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog = tmp_path / "bad.yaml"
    catalog.write_text("- just a list\n", encoding="utf-8")
    monkeypatch.setenv("PROFILE_CATALOG_PATH", str(catalog))
    catalog_mod.clear_catalog_cache()
    with pytest.raises(HTTPException) as exc:
        catalog_mod.load_profile_catalog()
    assert exc.value.status_code == 503


def test_catalog_malformed_profiles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog = tmp_path / "bad2.yaml"
    catalog.write_text("schema_version: 1\nprofiles: notalist\n", encoding="utf-8")
    monkeypatch.setenv("PROFILE_CATALOG_PATH", str(catalog))
    catalog_mod.clear_catalog_cache()
    with pytest.raises(HTTPException) as exc:
        catalog_mod.load_profile_catalog()
    assert exc.value.status_code == 503


def test_catalog_skips_non_dict_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog = tmp_path / "mixed.yaml"
    catalog.write_text(
        "schema_version: 1\nprofiles:\n  - not-a-map\n  - id: OK\n    kind: semantic\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PROFILE_CATALOG_PATH", str(catalog))
    catalog_mod.clear_catalog_cache()
    resp = catalog_mod.load_profile_catalog()
    assert [p.id for p in resp.profiles] == ["OK"]
