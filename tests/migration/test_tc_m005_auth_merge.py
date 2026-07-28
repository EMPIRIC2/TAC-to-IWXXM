"""TC-M005 superseded by F21 — Auth merge → Auth gone (ADR-031 / TC-F21-auth-gone).

Historical TC-M005 verified auth on the backend host. Public app privacy removes
operator Auth entirely; this module asserts the post-F21 topology.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
APPS_BACKEND = ROOT / "apps" / "backend"
SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"


def _ensure_backend_importable() -> None:
    backend_src = str(APPS_BACKEND)
    if backend_src not in sys.path:
        sys.path.insert(0, backend_src)


def _iter_route_paths(routes) -> list[str]:
    paths: list[str] = []
    for route in routes:
        if isinstance(route, APIRoute):
            paths.append(route.path)
        elif type(route).__name__ == "_IncludedRouter":
            paths.extend(_iter_route_paths(route.original_router.routes))
        elif hasattr(route, "routes") and route.routes:
            paths.extend(_iter_route_paths(route.routes))
    return paths


def _load_backend_api_module() -> ModuleType:
    _ensure_backend_importable()
    import importlib

    if "src.api" in sys.modules:
        return sys.modules["src.api"]
    return importlib.import_module("src.api")


@pytest.fixture
def backend_client() -> Iterator[TestClient]:
    """TestClient for apps/backend (public convert; no Auth)."""
    api_module = _load_backend_api_module()
    api_module.app.dependency_overrides.clear()
    client = TestClient(api_module.app)
    yield client
    api_module.app.dependency_overrides.clear()


@pytest.mark.migration
class TestTcM005AuthGoneStructure:
    """Structural checks for public API topology after Auth delete."""

    def test_security_module_does_not_use_auth_service_url(self) -> None:
        security_py = APPS_BACKEND / "src" / "utilities" / "security.py"
        content = security_py.read_text(encoding="utf-8")
        assert "AUTH_SERVICE_URL" not in content

    def test_backend_does_not_mount_auth_routes(self) -> None:
        api_module = _load_backend_api_module()
        paths = set(_iter_route_paths(api_module.app.routes))
        assert "/auth/login" not in paths
        assert "/auth/verify" not in paths
        assert not any(p.startswith("/auth/") for p in paths)

    def test_packages_auth_absent(self) -> None:
        assert not (ROOT / "packages" / "auth").exists()

    def test_compose_has_two_app_services_without_auth(self) -> None:
        """Compose is backend + frontend only (ADR-002 / F21)."""
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        assert "backend:" in compose
        assert "frontend:" in compose
        assert "auth:" not in compose
        assert "AUTH_SERVICE_URL" not in compose


@pytest.mark.migration
class TestTcM005PublicConvertIntegration:
    """In-process: Auth gone + public convert without JWT."""

    def test_auth_login_returns_404(self, backend_client: TestClient) -> None:
        response = backend_client.post(
            "/auth/login",
            json={"email": "merge@example.test", "password": "SecretPass1!"},
        )
        assert response.status_code == 404

    def test_convert_succeeds_without_authorization(
        self, backend_client: TestClient
    ) -> None:
        response = backend_client.post(
            "/api/v1/convert",
            data={"manual_text": SAMPLE_METAR},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["successful"] >= 1
