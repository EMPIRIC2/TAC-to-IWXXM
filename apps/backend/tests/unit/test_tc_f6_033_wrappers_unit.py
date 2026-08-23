"""TC-F6-033 / T2.5: API contract for /lint-tac + /validate package wrappers."""

from __future__ import annotations

import inspect

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart_lint(
    client: TestClient,
    *,
    manual_text: str,
    product: str = "METAR",
):
    """POST /lint-tac as multipart/form-data (Q8=A; TestClient data= alone is urlencoded)."""
    return client.post(
        "/api/v1/lint-tac",
        files={
            "manual_text": (None, manual_text),
            "product": (None, product),
        },
    )


def test_lint_tac_route_exists_multipart(client: TestClient) -> None:
    """POST /api/v1/lint-tac accepts multipart and returns ok/issues/fixes."""
    response = _multipart_lint(client, manual_text="")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert isinstance(payload["issues"], list)
    assert len(payload["issues"]) >= 1
    assert "severity" in payload["issues"][0]
    assert "code" in payload["issues"][0]
    assert "message" in payload["issues"][0]
    assert isinstance(payload.get("fixes", []), list)


def test_lint_tac_metar_pass(client: TestClient) -> None:
    response = _multipart_lint(
        client,
        manual_text="METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034=",
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["issues"] == []


def test_lint_tac_reads_uploaded_files(client: TestClient) -> None:
    """File parts are concatenated into TAC text (api lint-tac upload path)."""
    tac = "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034="
    response = client.post(
        "/api/v1/lint-tac",
        files=[
            ("product", (None, "METAR")),
            ("manual_text", (None, "")),
            ("files", ("a.tac", tac.encode("utf-8"), "text/plain")),
            ("files", ("empty.tac", b"", "text/plain")),
        ],
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_lint_tac_rejects_json_content_type(client: TestClient) -> None:
    """Q8=A: multipart only."""
    response = client.post(
        "/api/v1/lint-tac",
        json={"manual_text": "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034=", "product": "METAR"},
    )
    assert response.status_code in {415, 422}


def test_lint_tac_rejects_urlencoded(client: TestClient) -> None:
    """Q8=A: application/x-www-form-urlencoded is not accepted."""
    response = client.post(
        "/api/v1/lint-tac",
        data={"manual_text": "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034=", "product": "METAR"},
    )
    assert response.status_code == 415


def test_validate_accepts_profile_and_calls_iwxxm_validate(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Thin wrapper must invoke iwxxm_validate.validate (TC-F6-033) and map package fields."""
    calls: list[dict[str, object]] = []

    def fake_validate(xml: str, *, iwxxm_version: str, profile: str = "annex3", levels=None, product=None):
        calls.append(
            {
                "xml": xml,
                "iwxxm_version": iwxxm_version,
                "profile": profile,
                "levels": levels,
            }
        )
        from iwxxm_validate import Issue, ValidationReport

        return ValidationReport(
            ok=False,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[
                Issue(
                    severity="error",
                    code="E001",
                    message="Example package issue",
                    layer="xsd",
                    location="line 1, col 1",
                )
            ],
        )

    monkeypatch.setattr("iwxxm_validate.validate", fake_validate)
    monkeypatch.setattr("src.api.iwxxm_validate_fn", fake_validate, raising=False)

    xml = """<?xml version="1.0"?><root xmlns="http://icao.int/iwxxm/2023-1"/>"""
    response = client.post(
        "/api/v1/validate",
        files={
            "xml_content": (None, xml),
            "iwxxm_version": (None, "2023-1"),
            "profile": (None, "annex3"),
            "layers": (None, "XML_WELLFORMED"),
        },
    )
    assert response.status_code == 200
    assert calls, "expected iwxxm_validate.validate to be called"
    assert calls[0]["profile"] == "annex3"
    assert calls[0]["iwxxm_version"]


def test_convert_lint_form_defaults_true() -> None:
    """Q14=C: convert `lint` form flag defaults to True."""
    sig = inspect.signature(api_module.convert)
    lint_param = sig.parameters.get("lint")
    assert lint_param is not None, "convert() must declare lint form parameter"
    default = lint_param.default
    # FastAPI Form defaults expose .default
    assert getattr(default, "default", default) is True
