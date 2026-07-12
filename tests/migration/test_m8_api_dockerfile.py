"""M8 API Dockerfile gate — deploy.md §Docker Build Context, T8.1."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = ROOT / "apps" / "backend" / "docker" / "Dockerfile"


@pytest.mark.migration
class TestM8ApiDockerfileMonorepoContext:
    """API image builds from repo root with workspace packages and vendor schemas."""

    @pytest.fixture
    def dockerfile_text(self) -> str:
        return DOCKERFILE.read_text(encoding="utf-8")

    def test_dockerfile_exists(self) -> None:
        assert DOCKERFILE.is_file()

    def test_dockerfile_uses_python312_base(self, dockerfile_text: str) -> None:
        assert "python:3.12" in dockerfile_text

    def test_dockerfile_copies_monorepo_workspace_members(
        self, dockerfile_text: str
    ) -> None:
        for fragment in (
            "apps/backend",
            "packages/auth",
            "packages/tac2iwxxm",
            "packages/shared",
            "config",
            "vendor/schemas",
        ):
            assert fragment in dockerfile_text, f"Missing COPY path: {fragment}"
        assert "packages/gifts" not in dockerfile_text

    def test_dockerfile_copies_config_tree(self, dockerfile_text: str) -> None:
        """S003 — API image must bake config/prod.json for METAR_CONFIG_ENV=prod."""
        assert "COPY config" in dockerfile_text

    def test_dockerfile_does_not_reference_legacy_layout(
        self, dockerfile_text: str
    ) -> None:
        assert "COPY backend/" not in dockerfile_text
        assert "COPY GIFTs" not in dockerfile_text
        assert "COPY auth/" not in dockerfile_text

    def test_dockerfile_uses_uv_workspace_install(self, dockerfile_text: str) -> None:
        assert "uv sync" in dockerfile_text or "uv pip install" in dockerfile_text
        assert "pyproject.toml" in dockerfile_text

    def test_dockerfile_exposes_healthcheck_and_port(
        self, dockerfile_text: str
    ) -> None:
        assert "HEALTHCHECK" in dockerfile_text
        assert "/health" in dockerfile_text
        assert "8000" in dockerfile_text

    def test_dockerfile_runs_backend_module_entrypoint(
        self, dockerfile_text: str
    ) -> None:
        assert (
            'python", "-m", "src"' in dockerfile_text
            or "python -m src" in dockerfile_text
        )
