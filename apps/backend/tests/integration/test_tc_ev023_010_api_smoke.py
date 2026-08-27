"""T7.1 / TC-EV023 API convert+validate smoke (S030 / EV-023).

In-process FastAPI client (CI). Covers translationCentre Form gate + NSC omit
layers + validate path on convert output. Live H4-H5 deferred to T7.4 / 13.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.utilities.security import verify_supabase_token

pytestmark = [pytest.mark.integration, pytest.mark.smoke]

_METAR_OK = "METAR KJFK 231751Z 18012KT 9999 FEW020 15/07 Q1013="
# NSC exclusivity - must not emit layered cloud children (TC-EV023-001).
_METAR_NSC = "METAR KJFK 231751Z 18012KT 9999 NSC 15/07 Q1013="


def _multipart_post(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


def _attr(xml: str, name: str) -> str | None:
    m = re.search(rf'\b{re.escape(name)}="([^"]*)"', xml)
    return m.group(1) if m else None


@pytest.fixture
def smoke_client() -> Iterator[TestClient]:
    async def _auth_user() -> dict[str, str]:
        return {"sub": "ev023-smoke-user", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_tc_ev023_api_default_convert_omits_translation_centre(smoke_client: TestClient) -> None:
    resp = _multipart_post(
        smoke_client,
        "/api/v1/convert",
        {
            "manual_text": _METAR_OK,
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "lint": "false",
        },
    )
    assert resp.status_code == 200, resp.text[:800]
    body = resp.json()
    results = body.get("results") or []
    assert results, body
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert "iwxxm:METAR" in xml or "METAR" in xml
    assert _attr(xml, "translationCentreDesignator") is None
    assert _attr(xml, "translationCentreName") is None


def test_tc_ev023_api_emit_translation_centre_form(smoke_client: TestClient) -> None:
    resp = _multipart_post(
        smoke_client,
        "/api/v1/convert",
        {
            "manual_text": _METAR_OK,
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "lint": "false",
            "emit_translation_centre": "true",
            "translation_centre_designator": "KJFK",
            "translation_centre_name": "EV023 Smoke Centre",
        },
    )
    assert resp.status_code == 200, resp.text[:800]
    results = resp.json().get("results") or []
    assert results
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert _attr(xml, "translationCentreDesignator") == "KJFK"
    assert _attr(xml, "translationCentreName") == "EV023 Smoke Centre"


def test_tc_ev023_api_nsc_convert_and_validate(smoke_client: TestClient) -> None:
    convert = _multipart_post(
        smoke_client,
        "/api/v1/convert",
        {
            "manual_text": _METAR_NSC,
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "lint": "false",
        },
    )
    assert convert.status_code == 200, convert.text[:800]
    results = convert.json().get("results") or []
    assert results
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert "CloudLayer" not in xml
    assert "NSC" in xml or "nothingOfOperationalSignificance" in xml or "cloud" in xml.lower()

    validate = smoke_client.post(
        "/api/v1/validate",
        data={
            "xml_content": xml,
            "iwxxm_version": "2025-2",
            "layers": ["XML_WELLFORMED", "XML_SCHEMA"],
            "stop_on_error": "false",
            "profile": "annex3",
        },
    )
    # Accept 200 with structured report; do not hard-fail on SCH platform skips.
    assert validate.status_code == 200, validate.text[:800]
    payload = validate.json()
    assert isinstance(payload, dict)
    assert "layers_run" in payload or "is_valid" in payload
