"""TC-EVYFC-002 — Convert emit YAML parity / routing (#1229 / ADR-047)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from tac2iwxxm.cli import main
from tac2iwxxm.convert import convert
from tac2iwxxm.emit_map import (
    ENV_EMIT_MAP_DIR,
    EmitMapError,
    _parse_emit_map,
    _resolve_python_plugin,
    check_emit_map_overlay_dir,
    clear_emit_map_catalog_cache,
    emit_with_map,
    load_emit_map_catalog,
    resolve_emit_map,
)
from tac2iwxxm.profiles.annex3 import emit_metar_speci_annex3
from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci

_TAC = "METAR KJFK 121255Z 18008KT 10SM FEW250 22/18 A2992="
_REPO = Path(__file__).resolve().parents[3]
_EMIT_OVERLAY_DIR = _REPO / "packages" / "tac2iwxxm" / "examples" / "overlays" / "emit-maps" / "valid"


@pytest.fixture(autouse=True)
def _clear_emit_map_cache() -> None:
    clear_emit_map_catalog_cache()
    yield
    clear_emit_map_catalog_cache()


def test_tc_evyfc_002_builtin_emit_map_parity_annex3() -> None:
    """YAML-routed emit matches direct python plugin (TC-EVYFC-002)."""
    result = convert(_TAC, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True
    assert result.xml
    mapped = resolve_emit_map(profile="annex3", product="METAR", iwxxm_version="2025-2")
    assert mapped.id == "annex3-metar-speci-emit"
    assert "emit_metar_speci_annex3" in mapped.plugin


def test_tc_evyfc_002_emit_with_map_matches_plugin() -> None:
    parsed = parse_metar_speci(_TAC, product="METAR")
    direct = emit_metar_speci_annex3(parsed, product="METAR", iwxxm_version="2025-2")
    via_map = emit_with_map(parsed, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert via_map == direct


def test_tc_evyfc_002_speci_uses_same_map() -> None:
    mapped = resolve_emit_map(profile="annex3", product="SPECI", iwxxm_version="2023-1")
    assert mapped.id == "annex3-metar-speci-emit"


def test_load_catalog_has_us_and_ca() -> None:
    catalog = load_emit_map_catalog()
    assert "iwxxm-us-metar-speci-emit" in catalog
    assert "ca-eccc-metar-speci-emit" in catalog
    us = resolve_emit_map(profile="iwxxm_us", product="METAR", iwxxm_version="2025-2")
    assert "iwxxm_us" in us.plugin
    ca = resolve_emit_map(profile="ca_eccc", product="METAR", iwxxm_version="3.0.0")
    assert "ca_eccc" in ca.plugin


def test_emit_map_missing_raises() -> None:
    with pytest.raises(EmitMapError, match="no emit map"):
        resolve_emit_map(profile="annex3", product="TAF", iwxxm_version="2025-2")


def test_emit_map_overlay_extends_plugin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "swap.yaml").write_text(
        "\n".join(
            [
                "id: annex3-metar-speci-emit-overlay",
                "extends: annex3-metar-speci-emit",
                "plugin: python:tac2iwxxm.profiles.annex3:emit_metar_speci_annex3",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, str(tmp_path))
    mapped = resolve_emit_map(profile="annex3", product="METAR", iwxxm_version="2025-2")
    assert mapped.source_path.endswith("swap.yaml")
    check_emit_map_overlay_dir(tmp_path)


def test_check_emit_map_overlay_not_dir(tmp_path: Path) -> None:
    with pytest.raises(EmitMapError, match="not a folder"):
        check_emit_map_overlay_dir(tmp_path / "nope")


def test_parse_errors() -> None:
    with pytest.raises(EmitMapError, match="mapping"):
        _parse_emit_map([], source_path="x")
    with pytest.raises(EmitMapError, match="id"):
        _parse_emit_map(
            {"profiles": ["annex3"], "products": ["METAR"], "plugin": "python:a:b"},
            source_path="x",
        )
    with pytest.raises(EmitMapError, match="kind"):
        _parse_emit_map(
            {
                "id": "bad",
                "kind": "xml_template",
                "profiles": ["annex3"],
                "products": ["METAR"],
                "plugin": "python:a:b",
            },
            source_path="x",
        )
    with pytest.raises(EmitMapError, match="python:"):
        _resolve_python_plugin("not-python")
    with pytest.raises(EmitMapError, match="module:attr"):
        _resolve_python_plugin("python:onlymodule")
    with pytest.raises(EmitMapError, match="not callable"):
        _resolve_python_plugin("python:tac2iwxxm.emit_map:ENV_EMIT_MAP_DIR")


def test_overlay_unknown_extends(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "bad.yaml").write_text(
        "id: x\nextends: does-not-exist\nplugin: python:tac2iwxxm.profiles.annex3:emit_metar_speci_annex3\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, str(tmp_path))
    with pytest.raises(EmitMapError, match="unknown emit map"):
        load_emit_map_catalog()


def test_overlay_dir_not_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    f = tmp_path / "file.txt"
    f.write_text("x", encoding="utf-8")
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, str(f))
    with pytest.raises(EmitMapError, match="not a folder"):
        load_emit_map_catalog()


def test_starter_overlay_loads() -> None:
    assert _EMIT_OVERLAY_DIR.is_dir()
    check_emit_map_overlay_dir(_EMIT_OVERLAY_DIR)


def test_cli_emit_map_overlay() -> None:
    assert main(["--check-overlay", str(_EMIT_OVERLAY_DIR), "--overlay-kind", "emit-map"]) == 0


def test_national_profile_routes_annex3_map() -> None:
    mapped = resolve_emit_map(profile="au_bom", product="METAR", iwxxm_version="2025-2")
    assert mapped.id == "annex3-metar-speci-emit"


def test_restore_env_after_check(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, "prior")
    check_emit_map_overlay_dir(tmp_path)
    assert os.environ.get(ENV_EMIT_MAP_DIR) == "prior"


def test_new_map_without_extends_requires_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "incomplete.yaml").write_text("id: only-id\n", encoding="utf-8")
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, str(tmp_path))
    with pytest.raises(EmitMapError):
        load_emit_map_catalog()


def test_overlay_non_mapping(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "list.yaml").write_text("- not-a-map\n", encoding="utf-8")
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, str(tmp_path))
    with pytest.raises(EmitMapError, match="mapping"):
        load_emit_map_catalog()


def test_optional_list_errors() -> None:
    from tac2iwxxm.emit_map import _optional_string_list, _require_string_list

    with pytest.raises(EmitMapError, match="non-empty list"):
        _optional_string_list([], label="profiles")
    with pytest.raises(EmitMapError, match="non-empty strings"):
        _optional_string_list(["ok", ""], label="profiles")
    with pytest.raises(EmitMapError, match="required"):
        _require_string_list(None, label="profiles")


def test_bad_plugin_string() -> None:
    with pytest.raises(EmitMapError, match="plugin must be"):
        _parse_emit_map(
            {
                "id": "x",
                "profiles": ["annex3"],
                "products": ["METAR"],
                "plugin": "   ",
            },
            source_path="x",
        )


def test_empty_module_attr() -> None:
    with pytest.raises(EmitMapError, match="module:attr"):
        _resolve_python_plugin("python::attr")


def test_new_map_missing_fields_via_layer() -> None:
    from tac2iwxxm.emit_map import EmitMap, _layer_overlay

    mapped = EmitMap(
        id="x",
        profiles=(),
        products=(),
        iwxxm_versions=None,
        kind="python_plugin",
        plugin="",
        source_path="x",
    )
    with pytest.raises(EmitMapError, match="require profiles"):
        _layer_overlay({}, mapped, {})


def test_extends_must_be_string() -> None:
    from tac2iwxxm.emit_map import EmitMap, _layer_overlay

    mapped = EmitMap(
        id="x",
        profiles=("annex3",),
        products=("METAR",),
        iwxxm_versions=None,
        kind="python_plugin",
        plugin="python:tac2iwxxm.profiles.annex3:emit_metar_speci_annex3",
        source_path="x",
    )
    with pytest.raises(EmitMapError, match="extends must be"):
        _layer_overlay({"extends": 1}, mapped, {})


def test_wrong_iwxxm_version_filtered() -> None:
    with pytest.raises(EmitMapError, match="no emit map"):
        resolve_emit_map(profile="annex3", product="METAR", iwxxm_version="1999-1")


def test_check_clears_env_when_unset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv(ENV_EMIT_MAP_DIR, raising=False)
    check_emit_map_overlay_dir(tmp_path)
    assert ENV_EMIT_MAP_DIR not in os.environ


def test_yml_overlay_extension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "swap.yml").write_text(
        "\n".join(
            [
                "id: annex3-metar-speci-emit-overlay",
                "extends: annex3-metar-speci-emit",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, str(tmp_path))
    mapped = resolve_emit_map(profile="annex3", product="METAR", iwxxm_version="2025-2")
    assert mapped.source_path.endswith("swap.yml")


def test_new_standalone_map(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "extra.yaml").write_text(
        "\n".join(
            [
                "id: experimental-metar-emit",
                "profiles: [annex3]",
                "products: [METAR]",
                "iwxxm_versions: ['2099-1']",
                "plugin: python:tac2iwxxm.profiles.annex3:emit_metar_speci_annex3",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, str(tmp_path))
    mapped = resolve_emit_map(profile="annex3", product="METAR", iwxxm_version="2099-1")
    assert mapped.id == "experimental-metar-emit"
