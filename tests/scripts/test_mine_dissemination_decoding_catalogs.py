"""Tests for scripts/iwxxm/mine_dissemination_decoding_catalogs.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "iwxxm" / "mine_dissemination_decoding_catalogs.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "mine_dissemination_decoding_catalogs", SCRIPT
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mine_dissemination_decoding_check_ok() -> None:
    mod = _load_module()
    assert mod.main(["--check"]) == 0


def test_mine_dissemination_decoding_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_module()
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(mod, "DATA", data)
    monkeypatch.setattr(mod, "DISSEM_OUT", data / "dissem.yaml")
    monkeypatch.setattr(mod, "DECODE_OUT", data / "decode.yaml")
    assert mod.main([]) == 0
    assert (data / "dissem.yaml").is_file()
    assert (data / "decode.yaml").is_file()


def test_mine_dissemination_check_missing_and_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_module()
    missing = tmp_path / "missing-dissem.yaml"
    drifted = tmp_path / "drifted-decode.yaml"
    drifted.write_text("schema_version: 0\nentries: []\n", encoding="utf-8")
    monkeypatch.setattr(mod, "DISSEM_OUT", missing)
    monkeypatch.setattr(mod, "DECODE_OUT", drifted)
    assert mod.main(["--check"]) == 1
