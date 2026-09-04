"""T1.3 - Workspace/Docker/CI wire for packages/auth + JWKS env (EV-031 / F31)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestT13AuthWorkspaceWire:
    """Config gates for Auth package restore wiring (env-contract / ADR-033)."""

    def test_dockerfile_copies_packages_auth(self) -> None:
        text = (ROOT / "apps/backend/docker/Dockerfile").read_text(encoding="utf-8")
        assert "COPY packages/auth/pyproject.toml" in text
        assert "COPY packages/auth packages/auth" in text

    def test_makefile_lints_and_typechecks_auth(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        assert "packages/auth/src" in makefile
        assert "basedpyright packages/auth/src" in makefile
        assert "lint-auth" in makefile
        # EV-047 D-S056-cov95-scope=2 - restore make test-unit-auth (≥95% + per-file).
        assert "test-unit-auth:" in makefile
        assert "coverage-auth" not in makefile

    def test_ci_matrix_includes_auth_package(self) -> None:
        workflow = (ROOT / ".github/workflows/ci-cd.yml").read_text(encoding="utf-8")
        assert "auth," in workflow or "\n            auth," in workflow
        assert "matrix.package == 'auth'" in workflow
        assert "tests/unit/auth" in workflow
        assert "--cov-fail-under=100" in workflow
        assert "check_per_file_coverage.py" in workflow
        assert "worker," in workflow or "\n            worker," in workflow

    def test_env_example_documents_jwks(self) -> None:
        root_env = (ROOT / ".env.example").read_text(encoding="utf-8")
        assert "SUPABASE_JWKS_URL=" in root_env
        assert "SUPABASE_URL=" in root_env
        pkg_env = (ROOT / "packages/auth/.env.example").read_text(encoding="utf-8")
        assert "SUPABASE_JWKS_URL=" in pkg_env

    def test_compose_passes_auth_env_to_backend(self) -> None:
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        assert "SUPABASE_URL=${SUPABASE_URL:-}" in compose
        assert "SUPABASE_JWKS_URL=${SUPABASE_JWKS_URL:-}" in compose

    def test_render_api_lists_auth_env_keys(self) -> None:
        blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")
        # API service block must declare Auth URL + optional JWKS override.
        api_section = blueprint.split("metar-to-iwxxm-worker")[0]
        assert "SUPABASE_URL" in api_section
        assert "SUPABASE_JWKS_URL" in api_section
