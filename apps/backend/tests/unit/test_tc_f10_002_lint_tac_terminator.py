"""T2.3 / TC-F10-002: lint-tac HTTP passthrough for MISSING_TERMINATOR info + fix.

Spec: docs/api-contract.md §lint-tac; ADR-025 §2.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

CLEAN_NO_EQ = "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034"
EXPECTED_COPY = "Reports in bulletins end with '=' - add it before publishing"


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_lint_tac_missing_terminator_info_and_fix(client: TestClient) -> None:
    response = client.post(
        "/api/v1/lint-tac",
        files={
            "manual_text": (None, CLEAN_NO_EQ),
            "product": (None, "METAR"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    term = next(i for i in payload["issues"] if i["code"] == "MISSING_TERMINATOR")
    assert term["severity"] == "info"
    assert term["message"] == EXPECTED_COPY
    fix = next(f for f in payload["fixes"] if f["code"] == "add_terminator")
    assert fix["replacement"] == CLEAN_NO_EQ.rstrip() + "="
