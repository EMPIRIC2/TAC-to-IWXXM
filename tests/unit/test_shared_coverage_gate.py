"""Verify packages/shared meets ADR-007 98% coverage gate (T1.10)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_shared_package_coverage_gate_passes() -> None:
    """packages/shared pytest run enforces fail_under=98 in its pyproject.toml."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "pytest",
            "packages/shared/tests",
            "--cov=metar_shared",
            "--cov-config=packages/shared/pyproject.toml",
            "--cov-branch",
            "--cov-fail-under=98",
            "-q",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, (
        f"packages/shared coverage gate failed:\n{result.stdout}\n{result.stderr}"
    )
