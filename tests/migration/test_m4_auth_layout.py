"""M4 layout checks — packages/auth deleted (F21 / ADR-031 / E17-22)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGES_AUTH = ROOT / "packages" / "auth"


@pytest.mark.migration
class TestM4AuthPackageDeleted:
    """Operator Auth library is removed from the workspace (EV-017)."""

    def test_packages_auth_directory_absent(self) -> None:
        assert not PACKAGES_AUTH.exists(), (
            "packages/auth must be deleted (F21 / ADR-031 / E17-22)"
        )

    def test_root_pyproject_omits_auth_member(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "packages/auth" not in content
        assert "metar-auth" not in content

    def test_backend_pyproject_omits_metar_auth(self) -> None:
        content = (ROOT / "apps" / "backend" / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        assert "metar-auth" not in content
