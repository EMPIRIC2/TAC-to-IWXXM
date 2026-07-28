"""Verify packages/auth is deleted and no longer has a coverage gate (F21 / E17-22)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_auth_package_coverage_gate_retired() -> None:
    """packages/auth removed — ADR-007 gate no longer applies to metar-auth."""
    assert not (ROOT / "packages" / "auth").exists()
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "test-unit-auth" not in makefile
    assert "coverage-auth" not in makefile
