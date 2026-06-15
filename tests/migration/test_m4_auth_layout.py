"""M4 layout checks — migration-plan.md Step 2, spec.md §packages/auth."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGES_AUTH = ROOT / "packages" / "auth"


@pytest.mark.migration
class TestM4AuthPackageLayout:
    """packages/auth contains the in-repo auth library source tree."""

    def test_packages_auth_directory_exists(self) -> None:
        assert PACKAGES_AUTH.is_dir(), "packages/auth must exist after T4.2"

    def test_packages_auth_has_security_module(self) -> None:
        security = PACKAGES_AUTH / "src" / "auth" / "security.py"
        assert security.is_file(), "packages/auth/src/auth/security.py required for JWT middleware"

    def test_packages_auth_has_supabase_proxy(self) -> None:
        proxy = PACKAGES_AUTH / "src" / "auth" / "supabase_proxy.py"
        assert proxy.is_file(), "packages/auth/src/auth/supabase_proxy.py required for TC-M005"

    def test_packages_auth_has_pyproject(self) -> None:
        assert (PACKAGES_AUTH / "pyproject.toml").is_file()

    def test_packages_auth_has_tests_tree(self) -> None:
        assert (PACKAGES_AUTH / "tests").is_dir()
