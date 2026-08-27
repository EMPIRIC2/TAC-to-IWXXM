"""T5.1 / TC-F15 - GET /api/v1/lint-issue-catalog (E11-31 / api-contract).

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


def test_lint_issue_catalog_is_public() -> None:
    """F21: catalog is public - no Authorization required."""
    bare = TestClient(api_module.app)
    response = bare.get("/api/v1/lint-issue-catalog")
    assert response.status_code != 401
    assert response.status_code != 403
    assert response.status_code == 200


def test_lint_issue_catalog_shape_and_registry_subset(client: TestClient) -> None:
    response = client.get("/api/v1/lint-issue-catalog")
    assert response.status_code == 200
    payload = response.json()
    assert "issues" in payload
    assert isinstance(payload["issues"], list)
    lint_rows = [row for row in payload["issues"] if row.get("family") == "lint"]
    iwxxm_rows = [row for row in payload["issues"] if row.get("family") == "iwxxm"]
    assert len(lint_rows) == len(ISSUES)
    assert len(iwxxm_rows) >= 1
    assert len(payload["issues"]) == len(lint_rows) + len(iwxxm_rows)

    registry_codes = {spec.code for spec in ISSUES}
    seen: set[str] = set()
    for row in lint_rows:
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


def test_lint_issue_catalog_issue_type_filter(client: TestClient) -> None:
    response = client.get(
        "/api/v1/lint-issue-catalog",
        params={"issue_type": "iwxxm_schema", "family": "iwxxm"},
    )
    assert response.status_code == 200
    rows = response.json()["issues"]
    assert rows
    assert all(row.get("issue_type") == "iwxxm_schema" for row in rows)
    assert any(row["code"] == "XML_SCHEMA" for row in rows)


def test_lint_issue_catalog_source_access_filter(client: TestClient) -> None:
    response = client.get(
        "/api/v1/lint-issue-catalog",
        params={"source_access": "paywall", "family": "lint"},
    )
    assert response.status_code == 200
    rows = response.json()["issues"]
    assert rows
    assert all(row.get("source_access") == "paywall" for row in rows)
    assert any(row["code"] == "AMD_PRESENT" for row in rows)


def test_lint_issue_catalog_lint_row_has_ev062_fields(client: TestClient) -> None:
    response = client.get("/api/v1/lint-issue-catalog", params={"family": "lint"})
    assert response.status_code == 200
    amd = next(row for row in response.json()["issues"] if row["code"] == "AMD_PRESENT")
    assert amd.get("issue_type") == "presence"
    assert amd.get("source_locator")
    assert amd.get("source_access") == "paywall"
