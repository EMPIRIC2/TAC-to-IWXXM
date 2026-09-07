"""Auth package coverage gate - fail_under=100 in packages/auth pyproject (EV-080)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_auth_pyproject_fail_under_100() -> None:
    """packages/auth pyproject enforces fail_under = 100 (EV-080 / ADR-007)."""
    content = (ROOT / "packages/auth/pyproject.toml").read_text(encoding="utf-8")
    assert "fail_under = 100" in content
