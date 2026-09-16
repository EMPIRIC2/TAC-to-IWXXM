"""Tests for scripts/iwxxm/mine_validation_library_catalogs.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "iwxxm" / "mine_validation_library_catalogs.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "mine_validation_library_catalogs", SCRIPT
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mine_validation_library_catalogs_check_ok() -> None:
    mod = _load_module()
    assert mod.main(["--check"]) == 0


def test_mine_validation_library_catalogs_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_module()
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(mod, "DATA", data)
    monkeypatch.setattr(mod, "TAC_OUT", data / "tac.yaml")
    monkeypatch.setattr(mod, "IWXXM_OUT", data / "iwxxm.yaml")
    assert mod.main([]) == 0
    assert (data / "tac.yaml").is_file()
    assert (data / "iwxxm.yaml").is_file()


def test_mine_validation_check_missing_and_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_module()
    missing = tmp_path / "missing-tac.yaml"
    drifted = tmp_path / "drifted-iwxxm.yaml"
    drifted.write_text("schema_version: 0\nasserts: []\n", encoding="utf-8")
    monkeypatch.setattr(mod, "TAC_OUT", missing)
    monkeypatch.setattr(mod, "IWXXM_OUT", drifted)
    assert mod.main(["--check"]) == 1


def test_mine_iwxxm_validation_missing_sch(tmp_path: Path) -> None:
    mod = _load_module()
    with pytest.raises(FileNotFoundError, match="missing Schematron"):
        mod.mine_sch_file(tmp_path / "no.sch", authority="wmo-iwxxm")


def test_mine_iwxxm_validation_dedupe_and_rule_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_module()
    sch = tmp_path / "rules.sch"
    sch.write_text(
        """<?xml version="1.0"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <pattern id="P1">
    <rule context="iwxxm:METAR">
      <assert test="true()">RULE.A: first</assert>
      <assert test="true()">RULE.A: duplicate id</assert>
      <assert test="true()">plain text without colon</assert>
      <assert test="true()">has space: not an id</assert>
    </rule>
  </pattern>
</schema>
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    items = mod._dedupe_asserts(
        mod.mine_sch_file(sch, authority="wmo-iwxxm", namespace_ids=False)
    )
    ids = [a["id"] for a in items]
    assert ids.count("RULE.A") == 1
    assert "P1" in ids
    assert all(a["authority"] == "wmo-iwxxm" for a in items)


def test_tc_evpyl_mine_006_foundation_sch_included() -> None:
    """TC-EVPYL-MINE-006: latest WMO foundation SCH mined with authority tags."""
    mod = _load_module()
    catalog = mod.mine_iwxxm_validation()
    authorities = {a["authority"] for a in catalog["asserts"]}
    assert "wmo-iwxxm" in authorities
    assert "wmo-metce" in authorities
    assert "wmo-opm" in authorities
    assert "wmo-saf" in authorities
    assert "wmo-collect" in authorities
    core = [a for a in catalog["asserts"] if a["authority"] == "wmo-iwxxm"]
    foundation = [a for a in catalog["asserts"] if a["authority"] != "wmo-iwxxm"]
    assert len(core) >= 50
    assert len(foundation) >= 20
    # Core ids stay un-prefixed; foundation ids are namespaced.
    assert all(":" not in a["id"] or a["id"].count(":") == 1 for a in foundation)
    assert all(a["id"].startswith("wmo-") for a in foundation)
    assert catalog.get("sources")
    assert len(catalog["sources"]) >= 5


def test_tc_evpyl_mine_007_opengis_excluded() -> None:
    """TC-EVPYL-MINE-007: OpenGIS SCH paths are not mined."""
    mod = _load_module()
    paths = [str(p).replace("\\", "/") for p, _ in mod.iwxxm_sch_sources()]
    assert all("schemas.opengis.net" not in p for p in paths)
    assert all("/om/" not in p for p in paths)
    assert all("samplingSpatial" not in p for p in paths)
    assert all("sweCommon" not in p for p in paths)
