"""Unit tests for 98% coverage gate configuration (T1.9, ADR-007)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestCoverageConfig:
    """Coverage gates documented per workspace member."""

    def test_root_pyproject_fail_under_98(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "fail_under = 98" in content

    def test_root_coverage_sources_monorepo_paths(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert 'source = ["apps", "packages"]' in content

    def test_shared_package_fail_under_98(self) -> None:
        content = (ROOT / "packages/shared/pyproject.toml").read_text(encoding="utf-8")
        assert "fail_under = 98" in content

    def test_tac2iwxxm_package_fail_under_95(self) -> None:
        content = (ROOT / "packages/tac2iwxxm/pyproject.toml").read_text(
            encoding="utf-8"
        )
        assert "fail_under = 95" in content

    def test_auth_package_absent_from_coverage_gates(self) -> None:
        assert not (ROOT / "packages/auth/pyproject.toml").exists()
        # Codecov removed (EV-028 / #781); coverage gates live in pyproject.toml only.
        assert not (ROOT / ".codecov.yml").exists()
        root = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "packages/auth" not in root
