"""M8 CI auth Docker removal — ADR-002, T8.2."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CI_CCD = ROOT / ".github" / "workflows" / "ci-cd.yml"


@pytest.mark.migration
class TestM8CiAuthDockerRemoved:
    """Auth is merged into the API deployable; CI must not build a separate auth image."""

    @pytest.fixture
    def workflow_text(self) -> str:
        return CI_CCD.read_text(encoding="utf-8")

    def test_ci_workflow_exists(self) -> None:
        assert CI_CCD.is_file()

    def test_ci_does_not_build_auth_dockerfile(self, workflow_text: str) -> None:
        assert "auth/Dockerfile" not in workflow_text
        assert "Build and push auth Docker image" not in workflow_text

    def test_ci_does_not_enable_auth_build_filter(self, workflow_text: str) -> None:
        assert "auth_build=true" not in workflow_text

    def test_ci_backend_dockerfile_uses_monorepo_path(self, workflow_text: str) -> None:
        assert "apps/backend/docker/Dockerfile" in workflow_text
