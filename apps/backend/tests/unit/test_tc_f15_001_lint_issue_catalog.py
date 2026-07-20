"""T5.1 / TC-F15 — GET /api/v1/lint-issue-catalog (E11-31 / api-contract).

Spec: docs/api-contract.md §Lint issue catalog; ADR-028; execution-plan T5.1.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token
from tac_validate.issue_registry import ISSUES, by_code


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_lint_issue_catalog_requires_auth() -> None:
    """Same auth gate as convert / lint-tac when DISABLE_AUTH is unset."""
    bare = TestClient(api_module.app)
    response = bare.get("/api/v1/lint-issue-catalog")
    assert response.status_code == 401


def test_lint_issue_catalog_shape_and_registry_subset(client: TestClient) -> None:
    response = client.get("/api/v1/lint-issue-catalog")
    assert response.status_code == 200
    payload = response.json()
    assert "issues" in payload
    assert isinstance(payload["issues"], list)
    assert len(payload["issues"]) == len(ISSUES)
    assert len(payload["issues"]) >= 1

    registry_codes = {spec.code for spec in ISSUES}
    seen: set[str] = set()
    for row in payload["issues"]:
        assert set(row.keys()) >= {"code", "severity", "message_template", "product", "tags"}
        assert row["code"] in registry_codes
        assert row["code"] not in seen
        seen.add(row["code"])
        spec = by_code(row["code"])
        assert row["severity"] == spec.severity
        assert row["message_template"] == spec.message_template
        assert row["product"] == spec.product
        assert row["tags"] == list(spec.tags)


def test_lint_issue_catalog_product_filter_metar(client: TestClient) -> None:
    response = client.get("/api/v1/lint-issue-catalog", params={"product": "metar"})
    assert response.status_code == 200
    codes = {row["code"] for row in response.json()["issues"]}
    assert "MISSING_OBS_TIME" in codes
    assert "MISSING_TERMINATOR" in codes
    # TAF-only product field should not appear under metar filter
    assert "MISSING_VALIDITY" not in codes


def test_lint_issue_catalog_product_filter_speci(client: TestClient) -> None:
    response = client.get("/api/v1/lint-issue-catalog", params={"product": "SPECI"})
    assert response.status_code == 200
    codes = {row["code"] for row in response.json()["issues"]}
    assert "MISSING_CCCC" in codes
    assert "INVALID_WEATHER" in codes
