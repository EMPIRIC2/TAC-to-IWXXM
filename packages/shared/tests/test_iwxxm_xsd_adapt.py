"""T3.7 - committed xsdata models + adapt helpers (ADR-027)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import BaseModel

from metar_shared.iwxxm_xsd import (
    available_versions,
    import_version_leaf,
    package_name,
    pydantic_to_msgspec,
    pydantic_to_rust_hint,
    version_package,
)
from metar_shared.iwxxm_xsd.adapt import _PACKAGE_ROOT


def test_available_versions_match_status_and_trees() -> None:
    versions = available_versions()
    assert "2023-1" in versions
    assert "2025-2" in versions
    for version in versions:
        tree = _PACKAGE_ROOT / version_package(version)
        assert tree.is_dir(), tree
        py_files = list(tree.rglob("*.py"))
        assert len(py_files) >= 50, (version, len(py_files))


def test_version_package_and_package_name() -> None:
    assert version_package("2025-2") == "v2025_2"
    assert package_name("2023-1") == "metar_shared.iwxxm_xsd.v2023_1"


def test_import_version_leaf_xlink_has_basemodels() -> None:
    mod = import_version_leaf("2025-2", "xlink")
    # Second call: parents + namespace stub already registered (branch coverage).
    mod2 = import_version_leaf("2025-2", "xlink")
    assert mod2 is mod or mod2.__name__ == mod.__name__
    models = [
        obj
        for obj in vars(mod).values()
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel
    ]
    assert models


def test_msgspec_and_rust_adapt_placeholders() -> None:
    with pytest.raises(NotImplementedError, match="msgspec"):
        pydantic_to_msgspec(object())
    with pytest.raises(NotImplementedError, match="Rust"):
        pydantic_to_rust_hint(object())


def test_import_version_leaf_missing_tree() -> None:
    with pytest.raises(FileNotFoundError, match="generated models missing"):
        import_version_leaf("2099-9", "xlink")


def test_available_versions_empty_without_status(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import metar_shared.iwxxm_xsd.adapt as adapt

    monkeypatch.setattr(adapt, "_STATUS_PATH", tmp_path / "missing.json")
    assert adapt.available_versions() == []


def test_available_versions_ignores_bad_status_shape(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import metar_shared.iwxxm_xsd.adapt as adapt

    bad = tmp_path / "STATUS.json"
    bad.write_text('{"versions": {"not": "a list"}}', encoding="utf-8")
    monkeypatch.setattr(adapt, "_STATUS_PATH", bad)
    assert adapt.available_versions() == []


def test_available_versions_rejects_non_object_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import metar_shared.iwxxm_xsd.adapt as adapt

    bad = tmp_path / "STATUS.json"
    bad.write_text('["2025-2"]', encoding="utf-8")
    monkeypatch.setattr(adapt, "_STATUS_PATH", bad)
    assert adapt.available_versions() == []


def test_available_versions_skips_non_scalar_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import metar_shared.iwxxm_xsd.adapt as adapt

    status = tmp_path / "STATUS.json"
    status.write_text(
        '{"versions": ["2025-2", {"nested": true}, null, 2023]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(adapt, "_STATUS_PATH", status)
    assert adapt.available_versions() == ["2025-2", "2023"]
