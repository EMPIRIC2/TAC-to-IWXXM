"""M4 layout checks — migration-plan.md Step 2, spec.md §packages/auth."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGES_AUTH = ROOT / "packages" / "auth"
LEGACY_AUTH = ROOT / "auth"


@pytest.mark.migration
class TestM4AuthPackageLayout:
    """Auth source tree pre/post move expectations for M4."""

    def test_legacy_auth_directory_exists(self) -> None:
        assert LEGACY_AUTH.is_dir(), "auth/ must exist until T4.2 move completes"

    def test_legacy_auth_has_security_module(self) -> None:
        security = LEGACY_AUTH / "src" / "auth" / "security.py"
        assert security.is_file(), "auth/src/auth/security.py required for JWT middleware"

    def test_legacy_auth_has_supabase_proxy(self) -> None:
        proxy = LEGACY_AUTH / "src" / "auth" / "supabase_proxy.py"
        assert proxy.is_file(), "auth/src/auth/supabase_proxy.py required for TC-M005"

    @pytest.mark.skip(reason="packages/auth populated in T4.2")
    def test_packages_auth_directory_exists(self) -> None:
        assert PACKAGES_AUTH.is_dir(), "packages/auth must exist after T4.2"
