"""Coverage for scripts/iwxxm/export_iwxxm_versions.py."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import ClassVar

import pytest
import scripts.iwxxm.export_iwxxm_versions as export_versions


class _FakeVersions:
    DEFAULT_VERSION = "2025-2"
    SUPPORTED_VERSIONS: ClassVar[dict[str, dict[str, str]]] = {
        "2025-2": {"status": "latest"},
        "2023-1": {"status": "previous"},
    }


@pytest.mark.unit
def test_build_payload_maps_roles() -> None:
    payload = export_versions.build_payload(_FakeVersions())
    assert payload["default"] == "2025-2"
    assert {"id": "2025-2", "role": "latest"} in payload["versions"]


@pytest.mark.unit
def test_build_payload_rejects_bad_status() -> None:
    class Bad:
        DEFAULT_VERSION = "2025-2"
        SUPPORTED_VERSIONS: ClassVar[dict[str, dict[str, str]]] = {
            "2025-2": {"status": "experimental"}
        }

    with pytest.raises(SystemExit, match="must be latest\\|previous"):
        export_versions.build_payload(Bad())


@pytest.mark.unit
def test_build_payload_rejects_default_not_in_supported() -> None:
    class Bad:
        DEFAULT_VERSION = "2099-1"
        SUPPORTED_VERSIONS: ClassVar[dict[str, dict[str, str]]] = {
            "2025-2": {"status": "latest"}
        }

    with pytest.raises(SystemExit, match="DEFAULT_VERSION"):
        export_versions.build_payload(Bad())


@pytest.mark.unit
def test_load_versions_module() -> None:
    versions = export_versions._load_versions_module()
    assert hasattr(versions, "DEFAULT_VERSION")
    assert hasattr(versions, "SUPPORTED_VERSIONS")


@pytest.mark.unit
def test_main_writes_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "generated" / "iwxxm_versions.json"
    monkeypatch.setattr(export_versions, "_OUT", out)
    monkeypatch.setattr(export_versions, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        export_versions, "_load_versions_module", lambda: _FakeVersions()
    )
    assert export_versions.main() == 0
    assert out.is_file()


@pytest.mark.unit
def test_main_writes_json_from_real_module(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "generated" / "iwxxm_versions.json"
    monkeypatch.setattr(export_versions, "_OUT", out)
    monkeypatch.setattr(export_versions, "_REPO_ROOT", tmp_path)
    assert export_versions.main() == 0
    assert out.is_file()


@pytest.mark.unit
def test_main_module_entrypoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "generated" / "iwxxm_versions.json"
    monkeypatch.setattr(export_versions, "_OUT", out)
    monkeypatch.setattr(export_versions, "_REPO_ROOT", tmp_path)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("scripts.iwxxm.export_iwxxm_versions", run_name="__main__")
    assert exc.value.code == 0
