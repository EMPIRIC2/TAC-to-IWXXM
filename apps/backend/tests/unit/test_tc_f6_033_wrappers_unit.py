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


def test_lint_tac_route_exists_multipart(client: TestClient) -> None:
    """POST /api/v1/lint-tac accepts multipart and returns ok/issues/fixes."""
    response = client.post(
        "/api/v1/lint-tac",
        data={"manual_text": "", "product": "METAR"},
    )
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
    response = client.post(
        "/api/v1/lint-tac",
        data={
            "manual_text": "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034=",
            "product": "METAR",
        },
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["issues"] == []


def test_lint_tac_rejects_json_content_type(client: TestClient) -> None:
    """Q8=A: multipart only."""
    response = client.post(
        "/api/v1/lint-tac",
        json={"manual_text": "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034=", "product": "METAR"},
    )
    assert response.status_code in {415, 422}


def test_validate_accepts_profile_and_calls_iwxxm_validate(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Thin wrapper must invoke iwxxm_validate.validate (TC-F6-033)."""
    calls: list[dict[str, object]] = []

    def fake_validate(xml: str, *, iwxxm_version: str, profile: str = "annex3", levels=None):
        calls.append(
            {
                "xml": xml,
                "iwxxm_version": iwxxm_version,
                "profile": profile,
                "levels": levels,
            }
        )
        from iwxxm_validate import Issue, ValidationReport

        return ValidationReport(ok=True, iwxxm_version=iwxxm_version, profile=profile, issues=[])

    monkeypatch.setattr("iwxxm_validate.validate", fake_validate)
    # Also patch where the wrapper imports it if bound differently
    monkeypatch.setattr("src.api.iwxxm_validate_fn", fake_validate, raising=False)

    xml = """<?xml version="1.0"?><root xmlns="http://icao.int/iwxxm/2023-1"/>"""
    response = client.post(
        "/api/v1/validate",
        json={"iwxxm_xml": xml, "version": "2023-1", "validation_level": "schema", "profile": "annex3"},
    )
    # Wrapper may still return aggregated F2 shape; must be success path
    assert response.status_code == 200
    assert calls, "expected iwxxm_validate.validate to be called"


def test_convert_lint_form_defaults_true() -> None:
    """Q14=C: convert `lint` form flag defaults to True."""
    sig = inspect.signature(api_module.convert)
    lint_param = sig.parameters.get("lint")
    assert lint_param is not None, "convert() must declare lint form parameter"
    default = lint_param.default
    # FastAPI Form defaults expose .default
    assert getattr(default, "default", default) is True
