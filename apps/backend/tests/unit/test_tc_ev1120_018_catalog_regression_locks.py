"""TC-EV1120-018 — fail-closed regression locks for profile-scoped catalog criteria.

Locks mined national codes, filter matrix semantics, and provenance URL rules from
UJ-073 / EV-1120 so future catalog updates cannot silently regress #1121-#1123.

[Corpus: tests] [Corpus: product §F15] [Corpus: api]
"""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

# Planning-token patterns forbidden in operator-visible attribution (EV-048).
_INTERNAL_DOC_REF = re.compile(r"(?i)(\[Corpus:|docs/sessions/|ADR-\d+|EV-\d+|#\d{3,}|TC-EV|UJ-\d+|F\d{1,2}\.[a-z])")

# National-only TAC + IWXXM codes that must stay profile-scoped (mining notes).
_US_NATIONAL_ONLY = frozenset(
    {
        "US_TAF_BECMG_FORBIDDEN",
        "US_TAF_TEMPO_MAX_4H",
        "US_TAF_PROB40_NOT_USED",
        "US_METAR_STATUTE_MILE_VIS",
        "US_METAR_INHG_ALTIMETER",
        "IWXXM_US_EXTENSION",
        "IWXXM_US_ADDENDUM_REMARKS",
    }
)
_CA_NATIONAL_ONLY = frozenset(
    {
        "CA_METAR_LWIS",
        "CA_METAR_UP_AWOS_ONLY",
        "IWXXM_CA_EXTENSION",
        "IWXXM_CA_CODE_REGISTRY",
    }
)
_SHARED_ALWAYS = frozenset({"MISSING_TERMINATOR"})


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


def _rows_by_code(response_json: dict) -> dict[str, dict]:
    return {row["code"]: row for row in response_json["issues"]}


def test_tc_ev1120_018_icao_excludes_national_only_demo_codes(client: TestClient) -> None:
    """ICAO_2025 must not surface US/CA national-only demo codes (UJ-073 step 1)."""
    icao = _codes(
        client.get(
            "/api/v1/lint-issue-catalog",
            params={"semantic_profile": "ICAO_2025"},
        ).json()
    )
    assert icao >= _SHARED_ALWAYS
    assert icao.isdisjoint(_US_NATIONAL_ONLY)
    assert icao.isdisjoint(_CA_NATIONAL_ONLY)


def test_tc_ev1120_018_us_profile_includes_us_national_only(client: TestClient) -> None:
    """US_FAA_NWS returns shared union US national-only; CA-only stays hidden."""
    payload = client.get(
        "/api/v1/lint-issue-catalog",
        params={"semantic_profile": "US_FAA_NWS"},
    ).json()
    us = _codes(payload)
    assert us >= _SHARED_ALWAYS
    assert us >= _US_NATIONAL_ONLY
    assert us.isdisjoint(_CA_NATIONAL_ONLY)


def test_tc_ev1120_018_ca_profile_includes_ca_national_only(client: TestClient) -> None:
    """CA_ECCC returns shared union CA national-only; US-only stays hidden."""
    payload = client.get(
        "/api/v1/lint-issue-catalog",
        params={"semantic_profile": "CA_ECCC"},
    ).json()
    ca = _codes(payload)
    assert ca >= _SHARED_ALWAYS
    assert ca >= _CA_NATIONAL_ONLY
    assert ca.isdisjoint(_US_NATIONAL_ONLY)


def test_tc_ev1120_018_mined_rows_keep_https_provenance(client: TestClient) -> None:
    """Mined deepen codes keep public https provenance (no planning-token attribution)."""
    required = {
        "US_TAF_PROB40_NOT_USED": "US_FAA_NWS",
        "US_METAR_STATUTE_MILE_VIS": "US_FAA_NWS",
        "US_METAR_INHG_ALTIMETER": "US_FAA_NWS",
        "CA_METAR_UP_AWOS_ONLY": "CA_ECCC",
        "IWXXM_US_ADDENDUM_REMARKS": "US_FAA_NWS",
        "IWXXM_CA_CODE_REGISTRY": "CA_ECCC",
    }
    for code, profile in required.items():
        payload = client.get(
            "/api/v1/lint-issue-catalog",
            params={"semantic_profile": profile},
        ).json()
        row = _rows_by_code(payload)[code]
        url = row.get("source_url") or ""
        assert url.startswith("https://"), f"{code} missing https provenance"
        attribution = row.get("source_attribution") or ""
        assert _INTERNAL_DOC_REF.search(attribution) is None, (
            f"{code} attribution leaks planning tokens: {attribution!r}"
        )


def test_tc_ev1120_018_omit_params_preserves_full_catalog(client: TestClient) -> None:
    """Omit semantic/exchange params -> full catalog (older clients unchanged)."""
    baseline = client.get("/api/v1/lint-issue-catalog")
    assert baseline.status_code == 200
    codes = _codes(baseline.json())
    assert codes >= _US_NATIONAL_ONLY
    assert codes >= _CA_NATIONAL_ONLY
    assert codes >= _SHARED_ALWAYS


def test_tc_ev1120_018_unknown_profiles_still_400(client: TestClient) -> None:
    """Unknown profile query params remain fail-closed HTTP 400."""
    bad_sem = client.get(
        "/api/v1/lint-issue-catalog",
        params={"semantic_profile": "NOT_A_REAL_PROFILE"},
    )
    assert bad_sem.status_code == 400
    bad_ex = client.get(
        "/api/v1/lint-issue-catalog",
        params={"exchange_profile": "NOT_AN_EXCHANGE"},
    )
    assert bad_ex.status_code == 400
