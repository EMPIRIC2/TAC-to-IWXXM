"""TC-EV060-1003 / UJ-060: product=iwxxm pass-through (F7.t / #1003).

Spec: docs/test-plan.md TC-EV060-1003-001..002; [Corpus: api] [Corpus: tests]
[Corpus: product §F7].
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.routers import conversion as conversion_router
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
IWXXM_2023_1_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR
    xmlns:iwxxm='http://icao.int/iwxxm/2023-1'
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://icao.int/iwxxm/2023-1 https://schemas.wmo.int/iwxxm/2023-1/iwxxm.xsd"
    gml:id="metar-1">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="ti-1">
      <gml:timePosition>2026-09-07T18:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:runwayState>REMOVE_ME</iwxxm:runwayState>
</iwxxm:METAR>
"""


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


def test_tc_ev908_iwxxm_product_migrates_between_supported_lines(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """IWXXM upload can migrate to a requested supported target version."""
    validate_calls: list[dict[str, str]] = []

    def fake_validate(xml_payload: str, **kwargs):
        validate_calls.append(
            {
                "xml": xml_payload,
                "iwxxm_version": str(kwargs.get("iwxxm_version")),
            }
        )
        return type("Report", (), {"ok": True, "issues": []})()

    monkeypatch.setattr(conversion_router.api_surface, "_call_iwxxm_validate", fake_validate)

    response = _multipart(
        client,
        "/api/v1/convert",
        {
            "manual_text": IWXXM_2023_1_SAMPLE,
            "product": "iwxxm",
            "iwxxm_version": "2025-2",
            "validate_output": "false",
        },
    )

    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    content = payload["results"][0]["content"]
    assert "http://icao.int/iwxxm/2025-2" in content
    assert "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd" in content
    assert "runwayState" not in content
    assert payload["metadata"]["pass_through"] is True
    assert payload["metadata"]["source_iwxxm_version"] == "2023-1"
    assert payload["metadata"]["target_iwxxm_version"] == "2025-2"
    assert payload["metadata"]["migrated_iwxxm"] is True
    assert validate_calls
    assert validate_calls[0]["iwxxm_version"] == "2025-2"
    assert "http://icao.int/iwxxm/2025-2" in validate_calls[0]["xml"]


def test_tc_ev908_iwxxm_product_migration_fails_closed_on_invalid_output(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Migrated IWXXM must validate cleanly before convert returns success."""

    def fake_validate(_xml_payload: str, **_kwargs):
        return type(
            "Report",
            (),
            {
                "ok": False,
                "issues": [
                    type(
                        "Issue",
                        (),
                        {
                            "message": "schema mismatch after migration",
                            "code": "IWXXM_SCHEMA",
                            "location": "line 1",
                            "layer": "xsd",
                        },
                    )()
                ],
            },
        )()

    monkeypatch.setattr(conversion_router.api_surface, "_call_iwxxm_validate", fake_validate)

    response = _multipart(
        client,
        "/api/v1/convert",
        {
            "manual_text": IWXXM_2023_1_SAMPLE,
            "product": "iwxxm",
            "iwxxm_version": "2025-2",
            "validate_output": "false",
        },
    )

    assert response.status_code == 400, response.text[:500]
    detail = response.json()["detail"]
    assert detail["message"] == "Migrated IWXXM did not validate for the requested target version"
    assert detail["issues"][0]["code"] == "IWXXM_SCHEMA"
    assert detail["issues"][0]["severity"] == "error"


def test_tc_ev908_iwxxm_product_rejects_unknown_source_namespace(client: TestClient) -> None:
    response = _multipart(
        client,
        "/api/v1/convert",
        {
            "manual_text": "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2026-9'/>",
            "product": "iwxxm",
            "validate_output": "true",
        },
    )

    assert response.status_code == 400, response.text[:500]
    detail = response.json()["detail"]
    assert detail["message"] == "Unsupported IWXXM source version"


def test_tc_ev908_iwxxm_product_migration_validate_exception_fails_closed(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(_xml_payload: str, **_kwargs):
        raise RuntimeError("validator unavailable")

    monkeypatch.setattr(conversion_router.api_surface, "_call_iwxxm_validate", boom)

    response = _multipart(
        client,
        "/api/v1/convert",
        {
            "manual_text": IWXXM_2023_1_SAMPLE,
            "product": "iwxxm",
            "iwxxm_version": "2025-2",
            "validation_level": "schematron",
        },
    )

    assert response.status_code == 400, response.text[:500]
    detail = response.json()["detail"]
    assert detail["message"] == "Migrated IWXXM validation could not complete"


def test_tc_ev060_1003_migrated_iwxxm_validation_failure_fails_closed(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        api_module,
        "_call_iwxxm_validate",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            issues=[SimpleNamespace(message="schema fail", code="IWXXM_SCHEMA", layer="xsd", location="/")],
        ),
    )

    response = _multipart(
        client,
        "/api/v1/convert",
        {
            "manual_text": IWXXM_2023_1_SAMPLE,
            "product": "iwxxm",
            "iwxxm_version": "2025-2",
            "validate_output": "true",
        },
    )

    assert response.status_code == 400, response.text[:500]
    detail = response.json()["detail"]
    assert detail["message"] == "Migrated IWXXM did not validate for the requested target version"
    assert detail["issues"][0]["code"] == "IWXXM_SCHEMA"
