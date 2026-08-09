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

    def test_auth_package_listed_in_workspace_without_codecov(self) -> None:
        assert (ROOT / "packages/auth/pyproject.toml").exists()
        # Codecov removed (EV-028 / #781); coverage gates live in pyproject.toml only.
        assert not (ROOT / ".codecov.yml").exists()
        root = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "packages/auth" in root
        assert "metar-auth" in root

    def test_auth_and_worker_fail_under_95(self) -> None:
        """EV-047 D-S056-cov95-scope=2 — auth + worker hard package floors."""
        auth = (ROOT / "packages/auth/pyproject.toml").read_text(encoding="utf-8")
        worker = (ROOT / "apps/worker/pyproject.toml").read_text(encoding="utf-8")
        assert "fail_under = 95" in auth
        assert "fail_under = 95" in worker

    def test_per_file_coverage_checker_script_exists(self) -> None:
        assert (ROOT / "scripts/ci/check_per_file_coverage.py").is_file()
