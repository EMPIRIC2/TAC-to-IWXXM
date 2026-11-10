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
    api_dir = tmp_path / "api"
    fe_out = tmp_path / "apps" / "frontend" / "openapi" / "openapi.json"
    api_json = api_dir / "openapi.json"
    api_yaml = api_dir / "openapi.yaml"
    api_mod = types.ModuleType("src.api")
    api_mod.app = SimpleNamespace(openapi=lambda: {"openapi": "3.1.0", "paths": {}})
    src_mod = types.ModuleType("src")
    src_mod.api = api_mod

    monkeypatch.setattr(export_openapi, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(export_openapi, "_API_DIR", api_dir)
    monkeypatch.setattr(export_openapi, "_FE_OUT", fe_out)
    monkeypatch.setattr(export_openapi, "_API_JSON", api_json)
    monkeypatch.setattr(export_openapi, "_API_YAML", api_yaml)
    monkeypatch.setitem(sys.modules, "src", src_mod)
    monkeypatch.setitem(sys.modules, "src.api", api_mod)

    assert export_openapi.main() == 0

    text = api_json.read_text(encoding="utf-8")
    assert '"openapi": "3.1.0"' in text
    assert fe_out.is_file()
    assert api_yaml.is_file()
    assert "openapi: 3.1.0" in api_yaml.read_text(encoding="utf-8")


@pytest.mark.unit
def test_main_module_entrypoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``python -m`` path: call main under SystemExit without writing repo paths."""
    api_dir = tmp_path / "api"
    fe_out = tmp_path / "apps" / "frontend" / "openapi" / "openapi.json"
    api_json = api_dir / "openapi.json"
    api_yaml = api_dir / "openapi.yaml"
    monkeypatch.setattr(export_openapi, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(export_openapi, "_API_DIR", api_dir)
    monkeypatch.setattr(export_openapi, "_FE_OUT", fe_out)
    monkeypatch.setattr(export_openapi, "_API_JSON", api_json)
    monkeypatch.setattr(export_openapi, "_API_YAML", api_yaml)
    api_mod = types.ModuleType("src.api")
    api_mod.app = SimpleNamespace(openapi=lambda: {"openapi": "3.1.0", "paths": {}})
    src_mod = types.ModuleType("src")
    src_mod.api = api_mod
    monkeypatch.setitem(sys.modules, "src", src_mod)
    monkeypatch.setitem(sys.modules, "src.api", api_mod)

    with pytest.raises(SystemExit) as exc:
        raise SystemExit(export_openapi.main())
    assert exc.value.code == 0
    assert api_json.is_file()
