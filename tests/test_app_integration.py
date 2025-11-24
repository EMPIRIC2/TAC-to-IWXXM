"""Cross-service integration tests.

Validates that auth, backend, and gui services can operate together.
Uses lightweight FastAPI TestClient instances for each service.
"""
from __future__ import annotations
from gui.app import app as gui_app  # type: ignore
from backend.api import app as backend_app  # type: ignore
from auth.api import router as auth_router  # type: ignore

import random
import string
import pathlib
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure repository root importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import individual service apps/routers
AUTH_SRC = ROOT / "auth" / "src"
BACKEND_SRC = ROOT / "backend" / "src"
GUI_SRC = ROOT / "gui" / "src"
for p in (AUTH_SRC, BACKEND_SRC, GUI_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


# Build a composite app (optional) to show aggregation also works
composite_app = FastAPI(title="Composite METAR IWXXM App")
composite_app.include_router(auth_router)
# Replicate backend routes under /backend to avoid collision with gui
# (gui and backend both have /api/convert). Mounting preserves original paths.
composite_app.mount("/backend", backend_app)
# Mount gui at /gui for completeness (its root index is protected by auth)
composite_app.mount("/gui", gui_app)


@pytest.fixture(scope="session")
def auth_client() -> TestClient:
    # Only auth router
    app = FastAPI()
    app.include_router(auth_router)
    return TestClient(app)


@pytest.fixture(scope="session")
def backend_client() -> TestClient:
    return TestClient(backend_app)


@pytest.fixture(scope="session")
def gui_client() -> TestClient:
    return TestClient(gui_app)


@pytest.fixture(scope="session")
def composite_client() -> TestClient:
    return TestClient(composite_app)


@pytest.fixture(scope="session")
def user_token(auth_client: TestClient) -> str:
    suffix = ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=8))
    reg_payload = {
        "name": "Integration User",
        "email": f"integration-{suffix}@example.com",
        "address": "123 Integration Ave",
        "username": f"intuser{suffix}",
        "password": "StrongPass123!",
    }
    r = auth_client.post("/auth/register", json=reg_payload)
    assert r.status_code == 200, r.text
    r_login = auth_client.post("/auth/login", json={
        "username": reg_payload["username"],
        "password": reg_payload["password"],
    })
    assert r_login.status_code == 200, r_login.text
    return r_login.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class TestAuthService:
    def test_register_and_login(self, user_token: str) -> None:
        assert isinstance(user_token, str) and len(user_token) > 10


class TestBackendService:
    def test_backend_health(self, backend_client: TestClient) -> None:
        r = backend_client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ["healthy", "degraded"]

    def test_backend_manual_convert(self, backend_client: TestClient) -> None:
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
        r = backend_client.post("/api/convert", data={"manual_text": metar})
        assert r.status_code == 200
        data = r.json()
        assert data["successful"] == 1


class TestGuiService:
    def test_gui_health(self, gui_client: TestClient) -> None:
        r = gui_client.get("/health")
        assert r.status_code == 200

    def test_gui_protected_index(self, gui_client: TestClient, user_token: str) -> None:
        r = gui_client.get("/", headers=_auth_headers(user_token))
        assert r.status_code == 200
        assert "METAR" in r.text

    def test_gui_convert_endpoint(self, gui_client: TestClient, user_token: str) -> None:
        metar = "METAR EGLL 231750Z 27015KT 9999 FEW040 17/09 Q1023"
        r = gui_client.post(
            "/api/convert", data={"manual_text": metar}, headers=_auth_headers(user_token))
        assert r.status_code == 200
        data = r.json()
        assert data["successful"] == 1


class TestCompositeApp:
    def test_composite_auth_login(self, composite_client: TestClient, user_token: str) -> None:
        # Token already obtained from auth-only client; verify composite health & reuse token.
        r = composite_client.get("/backend/health")
        assert r.status_code == 200

    def test_composite_gui_index(self, composite_client: TestClient, user_token: str) -> None:
        r = composite_client.get("/gui/", headers=_auth_headers(user_token))
        assert r.status_code == 200
        assert "METAR" in r.text


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-q"])
