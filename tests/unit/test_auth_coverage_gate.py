"""Auth package restored — no separate Makefile coverage gate required (F31)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_auth_package_present_without_legacy_makefile_gate() -> None:
    """packages/auth exists; legacy test-unit-auth / coverage-auth targets stay retired."""
    assert (ROOT / "packages" / "auth").is_dir()
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "test-unit-auth" not in makefile
    assert "coverage-auth" not in makefile
