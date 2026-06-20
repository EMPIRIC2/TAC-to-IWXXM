"""M7 Playwright monorepo config — test-plan.md §E2E, deploy.md §Local."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
APPS_E2E = ROOT / "apps" / "e2e"


@pytest.mark.migration
class TestM7PlaywrightMonorepoConfig:
    """Playwright targets monorepo dev stack paths after T7.2."""

    @pytest.fixture
    def playwright_config(self) -> str:
        return (APPS_E2E / "playwright.config.ts").read_text(encoding="utf-8")

    @pytest.fixture
    def global_setup(self) -> str:
        return (APPS_E2E / "playwright.global-setup.ts").read_text(encoding="utf-8")

    def test_playwright_uses_monorepo_dev_stack(self, playwright_config: str) -> None:
        assert "start-dev-servers.sh" in playwright_config
        assert "VITE_API_BASE_URL=http://localhost:8001" in playwright_config

    def test_playwright_defaults_to_local_dev_ports(self, playwright_config: str) -> None:
        assert "http://localhost:5173" in playwright_config
        assert "http://localhost:8001" in playwright_config

    def test_global_setup_waits_for_merged_backend_only(self, global_setup: str) -> None:
        assert "http://localhost:8001" in global_setup
        assert "8003" not in global_setup
        assert "PLAYWRIGHT_AUTH_HEALTH_URL" not in global_setup

    def test_auth_integration_spec_targets_merged_api(self) -> None:
        spec = (APPS_E2E / "auth-service-integration.e2e.spec.ts").read_text(encoding="utf-8")
        assert "PLAYWRIGHT_API_BASE_URL" in spec
        assert "http://localhost:8001" in spec
        assert "http://localhost:8003" not in spec
        assert "service: 'auth'" not in spec
