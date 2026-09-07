"""TC-EV031-003 - public convert/lint/validate/decode stay JWT-free after Auth restore.

Spec: docs/test-plan.md TC-EV031-003; F21 Amended; F31 / ADR-033.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from src.api import app

SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
MINIMAL_IWXXM = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0"
  xmlns:gml="http://www.opengis.net/gml/3.2"
  gml:id="metar-tc-ev031-003"/>
"""


def _multipart(client: TestClient, path: str, fields: dict[str, str]):
    """POST multipart/form-data (``data=`` alone is urlencoded → 415)."""
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


@pytest.fixture
def public_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Unauthenticated client - no Authorization header injected."""
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")
    app.dependency_overrides.clear()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _assert_not_auth_gated(response) -> None:
    assert response.status_code not in {401, 403}, (
        f"public route must not require JWT; got {response.status_code}: {response.text}"
    )


@pytest.mark.unit
class TestTcEv031003PublicRoutesJwtFree:
    """Matrix of public operator routes succeed without Authorization."""

    def test_convert_without_authorization(self, public_client: TestClient) -> None:
        response = _multipart(
            public_client,
            "/api/v1/convert",
            {
                "manual_text": SAMPLE_METAR,
                "product": "METAR",
                "profile": "annex3",
                "iwxxm_version": "2025-2",
                "validate_output": "false",
            },
        )
        _assert_not_auth_gated(response)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body.get("successful", 0) >= 1

    def test_lint_tac_without_authorization(self, public_client: TestClient) -> None:
        response = _multipart(
            public_client,
            "/api/v1/lint-tac",
            {"manual_text": SAMPLE_METAR, "product": "METAR"},
        )
        _assert_not_auth_gated(response)
        assert response.status_code == 200, response.text
        assert "ok" in response.json()

    def test_decode_tac_without_authorization(self, public_client: TestClient) -> None:
        response = _multipart(
            public_client,
            "/api/v1/decode-tac",
            {"manual_text": SAMPLE_METAR, "product": "METAR"},
        )
        _assert_not_auth_gated(response)
        assert response.status_code == 200, response.text
        assert "segments" in response.json()

    def test_validate_without_authorization(self, public_client: TestClient) -> None:
        response = _multipart(
            public_client,
            "/api/v1/validate",
            {
                "iwxxm_xml": MINIMAL_IWXXM,
                "version": "2025-2",
            },
        )
        _assert_not_auth_gated(response)
        # Validation may fail schema/schematron; must not be auth-gated.
        assert response.status_code in {200, 400, 422}, response.text

    def test_auth_login_mounted_but_convert_stays_public(self, public_client: TestClient) -> None:
        """Restoring /auth/* must not re-gate convert (TC-EV031-003 objective)."""
        login = public_client.post(
            "/auth/login",
            json={"email": "tc-ev031-003@example.test", "password": "x"},
        )
        assert login.status_code != 404
        convert = _multipart(
            public_client,
            "/api/v1/convert",
            {"manual_text": SAMPLE_METAR, "validate_output": "false"},
        )
        _assert_not_auth_gated(convert)
        assert convert.status_code == 200, convert.text
