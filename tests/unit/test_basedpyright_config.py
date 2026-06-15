"""Unit tests for basedpyright workspace configuration (T1.7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestBasedpyrightConfig:
    """Root typechecker config per ADR-005 and typing-policy.md."""

    def test_pyrightconfig_json_exists(self) -> None:
        config = ROOT / "pyrightconfig.json"
        assert config.exists()

    def test_pyrightconfig_includes_monorepo_paths(self) -> None:
        data = json.loads((ROOT / "pyrightconfig.json").read_text(encoding="utf-8"))
        include = data.get("include", [])
        assert "apps" in include
        assert "packages" in include
        assert "tests" in include

    def test_pyrightconfig_strict_mode_and_python_3_12(self) -> None:
        data = json.loads((ROOT / "pyrightconfig.json").read_text(encoding="utf-8"))
        assert data.get("typeCheckingMode") == "strict"
        assert data.get("pythonVersion") == "3.12"

    def test_root_pyproject_declares_basedpyright(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "[tool.basedpyright]" in content
        assert 'typeCheckingMode = "strict"' in content
