"""Unit tests for root ruff configuration (T1.8)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestRuffConfig:
    """Root linter config per execution plan §Tech Stack."""

    def test_ruff_toml_exists(self) -> None:
        assert (ROOT / "ruff.toml").exists()

    def test_ruff_targets_python_3_12(self) -> None:
        content = (ROOT / "ruff.toml").read_text(encoding="utf-8")
        assert 'target-version = "py312"' in content

    def test_ruff_includes_monorepo_src_paths(self) -> None:
        content = (ROOT / "ruff.toml").read_text(encoding="utf-8")
        assert '"apps"' in content
        assert '"packages"' in content
        assert '"tests"' in content

    def test_tac2iwxxm_package_uses_ruff(self) -> None:
        tac_pyproject = (ROOT / "packages/tac2iwxxm/pyproject.toml").read_text(
            encoding="utf-8"
        )
        assert "[tool.ruff]" in tac_pyproject
        assert "flake8" not in tac_pyproject
        assert "black" not in tac_pyproject
