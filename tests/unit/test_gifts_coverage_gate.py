"""Verify packages/gifts meets ADR-007 98% coverage gate (T3.5)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_gifts_package_coverage_gate_passes() -> None:
    """packages/gifts pytest run enforces fail_under=98 in its pyproject.toml."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "pytest",
            "tests",
            "--cov=gifts",
            "--cov=validation",
            "--cov-config=pyproject.toml",
            "--cov-branch",
            "--cov-fail-under=98",
            "-q",
        ],
        cwd=ROOT / "packages/gifts",
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    assert result.returncode == 0, (
        f"packages/gifts coverage gate failed:\n{result.stdout}\n{result.stderr}"
    )
