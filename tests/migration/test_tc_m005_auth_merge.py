"""TC-M005: Auth merge behavior — test-plan.md §TC-M005, ADR-002.

Verifies auth endpoints are served from apps/backend (no AUTH_SERVICE_URL proxy)
and that protected conversion accepts a bearer token when auth is enabled.
Docker-compose two-service topology is asserted in T6.6 migration tests.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

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
def backend_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """TestClient for apps/backend with auth enforcement enabled."""
    monkeypatch.setenv("DISABLE_AUTH", "false")
    api_module = _load_backend_api_module()
    from src.utilities import security as sec

    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    api_module.app.dependency_overrides.clear()
    client = TestClient(api_module.app)
    yield client
    api_module.app.dependency_overrides.clear()


def _override_supabase_proxy(mock_proxy: MagicMock):
    """Return a dependency override for auth routes."""
    from auth.api_supabase import get_supabase_proxy

    def _override() -> MagicMock:
        return mock_proxy

    return get_supabase_proxy, _override


@pytest.mark.migration
class TestTcM005AuthMergeStructure:
    """Structural checks for merged auth topology."""

    def test_security_module_does_not_use_auth_service_url(self) -> None:
        security_py = APPS_BACKEND / "src" / "utilities" / "security.py"
        content = security_py.read_text(encoding="utf-8")
        assert "AUTH_SERVICE_URL" not in content

    def test_backend_mounts_auth_login_route(self) -> None:
        api_module = _load_backend_api_module()
        paths = set(_iter_route_paths(api_module.app.routes))
        assert "/auth/login" in paths
        assert "/auth/verify" in paths

    def test_compose_has_two_app_services_without_auth(self) -> None:
        """Post T6.6: compose is backend + frontend only (ADR-002)."""
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        assert "backend:" in compose
        assert "frontend:" in compose
        assert "auth:" not in compose
        assert "AUTH_SERVICE_URL" not in compose


@pytest.mark.migration
class TestTcM005AuthMergeIntegration:
    """In-process integration: login on backend host + JWT on convert."""

    def test_auth_login_on_backend_host(self, backend_client: TestClient) -> None:
        api_module = _load_backend_api_module()
        mock_proxy = MagicMock()
        mock_proxy.sign_in.return_value = {
            "user": {
                "id": "user-abc",
                "email": "merge@example.test",
                "metadata": {},
            },
            "session": {
                "access_token": "merged-access-token",
                "refresh_token": "merged-refresh-token",
                "expires_at": 4_102_444_800,
            },
        }

        dep_key, dep_override = _override_supabase_proxy(mock_proxy)
        api_module.app.dependency_overrides[dep_key] = dep_override
        try:
            response = backend_client.post(
                "/auth/login",
                json={
                    "email": "merge@example.test",
                    "password": "SecretPass1!",
                },
            )
        finally:
            api_module.app.dependency_overrides.pop(dep_key, None)

        assert response.status_code == 200
        body = response.json()
        assert body["user"]["id"] == "user-abc"
        assert body["session"]["access_token"] == "merged-access-token"
        mock_proxy.sign_in.assert_called_once()

    def test_convert_requires_auth_when_disabled_bypass_off(
        self, backend_client: TestClient
    ) -> None:
        response = backend_client.post(
            "/api/v1/convert",
            data={"manual_text": SAMPLE_METAR},
        )
        assert response.status_code == 401

    def test_convert_accepts_bearer_token_via_inlined_auth(
        self, backend_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utilities import security as sec

        mock_proxy = MagicMock()
        mock_proxy.verify_token.return_value = True
        mock_proxy.get_user.return_value = {
            "id": "user-abc",
            "email": "merge@example.test",
            "metadata": {},
        }
        monkeypatch.setattr(sec, "get_supabase_proxy", lambda: mock_proxy)

        response = backend_client.post(
            "/api/v1/convert",
            data={"manual_text": SAMPLE_METAR},
            headers={"Authorization": "Bearer merged-access-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["successful"] >= 1
        mock_proxy.verify_token.assert_called_once_with("merged-access-token")
        mock_proxy.get_user.assert_called_once_with("merged-access-token")
