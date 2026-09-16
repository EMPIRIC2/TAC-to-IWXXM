"""Tests for scripts/iwxxm/mine_conversion_schema_blocks.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "iwxxm" / "mine_conversion_schema_blocks.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "mine_conversion_schema_blocks", SCRIPT
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mine_conversion_schema_blocks_check_ok() -> None:
    mod = _load_module()
    assert mod.main(["--check"]) == 0


def test_mine_conversion_schema_blocks_writes(tmp_path: Path) -> None:
    mod = _load_module()
    out = tmp_path / "blocks.yaml"
    assert mod.main(["--out", str(out)]) == 0
    assert out.is_file()
    assert "authority: wmo" in out.read_text(encoding="utf-8")
