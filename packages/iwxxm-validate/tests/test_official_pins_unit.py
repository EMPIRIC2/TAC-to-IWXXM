"""Unit coverage for official_pins helpers and path cache resolve (FR-077)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from iwxxm_validate import official_pins as op
from iwxxm_validate import paths as paths_mod
from iwxxm_validate.paths import clear_path_caches


@pytest.fixture(autouse=True)
def _clear() -> None:
    clear_path_caches()


def test_official_pin_ids_default_and_catalog() -> None:
    assert op.official_pin_ids() == op.OFFICIAL_PIN_IDS
    assert op.official_pin_ids({"pins": {"a": {}}}) == ("a",)
    assert op.official_pin_ids({"pins": "bad"}) == op.OFFICIAL_PIN_IDS


def test_load_catalog_os_error(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(op.OfficialPinError, match="invalid official pin catalog"):
        op.load_official_pins_catalog(missing)


def test_load_catalog_non_object(tmp_path: Path) -> None:
    path = tmp_path / "arr.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(op.OfficialPinError, match="JSON object"):
        op.load_official_pins_catalog(path)


def test_load_catalog_pin_not_object(tmp_path: Path) -> None:
    path = tmp_path / "pins.json"
    path.write_text(json.dumps({"pins": {"2025-2": "x"}}), encoding="utf-8")
    with pytest.raises(op.OfficialPinError, match="must be an object"):
        op.load_official_pins_catalog(path)


def test_assert_runtime_subset_missing_xsd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pin = tmp_path / "cache" / "2025-2" / "IWXXM" / "rule"
    pin.mkdir(parents=True)
    (pin / "iwxxm.sch").write_text("<sch/>", encoding="utf-8")
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(tmp_path / "cache"))
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(tmp_path / "norepo"))
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()
    with pytest.raises(op.OfficialPinError, match="official XSD missing"):
        op.assert_official_runtime_subset("2025-2")


def test_assert_runtime_subset_missing_sch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    iwxxm = tmp_path / "cache" / "2025-2" / "IWXXM"
    iwxxm.mkdir(parents=True)
    (iwxxm / "iwxxm.xsd").write_text("<xs/>", encoding="utf-8")
    (iwxxm / "rule").mkdir()
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(tmp_path / "cache"))
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(tmp_path / "norepo"))
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()
    with pytest.raises(op.OfficialPinError, match="official Schematron missing"):
        op.assert_official_runtime_subset("2025-2")


def test_schema_cache_root_env_and_catalog(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache = tmp_path / "mycache"
    pin = cache / "2025-2" / "IWXXM"
    pin.mkdir(parents=True)
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(cache))
    assert paths_mod.schema_cache_root() == cache.resolve()

    monkeypatch.delenv("IWXXM_SCHEMA_CACHE", raising=False)
    repo = tmp_path / "repo"
    catalog_dir = repo / "config" / "schemas"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "iwxxm-official-pins.json").write_text(
        json.dumps({"default_cache_rel": ".cache/custom-schemas", "pins": {}}),
        encoding="utf-8",
    )
    custom = repo / ".cache" / "custom-schemas" / "2023-1" / "IWXXM"
    custom.mkdir(parents=True)
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(repo))
    clear_path_caches()
    assert paths_mod.schema_cache_root() == (repo / ".cache" / "custom-schemas").resolve()


def test_schema_cache_root_bad_catalog_falls_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    catalog_dir = repo / "config" / "schemas"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "iwxxm-official-pins.json").write_text("{not-json", encoding="utf-8")
    default_cache = repo / ".cache" / "iwxxm-schemas" / "2025-2" / "IWXXM"
    default_cache.mkdir(parents=True)
    monkeypatch.delenv("IWXXM_SCHEMA_CACHE", raising=False)
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(repo))
    clear_path_caches()
    assert paths_mod.schema_cache_root() == (repo / ".cache" / "iwxxm-schemas").resolve()


def test_schema_cache_root_non_dict_catalog_falls_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Non-object JSON catalog skips default_cache_rel and uses the default path."""
    repo = tmp_path / "repo"
    catalog_dir = repo / "config" / "schemas"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "iwxxm-official-pins.json").write_text("[]", encoding="utf-8")
    default_cache = repo / ".cache" / "iwxxm-schemas" / "2025-2" / "IWXXM"
    default_cache.mkdir(parents=True)
    monkeypatch.delenv("IWXXM_SCHEMA_CACHE", raising=False)
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(repo))
    clear_path_caches()
    assert paths_mod.schema_cache_root() == (repo / ".cache" / "iwxxm-schemas").resolve()


