"""M6 layout checks — migration-plan.md Step 3, spec.md §apps/frontend."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
APPS_FRONTEND = ROOT / "apps" / "frontend"


@pytest.mark.migration
class TestM6FrontendAppLayout:
    """apps/frontend contains the in-repo UI source tree."""

    def test_apps_frontend_directory_exists(self) -> None:
        assert APPS_FRONTEND.is_dir(), "apps/frontend must exist after T6.2"

    def test_apps_frontend_has_vite_config(self) -> None:
        assert (APPS_FRONTEND / "vite.config.ts").is_file()

    def test_apps_frontend_has_package_json(self) -> None:
        assert (APPS_FRONTEND / "package.json").is_file()

    def test_apps_frontend_has_app_entry(self) -> None:
        assert (APPS_FRONTEND / "src" / "app" / "App.tsx").is_file()

    def test_apps_frontend_has_vite_api_base_url_test(self) -> None:
        """T6.1 contract test lives under the monorepo frontend app."""
        test_file = APPS_FRONTEND / "src" / "test" / "vite-api-base-url.client.test.ts"
        assert test_file.is_file(), "T6.1 VITE_API_BASE_URL Vitest contract required"
