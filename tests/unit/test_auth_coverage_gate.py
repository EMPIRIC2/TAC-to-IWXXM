"""Auth package coverage gate — fail_under=95 in packages/auth pyproject (EV-047)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_auth_package_fail_under_95() -> None:
    """packages/auth pyproject enforces fail_under = 95 (D-S056-cov95-scope=2)."""
    assert (ROOT / "packages" / "auth").is_dir()
    content = (ROOT / "packages" / "auth" / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert "fail_under = 95" in content
