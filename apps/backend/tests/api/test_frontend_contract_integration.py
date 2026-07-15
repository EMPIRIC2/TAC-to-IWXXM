"""Integration-style API contract tests aligned with frontend api.ts types.

F7 workbench connection points (lint-tac, decode-tac, soft-preview, work-sessions,
CORS) live in ``test_f7_ui_connection_integration.py``.
"""

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.utilities.security import verify_supabase_token

VALID_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
INVALID_METAR = "NILl"


@pytest.fixture
def client() -> TestClient:
    """Create authenticated test client."""

    async def override_verify_token():
        return {"sub": "test-user-id", "aud": "test-project"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_convert_success_contract_matches_frontend(client: TestClient):
    """Validate convert success payload includes all fields expected by frontend."""
    response = client.post("/api/v1/convert", data={"manual_text": VALID_METAR})

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload["results"], list)
    assert isinstance(payload["errors"], list)
    assert isinstance(payload["issues"], list)
    assert isinstance(payload["total_processed"], int)
    assert isinstance(payload["successful"], int)
    assert isinstance(payload["failed"], int)

    assert payload["successful"] >= 1
    first_result = payload["results"][0]
    assert isinstance(first_result["name"], str)
    assert isinstance(first_result["content"], str)
    assert isinstance(first_result["source"], str)
    assert isinstance(first_result["size_bytes"], int)


def test_convert_partial_failure_includes_structured_issues(client: TestClient):
    """Validate mixed success/failure payload includes structured issues for frontend UI."""
    files = [
        ("files", ("valid.tac", VALID_METAR, "text/plain")),
        ("files", ("invalid.tac", INVALID_METAR, "text/plain")),
    ]
    response = client.post("/api/v1/convert", files=files)

    assert response.status_code == 200
    payload = response.json()

    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert len(payload["issues"]) >= 1

    issue = payload["issues"][0]
    assert isinstance(issue["source"], str)
    assert isinstance(issue["message"], str)
    assert issue["severity"] in {"error", "warning", "info"}


def test_convert_preview_contract_includes_failed_spans_keys(client: TestClient):
    """Soft-preview success still exposes ok/failed_spans keys the UI reads."""
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, VALID_METAR),
            "product": (None, "METAR"),
            "profile": (None, "annex3"),
            "lint": (None, "false"),
            "preview": (None, "true"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "ok" in payload
    assert isinstance(payload.get("failed_spans"), list)
    assert payload["successful"] >= 1
