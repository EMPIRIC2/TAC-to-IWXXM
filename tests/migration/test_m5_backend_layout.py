"""M5 layout checks — migration-plan.md Step 3, spec.md §apps/backend."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
APPS_BACKEND = ROOT / "apps" / "backend"


@pytest.mark.migration
class TestM5BackendAppLayout:
    """apps/backend contains the in-repo API source tree."""

    def test_apps_backend_directory_exists(self) -> None:
        assert APPS_BACKEND.is_dir(), "apps/backend must exist after T5.2"

    def test_apps_backend_has_api_module(self) -> None:
        api = APPS_BACKEND / "src" / "api.py"
        assert api.is_file(), "apps/backend/src/api.py required for F1 conversion"

    def test_apps_backend_has_pyproject(self) -> None:
        assert (APPS_BACKEND / "pyproject.toml").is_file()

    def test_apps_backend_has_tests_tree(self) -> None:
        assert (APPS_BACKEND / "tests").is_dir()
