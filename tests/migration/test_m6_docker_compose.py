"""M6 docker-compose topology - deploy.md §Local, test-plan.md TC-M005 compose gate."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT / "docker-compose.yml"


@pytest.mark.migration
class TestM6DockerComposeTwoServices:
    """Post-auth-merge compose exposes backend + frontend only."""

    @pytest.fixture
    def compose_text(self) -> str:
        return COMPOSE_FILE.read_text(encoding="utf-8")

    def test_compose_file_exists(self) -> None:
        assert COMPOSE_FILE.is_file()

    def test_compose_has_exactly_two_app_services(self, compose_text: str) -> None:
        service_headers = re.findall(r"^  (\w+):\s*$", compose_text, re.MULTILINE)
        assert service_headers == ["backend", "frontend"]

    def test_compose_does_not_define_auth_service(self, compose_text: str) -> None:
        assert "auth:" not in compose_text
        assert "AUTH_SERVICE_URL" not in compose_text
        assert "VITE_AUTH_SERVICE_URL" not in compose_text
        assert "VITE_BACKEND_URL" not in compose_text

    def test_backend_uses_monorepo_dockerfile(self, compose_text: str) -> None:
        assert "dockerfile: apps/backend/docker/Dockerfile" in compose_text
        assert "context: ." in compose_text

    def test_frontend_uses_apps_frontend_context(self, compose_text: str) -> None:
        assert "context: ./apps/frontend" in compose_text

    def test_frontend_wires_unified_vite_api_base_url(self, compose_text: str) -> None:
        assert "VITE_API_BASE_URL" in compose_text

    def test_backend_wires_metar_cors_origins(self, compose_text: str) -> None:
        assert "METAR_CORS_ORIGINS" in compose_text

    def test_frontend_depends_on_backend_only(self, compose_text: str) -> None:
        frontend_block = compose_text.split("frontend:", 1)[1]
        depends_section = frontend_block.split("networks:", 1)[0]
        assert "depends_on:" in depends_section
        assert "backend:" in depends_section
        assert "auth:" not in depends_section
