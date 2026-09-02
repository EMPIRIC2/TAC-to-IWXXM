"""EV-981 / TC-EV981 API — propagate_residuals_to_remarks Form wire."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.utilities.security import verify_supabase_token

pytestmark = [pytest.mark.integration]

_TAC = "METAR KJFK 251451Z 18005KT 10SM FEW050 ZZZZ 22/12 A2992 RMK AO2 SLP123="


def _multipart_post(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


@pytest.fixture
def api_client() -> Iterator[TestClient]:
    async def _auth_user() -> dict[str, str]:
        return {"sub": "ev981-api-user", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _issue_codes(body: dict) -> list[str]:
    codes: list[str] = []
    for issue in body.get("issues") or []:
        code = issue.get("code")
        if code:
            codes.append(str(code))
    return codes


def test_tc_ev981_api_omit_default_off_no_propagate_issue(api_client: TestClient) -> None:
    resp = _multipart_post(
        api_client,
        "/api/v1/convert",
        {
            "manual_text": _TAC,
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "lint": "false",
        },
    )
    assert resp.status_code == 200, resp.text[:800]
    body = resp.json()
    assert "RESIDUALS_PROPAGATED_TO_REMARKS" not in _issue_codes(body)
    results = body.get("results") or []
    assert results
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert "ZZZZ" not in xml


def test_tc_ev981_api_flag_on_iwxxm_us_folds_residual(api_client: TestClient) -> None:
    resp = _multipart_post(
        api_client,
        "/api/v1/convert",
        {
            "manual_text": _TAC,
            "product": "METAR",
            "profile": "iwxxm_us",
            "iwxxm_version": "2025-2",
            "lint": "false",
            "propagate_residuals_to_remarks": "true",
        },
    )
    assert resp.status_code == 200, resp.text[:800]
    body = resp.json()
    assert "RESIDUALS_PROPAGATED_TO_REMARKS" in _issue_codes(body)
    results = body.get("results") or []
    assert results
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert "ZZZZ" in xml
    assert "humanReadableText" in xml


def test_tc_ev981_api_annex3_flag_on_documents_no_xml_target(api_client: TestClient) -> None:
    resp = _multipart_post(
        api_client,
        "/api/v1/convert",
        {
            "manual_text": _TAC,
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "lint": "false",
            "propagate_residuals_to_remarks": "true",
        },
    )
    assert resp.status_code == 200, resp.text[:800]
    body = resp.json()
    codes = _issue_codes(body)
    assert "RESIDUALS_PROPAGATED_TO_REMARKS" in codes
    results = body.get("results") or []
    assert results
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert "ZZZZ" not in xml
    assert "humanReadableText" not in xml
    prop = next(i for i in (body.get("issues") or []) if i.get("code") == "RESIDUALS_PROPAGATED_TO_REMARKS")
    assert "no xml" in str(prop.get("message") or "").lower()
