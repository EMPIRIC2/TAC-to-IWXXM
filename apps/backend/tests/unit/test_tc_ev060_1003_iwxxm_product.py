"""TC-EV060-1003 / UJ-060: product=iwxxm pass-through (F7.t / #1003).

Spec: docs/test-plan.md TC-EV060-1003-001..002; [Corpus: api] [Corpus: tests]
[Corpus: product §F7].
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.iwxxm_pass_through import (
    NOT_WELLFORMED_XML_CODE,
    NOT_XML_CODE,
    lint_iwxxm_pass_through,
)
from src.utilities.security import verify_supabase_token

GOLDEN_XML = (
    Path(__file__).resolve().parents[4]
    / "packages"
    / "tac2iwxxm"
    / "tests"
    / "fixtures"
    / "annex3_golden"
    / "metar_basic.golden.xml"
)

TAC_SAMPLE = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


def test_normalize_api_product_accepts_iwxxm() -> None:
    assert api_module.normalize_api_product("iwxxm") == "IWXXM"
    assert api_module.normalize_api_product("IWXXM") == "IWXXM"


def test_lint_iwxxm_pass_through_empty_and_malformed() -> None:
    empty = lint_iwxxm_pass_through("   ")
    assert empty.ok is False
    assert empty.issues[0].code == NOT_XML_CODE
    malformed = lint_iwxxm_pass_through("<iwxxm:METAR>")
    assert malformed.ok is False
    assert malformed.issues[0].code == NOT_WELLFORMED_XML_CODE


def test_tc_ev060_1003_001_lint_tac_xml_pass_through(client: TestClient) -> None:
    """Valid IWXXM XML under product=iwxxm is not TAC-linted as METAR."""
    xml = GOLDEN_XML.read_text(encoding="utf-8")
    response = _multipart(
        client,
        "/api/v1/lint-tac",
        {"manual_text": xml, "product": "iwxxm"},
    )
    assert response.status_code == 200, response.text[:400]
    payload = response.json()
    assert payload["ok"] is True
    codes = [i["code"] for i in payload["issues"]]
    assert "MISSING_PRODUCT_KEYWORD" not in codes
    assert "NOT_XML" not in codes


def test_tc_ev060_1003_002_lint_tac_text_is_not_xml(client: TestClient) -> None:
    """TAC text under product=iwxxm returns structured NOT_XML (not METAR flood)."""
    response = _multipart(
        client,
        "/api/v1/lint-tac",
        {"manual_text": TAC_SAMPLE, "product": "iwxxm"},
    )
    assert response.status_code == 200, response.text[:400]
    payload = response.json()
    assert payload["ok"] is False
    codes = [i["code"] for i in payload["issues"]]
    assert "NOT_XML" in codes
    assert "MISSING_PRODUCT_KEYWORD" not in codes
    assert "INVALID_WIND" not in codes


def test_tc_ev060_1003_001_convert_xml_no_tac_convert(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Convert with product=iwxxm returns XML pass-through; TAC convert never runs."""
    xml = GOLDEN_XML.read_text(encoding="utf-8")
    called: list[str] = []

    def boom(*_a, **_k):
        called.append("convert")
        raise AssertionError("TAC convert must not run for product=iwxxm")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", boom)

    response = _multipart(
        client,
        "/api/v1/convert",
        {
            "manual_text": xml,
            "product": "iwxxm",
            "validate_output": "false",
        },
    )
    assert response.status_code == 200, response.text[:500]
    assert called == []
    body = response.json()
    assert body["successful"] >= 1
    assert body["results"][0]["content"].strip().startswith("<")
    assert "iwxxm" in body["results"][0]["content"].lower()


def test_tc_ev060_1003_002_convert_tac_text_not_xml(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Convert TAC text with product=iwxxm fails with NOT_XML; no TAC convert."""

    def boom(*_a, **_k):
        raise AssertionError("TAC convert must not run for product=iwxxm")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", boom)

    response = _multipart(
        client,
        "/api/v1/convert",
        {"manual_text": TAC_SAMPLE, "product": "iwxxm"},
    )
    assert response.status_code in (400, 422), response.text[:500]
    detail = response.json().get("detail") or response.json()
    issues = detail.get("issues") if isinstance(detail, dict) else None
    if issues is None and isinstance(detail, dict):
        issues = detail.get("issues") or []
    codes = [i.get("code") for i in (issues or []) if isinstance(i, dict)]
    blob = response.text
    assert "NOT_XML" in codes or "NOT_XML" in blob
    assert "MISSING_PRODUCT_KEYWORD" not in blob


def test_tc_ev060_1003_001_convert_bulletin_xml_pass_through(client: TestClient) -> None:
    """Bulletin convert with product=iwxxm returns XML without AHL split."""
    xml = GOLDEN_XML.read_text(encoding="utf-8")
    response = _multipart(
        client,
        "/api/v1/convert-bulletin",
        {"manual_text": xml, "product": "iwxxm"},
    )
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload["results"][0]["ok"] is True
    assert payload["results"][0]["xml"].strip().startswith("<")


def test_tc_ev060_1003_002_convert_bulletin_tac_not_xml(client: TestClient) -> None:
    """Bulletin convert TAC text with product=iwxxm is NOT_XML."""
    response = _multipart(
        client,
        "/api/v1/convert-bulletin",
        {"manual_text": TAC_SAMPLE, "product": "iwxxm"},
    )
    assert response.status_code == 400, response.text[:500]
    blob = response.text
    assert "NOT_XML" in blob
    assert "MISSING_PRODUCT_KEYWORD" not in blob


def test_tc_ev060_1003_openapi_product_describes_iwxxm() -> None:
    """OpenAPI convert/lint/bulletin product fields mention iwxxm pass-through."""
    schema = api_module.app.openapi()
    components = schema["components"]["schemas"]
    convert_body = components["Body_convert_api_v1_convert_post"]
    assert "iwxxm" in convert_body["properties"]["product"]["description"].lower()
    lint_body = components["Body_lint_tac_api_v1_lint_tac_post"]
    assert "iwxxm" in lint_body["properties"]["product"]["description"].lower()
    bulletin_body = components["Body_convert_bulletin_api_v1_convert_bulletin_post"]
    assert "iwxxm" in bulletin_body["properties"]["product"]["description"].lower()
