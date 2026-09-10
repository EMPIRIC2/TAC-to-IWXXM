"""TC-EV1120-001..005 — profile filters on GET /lint-issue-catalog (#1121).

Spec: docs/api-contract.md §Lint issue catalog; EV-1120 Phase A.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token() -> dict[str, str]:
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _codes(response_json: dict) -> set[str]:
    return {row["code"] for row in response_json["issues"]}


def test_tc_ev1120_001_omit_params_preserves_prior_behavior(client: TestClient) -> None:
    """Omit semantic/exchange params → same issue set as unfiltered baseline."""
    baseline = client.get("/api/v1/lint-issue-catalog")
    assert baseline.status_code == 200
    filtered = client.get("/api/v1/lint-issue-catalog")
    assert filtered.status_code == 200
    assert _codes(filtered.json()) == _codes(baseline.json())
    assert len(filtered.json()["issues"]) == len(baseline.json()["issues"])


def test_tc_ev1120_002_semantic_profile_shared_union_matching(client: TestClient) -> None:
    """Filter returns shared plus profile-applicable; national-only omitted elsewhere."""
    icao = client.get(
        "/api/v1/lint-issue-catalog",
        params={"semantic_profile": "ICAO_2025"},
    )
    assert icao.status_code == 200
    icao_codes = _codes(icao.json())

    us = client.get(
        "/api/v1/lint-issue-catalog",
        params={"semantic_profile": "US_FAA_NWS"},
    )
    assert us.status_code == 200
    us_codes = _codes(us.json())

    ca = client.get(
        "/api/v1/lint-issue-catalog",
        params={"semantic_profile": "CA_ECCC"},
    )
    assert ca.status_code == 200
    ca_codes = _codes(ca.json())

    # Shared terminator remains under every known semantic profile
    assert "MISSING_TERMINATOR" in icao_codes
    assert "MISSING_TERMINATOR" in us_codes
    assert "MISSING_TERMINATOR" in ca_codes

    # US-tagged national TAF rule must not appear under ICAO-only filter
    assert "US_TAF_BECMG_FORBIDDEN" not in icao_codes
    assert "US_TAF_BECMG_FORBIDDEN" in us_codes

    # CA-tagged national TAC rule
    assert "CA_METAR_LWIS" not in icao_codes
    assert "CA_METAR_LWIS" not in us_codes
    assert "CA_METAR_LWIS" in ca_codes

    # IWXXM-family rows can also be profile-scoped by applicability tags
    assert "IWXXM_US_EXTENSION" not in icao_codes
    assert "IWXXM_US_EXTENSION" in us_codes
    assert "IWXXM_US_EXTENSION" not in ca_codes
    assert "IWXXM_CA_EXTENSION" not in icao_codes
    assert "IWXXM_CA_EXTENSION" not in us_codes
    assert "IWXXM_CA_EXTENSION" in ca_codes


def test_tc_ev1120_003_unknown_semantic_profile_400(client: TestClient) -> None:
    response = client.get(
        "/api/v1/lint-issue-catalog",
        params={"semantic_profile": "NOT_A_REAL_PROFILE"},
    )
    assert response.status_code == 400
    detail = response.json().get("detail", response.json())
    if isinstance(detail, dict):
        assert detail.get("code") == "invalid_semantic_profile"
    else:
        assert "invalid_semantic_profile" in response.text


def test_tc_ev1120_004_exchange_profile_filter_and_unknown(client: TestClient) -> None:
    ok = client.get(
        "/api/v1/lint-issue-catalog",
        params={"exchange_profile": "GLOBAL_AFS"},
    )
    assert ok.status_code == 200
    assert "MISSING_TERMINATOR" in _codes(ok.json())

    bad = client.get(
        "/api/v1/lint-issue-catalog",
        params={"exchange_profile": "NOT_AN_EXCHANGE"},
    )
    assert bad.status_code == 400
    detail = bad.json().get("detail", bad.json())
    if isinstance(detail, dict):
        assert detail.get("code") == "invalid_exchange_profile"
    else:
        assert "invalid_exchange_profile" in bad.text


def test_tc_ev1120_005_catalog_rows_expose_semantic_profiles_field(
    client: TestClient,
) -> None:
    """Additive semantic_profiles / exchange_profiles on rows (older clients ignore)."""
    response = client.get("/api/v1/lint-issue-catalog")
    assert response.status_code == 200
    rows = response.json()["issues"]
    assert rows
    for row in rows:
        assert "semantic_profiles" in row
        assert "exchange_profiles" in row
        assert isinstance(row["semantic_profiles"], list)
        assert isinstance(row["exchange_profiles"], list)

    us_row = next(r for r in rows if r["code"] == "US_TAF_BECMG_FORBIDDEN")
    assert "us_faa_nws" in us_row["semantic_profiles"]
    assert us_row["semantic_profiles"]  # national-only, not empty shared

    ca_iwxxm_row = next(r for r in rows if r["code"] == "IWXXM_CA_EXTENSION")
    assert ca_iwxxm_row["family"] == "iwxxm"
    assert "ca_eccc" in ca_iwxxm_row["semantic_profiles"]
