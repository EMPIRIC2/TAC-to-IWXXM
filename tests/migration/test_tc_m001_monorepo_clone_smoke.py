"""TC-M001: Monorepo Clone Smoke — test-plan.md §TC-M001, UJ-DEV-001.

Verifies a clean clone builds and runs unit tests without git submodules.
Steps (test-plan):
  1. Clone repo (precondition checks below).
  2. ``make install && make test-unit``.
  3. ``make dev`` (or docker-compose) and hit ``/health`` (deferred until T1.6+).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

MONOREPO_LAYOUT_PATHS = (
    "packages/shared",
    "pyproject.toml",
    "pnpm-workspace.yaml",
    "Makefile",
)


def _run_make(target: str, *, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", target],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


@pytest.mark.migration
class TestTcM001MonorepoCloneSmoke:
    """Single-clone monorepo smoke per test-plan.md TC-M001."""

    def test_no_gitmodules_file(self) -> None:
        """Precondition: clone works without ``git submodule update``."""
        gitmodules = ROOT / ".gitmodules"
        assert not gitmodules.exists(), (
            "TC-M001 requires .gitmodules absent; remove submodules in T11.1"
        )

    @pytest.mark.parametrize("relative_path", MONOREPO_LAYOUT_PATHS)
    def test_monorepo_layout_path_exists(self, relative_path: str) -> None:
        """Target tree from spec.md §Repository."""
        path = ROOT / relative_path
        assert path.exists(), f"Missing monorepo path: {relative_path}"

    def test_make_install_target_exists(self) -> None:
        """Makefile exposes ``install`` (config-spec-monorepo.md)."""
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        assert re_install_target(makefile), (
            "Makefile must define an ``install`` target (T1.6)"
        )

    def test_make_install_succeeds(self) -> None:
        """Step 2: ``make install`` completes without error."""
        result = _run_make("install", timeout=900)
        assert result.returncode == 0, (
            f"make install failed (exit {result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )

    def test_make_test_unit_succeeds(self) -> None:
        """Step 2: core unit tests green after install."""
        result = _run_make("test-unit", timeout=1800)
        assert result.returncode == 0, (
            f"make test-unit failed (exit {result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )

    @pytest.mark.skip(
        reason="Health check wired when make dev targets monorepo apps (T1.6+)"
    )
    def test_backend_health_returns_200(self) -> None:
        """Step 3: ``/health`` returns 200 after ``make dev`` or docker-compose."""
        import httpx

        response = httpx.get("http://localhost:18001/health", timeout=5.0)
        assert response.status_code == 200


def re_install_target(makefile: str) -> bool:
    """Return True when Makefile declares an ``install`` phony/target."""
    for line in makefile.splitlines():
        stripped = line.strip()
        if stripped.startswith("install:"):
            return True
        if stripped.startswith(".PHONY:") and "install" in stripped:
            return True
    return False
