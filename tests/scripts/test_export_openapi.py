"""Coverage for scripts/openapi/export_openapi.py."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
import scripts.openapi.export_openapi as export_openapi


@pytest.mark.unit
def test_main_writes_openapi(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "openapi.json"
    api_mod = types.ModuleType("src.api")
    api_mod.app = SimpleNamespace(openapi=lambda: {"openapi": "3.1.0", "paths": {}})
    src_mod = types.ModuleType("src")
    src_mod.api = api_mod

    monkeypatch.setattr(export_openapi, "_OUT", out)
    monkeypatch.setattr(export_openapi, "_REPO_ROOT", tmp_path)
    monkeypatch.setitem(sys.modules, "src", src_mod)
    monkeypatch.setitem(sys.modules, "src.api", api_mod)

    assert export_openapi.main() == 0

    text = out.read_text(encoding="utf-8")
    assert '"openapi": "3.1.0"' in text


@pytest.mark.unit
def test_main_module_entrypoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import runpy

    out = tmp_path / "openapi.json"
    monkeypatch.setattr(export_openapi, "_OUT", out)
    monkeypatch.setattr(export_openapi, "_REPO_ROOT", tmp_path)
    api_mod = types.ModuleType("src.api")
    api_mod.app = SimpleNamespace(openapi=lambda: {"openapi": "3.1.0", "paths": {}})
    src_mod = types.ModuleType("src")
    src_mod.api = api_mod
    monkeypatch.setitem(sys.modules, "src", src_mod)
    monkeypatch.setitem(sys.modules, "src.api", api_mod)

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("scripts.openapi.export_openapi", run_name="__main__")
    assert exc.value.code == 0