def test_schema_cache_root_skips_non_pin_children(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cache dirs without an ``IWXXM`` child are skipped before a valid pin."""
    cache = tmp_path / "cache"
    (cache / "noise").mkdir(parents=True)
    (cache / "noise" / "readme.txt").write_text("x", encoding="utf-8")
    pin = cache / "2025-2" / "IWXXM"
    pin.mkdir(parents=True)
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(cache))
    clear_path_caches()
    assert paths_mod.schema_cache_root() == cache.resolve()


def test_candidate_roots_appends_default_cache_when_packaged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default cache is listed after packaged when ``IWXXM_SCHEMA_CACHE`` is unset."""
    repo = tmp_path / "repo"
    packaged = tmp_path / "packaged"
    (packaged / "iwxxm" / "2023-1" / "IWXXM").mkdir(parents=True)
    default = repo / ".cache" / "iwxxm-schemas" / "2025-2" / "IWXXM"
    default.mkdir(parents=True)
    monkeypatch.delenv("IWXXM_SCHEMA_CACHE", raising=False)
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(repo))
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: packaged)
    clear_path_caches()
    roots = paths_mod._candidate_iwxxm_roots()
    assert packaged / "iwxxm" in roots
    assert (repo / ".cache" / "iwxxm-schemas").resolve() in roots


def test_schema_cache_root_catalog_without_default_rel(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    catalog_dir = repo / "config" / "schemas"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "iwxxm-official-pins.json").write_text(
        json.dumps({"pins": {}}),
        encoding="utf-8",
    )
    default_cache = repo / ".cache" / "iwxxm-schemas" / "2025-2" / "IWXXM"
    default_cache.mkdir(parents=True)
    monkeypatch.delenv("IWXXM_SCHEMA_CACHE", raising=False)
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(repo))
    clear_path_caches()
    assert paths_mod.schema_cache_root() == (repo / ".cache" / "iwxxm-schemas").resolve()


def test_schema_cache_root_catalog_non_dict_falls_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cover paths.py L111 false branch: catalog JSON parses but is not a dict."""
    repo = tmp_path / "repo"
    catalog_dir = repo / "config" / "schemas"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "iwxxm-official-pins.json").write_text("[]", encoding="utf-8")
    default_cache = repo / ".cache" / "iwxxm-schemas" / "2025-2" / "IWXXM"
    default_cache.mkdir(parents=True)
    monkeypatch.delenv("IWXXM_SCHEMA_CACHE", raising=False)
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(repo))
    clear_path_caches()
    assert paths_mod.schema_cache_root() == (repo / ".cache" / "iwxxm-schemas").resolve()


def test_schema_cache_root_missing_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(tmp_path / "does-not-exist"))
    clear_path_caches()
    assert paths_mod.schema_cache_root() is None


def test_schema_cache_root_no_catalog_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the catalog file is absent, default ``.cache/iwxxm-schemas`` is used."""
    repo = tmp_path / "repo"
    default_cache = repo / ".cache" / "iwxxm-schemas" / "2025-2" / "IWXXM"
    default_cache.mkdir(parents=True)
    monkeypatch.delenv("IWXXM_SCHEMA_CACHE", raising=False)
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(repo))
    clear_path_caches()
    assert paths_mod.schema_cache_root() == (repo / ".cache" / "iwxxm-schemas").resolve()


def test_repo_root_schema_cache_name_guess(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IWXXM_VALIDATE_REPO_ROOT", raising=False)
    monkeypatch.setenv("IWXXM_SCHEMAS_ROOT", "/tmp/iwxxm-schemas")
    clear_path_caches()
    assert paths_mod.repo_root() == paths_mod._DEFAULT_REPO_ROOT


def test_require_pin_cache_wraps_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(tmp_path / "empty"))
    (tmp_path / "empty").mkdir()
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(tmp_path / "norepo"))
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()
    with pytest.raises(op.OfficialPinError, match="pin cache missing"):
        op.assert_official_pin_cache_present("2021-2")
