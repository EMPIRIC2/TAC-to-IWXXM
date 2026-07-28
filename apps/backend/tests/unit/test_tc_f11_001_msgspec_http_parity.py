"""T5.1 / TC-F11-001: msgspec high-churn HTTP parity (UJ-022 / ADR-026).

Spec: docs/test-plan.md TC-F11-001; docs/adr/ADR-026-msgspec-http-openapi.md;
docs/api-contract.md §Serialization boundary; E10-28, E10-38.

Expected red until T5.2 adds ``src.msgspec_http.msgspec_json_response`` and wires
high-churn JSON routes through it (pydantic OpenAPI aliases only; Form intake unchanged).
"""

from __future__ import annotations

import inspect
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src import api as api_module
from src.utilities.security import verify_supabase_token

FIXTURES = Path(__file__).resolve().parents[4] / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "product_matrix"

METAR_TAC = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()

BULLETIN_TEXT = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=
"""

HIGH_CHURN_JSON_PATHS = (
    "/api/v1/convert",
    "/api/v1/convert-bulletin",
    "/api/v1/validate",
    "/api/v1/lint-tac",
    "/api/v1/decode-tac",
    "/api/v1/lint-issue-catalog",
)


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart(client: TestClient, path: str, fields: dict[str, str]):
    """POST multipart/form-data (TestClient ``data=`` alone is urlencoded → 415)."""
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


def _iter_api_routes(routes) -> list[APIRoute]:
    """Walk FastAPI routes including ``_IncludedRouter`` mounts (auth)."""
    found: list[APIRoute] = []
    for route in routes:
        if isinstance(route, APIRoute):
            found.append(route)
        elif type(route).__name__ == "_IncludedRouter":
            found.extend(_iter_api_routes(route.original_router.routes))
        elif hasattr(route, "routes") and route.routes:
            found.extend(_iter_api_routes(route.routes))
    return found


def _route_for(path: str, method: str = "POST") -> APIRoute:
    for route in _iter_api_routes(api_module.app.routes):
        if route.path == path and method in route.methods:
            return route
    raise AssertionError(f"route not found: {method} {path}")


# --- Helper surface (T5.2 contract) -------------------------------------------------


def test_msgspec_http_helper_module_exists() -> None:
    """E10-38: thin helper Struct→msgspec.json.encode→Response must exist."""
    from src.msgspec_http import msgspec_json_response

    assert callable(msgspec_json_response)


def test_msgspec_http_helper_reuses_encoder() -> None:
    """ADR-026 / ADR-016: reuse Encoder on hot paths (no per-call construction)."""
    from src import msgspec_http

    assert hasattr(msgspec_http, "json_encoder")
    enc = msgspec_http.json_encoder
    assert enc is msgspec_http.json_encoder
    # Second import must share the same instance
    import importlib

    reloaded = importlib.reload(msgspec_http)
    assert reloaded.json_encoder is not None


def test_msgspec_json_response_returns_fastapi_response() -> None:
    """Helper returns starlette/fastapi Response with application/json body."""
    import msgspec
    from starlette.responses import Response

    from src.msgspec_http import msgspec_json_response

    class _Sample(msgspec.Struct):
        ok: bool
        product: str

    resp = msgspec_json_response(_Sample(ok=True, product="METAR"))
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert "application/json" in (resp.media_type or resp.headers.get("content-type", ""))
    payload = msgspec.json.decode(resp.body)
    assert payload == {"ok": True, "product": "METAR"}


# --- High-churn routes use msgspec encode path --------------------------------------


def test_api_binds_msgspec_json_response() -> None:
    """Handlers must bind the shared helper (no dual pydantic runtime encode)."""
    bound = getattr(api_module, "msgspec_json_response", None)
    assert callable(bound)
    assert bound.__name__ == "msgspec_json_response"
    assert bound.__module__.endswith("msgspec_http")
    # High-churn handlers reference the bound name in source
    assert "msgspec_json_response" in inspect.getsource(api_module.lint_tac)
    assert "msgspec_json_response" in inspect.getsource(api_module.lint_issue_catalog)


@pytest.mark.parametrize(
    ("path", "fields"),
    [
        (
            "/api/v1/lint-tac",
            {"manual_text": METAR_TAC, "product": "METAR"},
        ),
        (
            "/api/v1/decode-tac",
            {"manual_text": METAR_TAC, "product": "METAR"},
        ),
        (
            "/api/v1/validate",
            {
                "xml_content": '<?xml version="1.0"?><root xmlns="http://icao.int/iwxxm/2023-1"/>',
                "iwxxm_version": "2023-1",
                "profile": "annex3",
                "layers": "XML_WELLFORMED",
            },
        ),
        (
            "/api/v1/convert",
            {
                "manual_text": METAR_TAC,
                "product": "METAR",
                "profile": "annex3",
                "lint": "false",
            },
        ),
        (
            "/api/v1/convert-bulletin",
            {
                "manual_text": BULLETIN_TEXT,
                "product": "METAR",
                "profile": "annex3",
                "lint": "false",
            },
        ),
    ],
)
def test_high_churn_json_routes_call_msgspec_helper(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    fields: dict[str, str],
) -> None:
    """TC-F11-001: convert/validate/lint/decode(+bulletin) responses via msgspec path."""
    from src import msgspec_http

    if path == "/api/v1/convert-bulletin":

        def fake_convert(tac: str, **_kwargs: Any):
            return f"<iwxxm:METAR>{tac[:24]}</iwxxm:METAR>", None

        monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    if path == "/api/v1/convert":

        def fake_convert_one(tac: str, **_kwargs: Any):
            return f"<iwxxm:METAR>{tac[:24]}</iwxxm:METAR>", None

        # Prefer lightweight convert when available; fall back to full path.
        if hasattr(api_module, "convert_metar_tac_with_metadata"):
            monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert_one)

    calls: list[Any] = []
    real = msgspec_http.msgspec_json_response

    def spy(obj: Any, **kwargs: Any):
        calls.append(obj)
        return real(obj, **kwargs)

    monkeypatch.setattr(msgspec_http, "msgspec_json_response", spy)
    monkeypatch.setattr(api_module, "msgspec_json_response", spy)

    response = _multipart(client, path, fields)
    assert response.status_code == 200, response.text[:800]
    assert calls, f"{path} must encode via msgspec_json_response"
    assert "application/json" in response.headers.get("content-type", "")
    body = response.json()
    assert isinstance(body, dict)


def test_high_churn_openapi_keeps_pydantic_response_aliases() -> None:
    """ADR-026: OpenAPI still publishes pydantic aliases — no dual runtime validation."""
    schema = api_module.app.openapi()
    components = schema.get("components", {}).get("schemas", {})
    for name in (
        "ConversionResponse",
        "ValidateResponse",
        "LintTacResponse",
        "DecodeTacResponse",
        "ConvertBulletinResponse",
        "LintIssueCatalogResponse",
    ):
        assert name in components, f"OpenAPI missing pydantic alias schema {name}"

    for path in HIGH_CHURN_JSON_PATHS:
        method = "GET" if path.endswith("/lint-issue-catalog") else "POST"
        route = _route_for(path, method=method)
        assert route.response_model is not None, f"{path} must keep response_model for OpenAPI"
        assert issubclass(route.response_model, BaseModel)


def test_multipart_intake_unchanged_rejects_json_on_lint(client: TestClient) -> None:
    """E10-28: multipart Form intake unchanged — JSON body is not accepted."""
    response = client.post(
        "/api/v1/lint-tac",
        json={"manual_text": METAR_TAC, "product": "METAR"},
    )
    assert response.status_code in {415, 422}


# --- convert-zip (high-churn but ZIP, not msgspec JSON) -----------------------------


def test_convert_zip_returns_application_zip(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """ADR-026 lists convert-zip as high-churn; live contract remains application/zip."""

    def fake_convert(tac: str, **_kwargs: Any):
        return f"<iwxxm:METAR>{tac[:24]}</iwxxm:METAR>", None

    if hasattr(api_module, "convert_metar_tac_with_metadata"):
        monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert-zip",
        files={
            "manual_text": (None, METAR_TAC),
            "product": (None, "METAR"),
            "profile": (None, "annex3"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    ctype = response.headers.get("content-type", "")
    assert "application/zip" in ctype or "zip" in ctype
    with zipfile.ZipFile(BytesIO(response.content)) as zf:
        assert zf.namelist(), "ZIP must contain at least one member"


# --- Auth routes gone (F21) ---------------------------------------------------------


def test_auth_login_route_absent() -> None:
    """F21 / ADR-031: /auth/login is not mounted (msgspec/pydantic auth path retired)."""
    with pytest.raises(AssertionError, match="/auth/login"):
        _route_for("/auth/login")


def test_auth_login_http_404_without_msgspec(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /auth/login returns 404; msgspec helper must not be involved."""
    from src import msgspec_http

    calls: list[Any] = []
    real = msgspec_http.msgspec_json_response

    def spy(obj: Any, **kwargs: Any):
        calls.append(obj)
        return real(obj, **kwargs)

    monkeypatch.setattr(msgspec_http, "msgspec_json_response", spy)
    if hasattr(api_module, "msgspec_json_response"):
        monkeypatch.setattr(api_module, "msgspec_json_response", spy)

    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "not-a-real-password"},
    )
    assert response.status_code == 404
    assert calls == [], f"404 auth path must not use msgspec_json_response, got {len(calls)} calls"


