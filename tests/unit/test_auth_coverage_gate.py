"""Verify packages/auth meets ADR-007 98% coverage gate (T4.4)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_auth_package_coverage_gate_passes() -> None:
    """packages/auth pytest run enforces fail_under=98 in its pyproject.toml."""
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "pytest",
            "tests",
            "--cov=src",
            "--cov-config=pyproject.toml",
            "--cov-branch",
            "--cov-fail-under=98",
            "-q",
        ],
        cwd=ROOT / "packages/auth",
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
        env=env,
    )
    assert result.returncode == 0, (
        f"packages/auth coverage gate failed:\n{result.stdout}\n{result.stderr}"
    )
