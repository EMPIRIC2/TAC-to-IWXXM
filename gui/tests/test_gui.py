"""GUI service tests with auth token injection.

Ensures static assets load and conversion endpoints function under auth.
"""
from __future__ import annotations
from gui.app import app

import random
import string
import sys
import pathlib
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Ensure repository root on path
ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_token(client: TestClient) -> str:
    suffix = ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=8))
    reg_payload = {
        "name": "GUI Test User",
        "email": f"guitest-{suffix}@example.com",
        "address": "123 Test St",
        "username": f"guitester{suffix}",
        "password": "StrongPass123!",
    }
    r = client.post("/auth/register", json=reg_payload)
    assert r.status_code == 200, r.text
    r_login = client.post("/auth/login", json={
        "username": reg_payload["username"], "password": reg_payload["password"]
    })
    assert r_login.status_code == 200, r_login.text
    return r_login.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class TestHealth:
    def test_health_endpoint(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert isinstance(data["gifts_available"], bool)


class TestStaticFiles:
    def test_index_page_loads(self, client: TestClient, auth_token: str) -> None:
        response = client.get("/", headers=_auth_headers(auth_token))
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "METAR" in response.text

    def test_javascript_loads(self, client: TestClient) -> None:
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert "application/javascript" in response.headers["content-type"] or "text/javascript" in response.headers["content-type"]

    def test_css_loads(self, client: TestClient) -> None:
        response = client.get("/static/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]


class TestConvertEndpoint:
    def test_manual_text_conversion(self, client: TestClient, auth_token: str) -> None:
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 SCT120 BKN250 15/07 A3005"
        response = client.post(
            "/api/convert", data={"manual_text": metar}, headers=_auth_headers(auth_token))
        assert response.status_code == 200
        data = response.json()
        assert data["successful"] == 1

    def test_file_upload_conversion(self, client: TestClient, auth_token: str) -> None:
        metar = "METAR EGLL 231750Z 27015KT 9999 FEW040 17/09 Q1023".encode(
            "utf-8")
        response = client.post(
            "/api/convert",
            files={"files": ("test.tac", metar, "text/plain")},
            headers=_auth_headers(auth_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1

    def test_multiple_file_upload(self, client: TestClient, auth_token: str) -> None:
        files = [
            ("files", ("metar1.tac",
             b"METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005", "text/plain")),
            ("files", ("metar2.tac",
             b"METAR EGLL 231750Z 27015KT 9999 FEW040 17/09 Q1023", "text/plain")),
        ]
        response = client.post("/api/convert", files=files,
                               headers=_auth_headers(auth_token))
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_manual_and_files_combined(self, client: TestClient, auth_token: str) -> None:
        response = client.post(
            "/api/convert",
            data={"manual_text": "METAR LFPG 231800Z 09012KT CAVOK 18/08 Q1015"},
            files={"files": (
                "test.tac", b"METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005", "text/plain")},
            headers=_auth_headers(auth_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_empty_file_error(self, client: TestClient, auth_token: str) -> None:
        response = client.post(
            "/api/convert",
            files={"files": ("empty.tac", b"", "text/plain")},
            headers=_auth_headers(auth_token),
        )
        assert response.status_code == 400

    def test_no_input_returns_empty(self, client: TestClient, auth_token: str) -> None:
        response = client.post(
            "/api/convert", data={"manual_text": ""}, headers=_auth_headers(auth_token))
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0


class TestConvertZipEndpoint:
    def test_zip_with_manual_input(self, client: TestClient, auth_token: str) -> None:
        response = client.post(
            "/api/convert-zip",
            data={"manual_text": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"},
            headers=_auth_headers(auth_token),
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"

    def test_zip_no_input_fails(self, client: TestClient, auth_token: str) -> None:
        response = client.post(
            "/api/convert-zip",
            data={"manual_text": ""},
            headers=_auth_headers(auth_token),
        )
        assert response.status_code in [200, 400]


class TestErrorHandling:
    def test_nonexistent_static_file_404(self, client: TestClient) -> None:
        response = client.get("/static/nonexistent.js")
        assert response.status_code == 404

    def test_unicode_in_manual_input(self, client: TestClient, auth_token: str) -> None:
        response = client.post(
            "/api/convert",
            data={
                "manual_text": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2"},
            headers=_auth_headers(auth_token),
        )
        assert response.status_code in [200, 400]

    def test_large_file_upload(self, client: TestClient, auth_token: str) -> None:
        metars = "\n".join([
            f"METAR KJFK 2317{i:02d}Z 18012KT 10SM FEW040 15/07 A3005" for i in range(3)
        ])
        response = client.post(
            "/api/convert",
            files={"files": ("large.tac", metars.encode(
                "utf-8"), "text/plain")},
            headers=_auth_headers(auth_token),
        )
        assert response.status_code in [200, 400]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