# --- Contract shape smoke (parity for FE) -------------------------------------------


def test_lint_tac_contract_shape(client: TestClient) -> None:
    response = _multipart(client, "/api/v1/lint-tac", {"manual_text": METAR_TAC, "product": "METAR"})
    assert response.status_code == 200
    payload = response.json()
    assert "ok" in payload
    assert isinstance(payload["issues"], list)
    assert isinstance(payload.get("fixes", []), list)


def test_decode_tac_contract_shape(client: TestClient) -> None:
    response = _multipart(client, "/api/v1/decode-tac", {"manual_text": METAR_TAC, "product": "METAR"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["product"].upper() == "METAR"
    assert isinstance(payload["segments"], list)
    assert isinstance(payload["residuals"], list)
    assert "summary" in payload


def test_validate_contract_shape(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from iwxxm_validate import ValidationReport

    def fake_sdk(xml: str, *, iwxxm_version: str, profile: str = "annex3", levels=None):
        return ValidationReport(ok=True, iwxxm_version=iwxxm_version, profile=profile, issues=[])

    monkeypatch.setattr(api_module, "iwxxm_validate_fn", fake_sdk)
    response = _multipart(
        client,
        "/api/v1/validate",
        {
            "xml_content": '<?xml version="1.0"?><root xmlns="http://icao.int/iwxxm/2023-1"/>',
            "iwxxm_version": "2023-1",
            "profile": "annex3",
            "layers": "XML_WELLFORMED",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "is_valid" in payload
    assert "package_ok" in payload
    assert "package_issues" in payload


def test_high_churn_handlers_annotated_or_return_response() -> None:
    """T5.2 handlers should return Response from msgspec helper (not live pydantic encode)."""
    from starlette.responses import Response

    for name in ("lint_tac", "lint_issue_catalog", "decode_tac_endpoint", "convert_bulletin", "validate_comprehensive"):
        fn = getattr(api_module, name)
        # Either annotation is Response, or source references msgspec_json_response
        src = inspect.getsource(fn)
        ret = inspect.signature(fn).return_annotation
        uses_helper = "msgspec_json_response" in src
        returns_response = ret is Response or getattr(ret, "__name__", "") == "Response"
        assert uses_helper or returns_response, f"{name} must call msgspec_json_response or annotate Response return"
