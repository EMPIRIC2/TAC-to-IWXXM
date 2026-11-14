"""Unit tests for basedpyright workspace configuration (T1.7)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestBasedpyrightConfig:
    """Root typechecker config per and typing-policy.md."""

    def test_root_pyproject_declares_basedpyright(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "[tool.basedpyright]" in content
        assert 'typeCheckingMode = "strict"' in content
        assert 'pythonVersion = "3.12"' in content
        assert '"apps"' in content
        assert '"packages"' in content
        assert '"tests"' in content

    def test_root_pyrightconfig_json_removed(self) -> None:
        """Typecheck settings live in pyproject.toml; root JSON was removed."""
        assert not (ROOT / "pyrightconfig.json").exists()
