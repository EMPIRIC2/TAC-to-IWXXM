"""Unit tests for scripts/schemas/fetch_official_iwxxm_pins.py (no network)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_SCRIPT = _REPO / "scripts" / "schemas" / "fetch_official_iwxxm_pins.py"


def _load():
    spec = importlib.util.spec_from_file_location("fetch_official_iwxxm_pins", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _mini_pin(root: Path, name: str) -> Path:
    iwxxm = root / name / "IWXXM"
    rule = iwxxm / "rule"
    rule.mkdir(parents=True)
    (iwxxm / "iwxxm.xsd").write_text("<xs/>", encoding="utf-8")
    (rule / "iwxxm.sch").write_text("<sch/>", encoding="utf-8")
    return root / name


def test_compute_runtime_subset_sha256_stable(tmp_path: Path) -> None:
    fetch = _load()
    pin = _mini_pin(tmp_path, "2025-2")
    a = fetch.compute_runtime_subset_sha256(pin)
    b = fetch.compute_runtime_subset_sha256(pin)
    assert a == b
    assert len(a) == 64


def test_compute_runtime_subset_missing_tree(tmp_path: Path) -> None:
    fetch = _load()
    with pytest.raises(FileNotFoundError, match="IWXXM runtime tree missing"):
        fetch.compute_runtime_subset_sha256(tmp_path / "nope")


def test_default_cache_root_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fetch = _load()
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(tmp_path / "c"))
    assert fetch.default_cache_root({}) == (tmp_path / "c").resolve()


def test_fetch_pins_write_hashes_and_verify(tmp_path: Path) -> None:
    fetch = _load()
    catalog = {
        "upstream_repo": "wmo-im/iwxxm",
        "pins": {
            "2025-2": {
                "tag": "v2025-2",
                "commit_sha": "abc",
                "cache_dirname": "2025-2",
                "namespace_fragment": "2025-2",
                "runtime_subset_sha256": "",
            }
        },
    }
    catalog_path = tmp_path / "cat.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    def _mat(*, repo, commit_sha, cache_dirname, cache_root, checkout_root):
        del repo, commit_sha, checkout_root
        return _mini_pin(cache_root, cache_dirname)

    fetch._materialize_pin = _mat  # type: ignore[method-assign]
    summary = fetch.fetch_pins(
        catalog_path=catalog_path,
        cache_root=tmp_path / "cache",
        pins=["2025-2"],
        write_hashes=True,
        verify=True,
    )
    updated = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert updated["pins"]["2025-2"]["runtime_subset_sha256"]
    assert "2025-2" in summary["pins"]


def test_main_unknown_pin_exits_1(tmp_path: Path) -> None:
    fetch = _load()
    catalog_path = tmp_path / "cat.json"
    catalog_path.write_text(
        json.dumps({"upstream_repo": "wmo-im/iwxxm", "pins": {}}),
        encoding="utf-8",
    )
    code = fetch.main(["--catalog", str(catalog_path), "--pin", "nope", "--cache-root", str(tmp_path / "c")])
    assert code == 1


def test_verify_existing_missing_hash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fetch = _load()
    pin = _mini_pin(tmp_path / "cache", "2025-2")
    catalog = {
        "upstream_repo": "wmo-im/iwxxm",
        "pins": {
            "2025-2": {
                "tag": "v2025-2",
                "commit_sha": "abc",
                "cache_dirname": "2025-2",
                "namespace_fragment": "2025-2",
                "runtime_subset_sha256": "",
            }
        },
    }
    catalog_path = tmp_path / "cat.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(tmp_path / "cache"))
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(tmp_path / "norepo"))

    import iwxxm_validate.paths as paths_mod

    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    paths_mod.clear_path_caches()
    with pytest.raises(ValueError, match="missing runtime_subset_sha256"):
        fetch.verify_existing_pins(catalog_path=catalog_path, pins=["2025-2"])
    assert pin.is_dir()
