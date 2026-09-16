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
        mod.mine_iwxxm_validation(sch_path=tmp_path / "no.sch")


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
    catalog = mod.mine_iwxxm_validation(sch_path=sch)
    ids = [a["id"] for a in catalog["asserts"]]
    assert ids.count("RULE.A") == 1
    assert "P1" in ids
