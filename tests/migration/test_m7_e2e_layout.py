"""M7 E2E workspace layout — migration-plan.md Step 3, test-plan.md §E2E."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
APPS_E2E = ROOT / "apps" / "e2e"
LEGACY_TESTS = ROOT / "tests"

EXPECTED_SPECS = (
    "00-preflight.e2e.spec.ts",
    "admin-navigation.e2e.spec.ts",
    "auth-service-integration.e2e.spec.ts",
    "auth.e2e.spec.ts",
    "tac-file-conversion.e2e.spec.ts",
    "tac-file-upload-database.e2e.spec.ts",
    "workflow-auth-admin-readiness.e2e.spec.ts",
    "workflow-conversion-parameters-preferences.e2e.spec.ts",
    "workflow-logout-protection.e2e.spec.ts",
    "workflow-narrative-full-journey.e2e.spec.ts",
    "workflow-theme-persistence.e2e.spec.ts",
)


@pytest.mark.migration
class TestM7E2eWorkspaceLayout:
    """Playwright cross-app specs live in apps/e2e after T7.1."""

    def test_apps_e2e_directory_exists(self) -> None:
        assert APPS_E2E.is_dir(), "apps/e2e must exist after T7.1"

    def test_apps_e2e_has_package_json(self) -> None:
        assert (APPS_E2E / "package.json").is_file()

    def test_apps_e2e_has_playwright_config(self) -> None:
        assert (APPS_E2E / "playwright.config.ts").is_file()

    def test_apps_e2e_has_helpers_module(self) -> None:
        assert (APPS_E2E / "playwright-e2e-helpers.ts").is_file()

    @pytest.mark.parametrize("spec_name", EXPECTED_SPECS)
    def test_relocated_spec_present_in_apps_e2e(self, spec_name: str) -> None:
        assert (APPS_E2E / spec_name).is_file(), f"Missing relocated spec: {spec_name}"

    def test_no_e2e_specs_remain_in_root_tests(self) -> None:
        remaining = list(LEGACY_TESTS.glob("*.e2e.spec.ts"))
        assert remaining == [], (
            "Root tests/ must not contain *.e2e.spec.ts after relocation: "
            + ", ".join(p.name for p in remaining)
        )

    def test_pnpm_workspace_includes_apps_e2e(self) -> None:
        workspace = (ROOT / "pnpm-workspace.yaml").read_text(encoding="utf-8")
        assert "apps/*" in workspace or "apps/e2e" in workspace
