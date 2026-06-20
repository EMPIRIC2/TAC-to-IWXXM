"""M7 T2 product E2E gate — test-plan.md TC-001, TC-003."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
APPS_E2E = ROOT / "apps" / "e2e"
MAKEFILE = ROOT / "Makefile"


@pytest.mark.migration
class TestM7T2ProductE2eGate:
    """TC-001 and TC-003 Playwright specs are wired for local T2 verification."""

    def test_tc001_spec_present(self) -> None:
        spec = APPS_E2E / "tac-file-conversion.e2e.spec.ts"
        assert spec.is_file(), "TC-001 maps to tac-file-conversion.e2e.spec.ts"

    def test_tc003_spec_present(self) -> None:
        spec = APPS_E2E / "auth.e2e.spec.ts"
        assert spec.is_file(), "TC-003 maps to auth.e2e.spec.ts"

    def test_makefile_exposes_t2_product_target(self) -> None:
        makefile = MAKEFILE.read_text(encoding="utf-8")
        assert "test-e2e-t2-product:" in makefile
        assert "tac-file-conversion.e2e.spec.ts" in makefile
        assert "auth.e2e.spec.ts" in makefile

    def test_playwright_helpers_accept_root_admin_env_fallback(self) -> None:
        helpers = (APPS_E2E / "playwright-e2e-helpers.ts").read_text(encoding="utf-8")
        assert "process.env.ADMIN_EMAIL" in helpers
        assert "process.env.ADMIN_PASSWORD" in helpers
        assert "openConverterForE2e" in helpers

    def test_start_dev_servers_loads_repo_env(self) -> None:
        script = (ROOT / "start-dev-servers.sh").read_text(encoding="utf-8")
        assert "load_repo_env" in script
        assert "VITE_SUPABASE_URL" in script
