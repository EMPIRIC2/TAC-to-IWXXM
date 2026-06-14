"""Unit tests for root uv workspace configuration (T1.2)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestUvWorkspaceConfig:
    """Root pyproject.toml satisfies spec.md §Repository and ADR-005."""

    def test_python_version_file_pins_3_12(self) -> None:
        version_file = ROOT / ".python-version"
        assert version_file.exists()
        assert version_file.read_text(encoding="utf-8").strip().startswith("3.12")

    def test_root_pyproject_declares_uv_workspace(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "[tool.uv.workspace]" in content
        assert "members" in content

    def test_requires_python_is_3_12_plus(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert 'requires-python = ">=3.12"' in content
