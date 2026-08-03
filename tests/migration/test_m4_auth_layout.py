"""M4 layout checks — packages/auth restored (F31 / ADR-033 / EV-031)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGES_AUTH = ROOT / "packages" / "auth"


@pytest.mark.migration
class TestM4AuthPackageRestored:
    """Operator Auth library is restored for JWKS-only login (EV-031)."""

    def test_packages_auth_directory_present(self) -> None:
        assert PACKAGES_AUTH.is_dir(), (
            "packages/auth must exist (F31 / ADR-033 / EV-031)"
        )
        assert (PACKAGES_AUTH / "pyproject.toml").is_file()
        assert (PACKAGES_AUTH / "src" / "metar_auth" / "jwks.py").is_file()

    def test_root_pyproject_includes_auth_member(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "packages/auth" in content
        assert "metar-auth" in content

    def test_backend_pyproject_includes_metar_auth(self) -> None:
        content = (ROOT / "apps" / "backend" / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        assert "metar-auth" in content

    def test_no_admin_module_in_auth_package(self) -> None:
        """Admin API must not return with the Auth restore (strip admin)."""
        assert not (PACKAGES_AUTH / "src" / "metar_auth" / "admin_api.py").exists()
        assert not (PACKAGES_AUTH / "src" / "admin_api.py").exists()
