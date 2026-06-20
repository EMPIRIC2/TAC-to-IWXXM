"""M10 CI monorepo paths — T10.1, migration-plan.md Step 7."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CI_CCD = ROOT / ".github" / "workflows" / "ci-cd.yml"

LEGACY_PATH_FRAGMENTS = (
    "cd backend",
    "cd auth",
    "cd GIFTs",
    "cd frontend",
    "./backend/",
    "./auth/",
    "./GIFTs/",
    "./frontend/",
    "git submodule",
)

MONOREPO_PATH_FRAGMENTS = (
    "apps/backend",
    "packages/auth",
    "packages/gifts",
    "apps/frontend",
)


@pytest.mark.migration
class TestM10CiMonorepoPaths:
    """CI must target monorepo layout with pinned Python 3.12 and Node 22."""

    @pytest.fixture
    def workflow_text(self) -> str:
        return CI_CCD.read_text(encoding="utf-8")

    def test_ci_workflow_exists(self) -> None:
        assert CI_CCD.is_file()

    def test_ci_uses_monorepo_paths(self, workflow_text: str) -> None:
        for fragment in MONOREPO_PATH_FRAGMENTS:
            assert fragment in workflow_text, f"expected monorepo path {fragment!r} in ci-cd.yml"

    def test_ci_does_not_reference_legacy_paths(self, workflow_text: str) -> None:
        for fragment in LEGACY_PATH_FRAGMENTS:
            assert fragment not in workflow_text, f"legacy path {fragment!r} must be removed from ci-cd.yml"

    def test_ci_pins_python_312(self, workflow_text: str) -> None:
        assert "python-version: '3.12'" in workflow_text or 'python-version: "3.12"' in workflow_text
        assert not re.search(r"python-version:\s*['\"]3\.11['\"]", workflow_text)

    def test_ci_pins_node_22(self, workflow_text: str) -> None:
        assert "node-version: '22'" in workflow_text or 'node-version: "22"' in workflow_text

    def test_ci_frontend_uses_pnpm(self, workflow_text: str) -> None:
        assert "pnpm" in workflow_text
        assert "npm install --legacy-peer-deps" not in workflow_text


@pytest.mark.migration
class TestM10CiInRepoFrontendBuild:
    """T10.2 — frontend Docker build must use in-repo apps/frontend."""

    @pytest.fixture
    def workflow_text(self) -> str:
        return CI_CCD.read_text(encoding="utf-8")

    def test_ci_does_not_clone_external_frontend_repo(self, workflow_text: str) -> None:
        assert "FRONTEND_SOURCE_REPO" not in workflow_text
        assert "_frontend_src" not in workflow_text

    def test_ci_builds_frontend_from_apps_frontend(self, workflow_text: str) -> None:
        assert "context: ./apps/frontend" in workflow_text
        assert "file: ./apps/frontend/Dockerfile" in workflow_text
