"""F7 UI↔API connection-point integration (S011 / EV-008).

Mirrors shapes consumed by ``apps/frontend/src/utils/api.ts`` and
``workSessionApi.ts`` so each workbench wiring surface stays aligned with the
backend. Complements ``test_frontend_contract_integration.py`` (legacy convert)
and H0i CORS tests.

Spec: docs/api-contract.md (lint-tac, decode-tac, soft-preview, work-sessions);
docs/test-plan.md TC-F7-002–005; connectivity-gates H0i.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.utilities.security import verify_supabase_token

FIXTURES = Path(__file__).resolve().parents[4] / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "product_matrix"
VALID_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
BAD_METAR_TAC = "METAR XXXX NOT_A_REAL_REPORT GARBAGE="
BROWSER_ORIGIN = "http://localhost:18000"
USER_ID = uuid4()

pytestmark = [pytest.mark.integration]


@pytest.fixture
def client() -> TestClient:
    """Authenticated TestClient matching frontend Bearer calls."""

    async def override_verify_token():
        return {"sub": str(USER_ID), "aud": "test-project"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def _assert_optional_offsets(item: dict[str, Any]) -> None:
    """Frontend LintIssue / FailedSpan may include optional character offsets."""
    if "start" in item and item["start"] is not None:
        assert isinstance(item["start"], int)
    if "end" in item and item["end"] is not None:
        assert isinstance(item["end"], int)
        if item.get("start") is not None:
            assert item["start"] <= item["end"]


class TestUiLintTacConnection:
    """UI connection: live workbench → POST /api/v1/lint-tac."""

    def test_lint_tac_response_matches_frontend_lint_tac_response(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/lint-tac",
            files={
                "manual_text": (None, VALID_METAR),
                "product": (None, "METAR"),
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload["ok"], bool)
        assert isinstance(payload["issues"], list)
        assert isinstance(payload["fixes"], list)
        for issue in payload["issues"]:
            assert isinstance(issue["severity"], str)
            assert isinstance(issue["code"], str)
            assert isinstance(issue["message"], str)
            _assert_optional_offsets(issue)
        for fix in payload["fixes"]:
            assert isinstance(fix["code"], str)
            assert isinstance(fix["message"], str)
            assert "replacement" in fix


class TestUiDecodeTacConnection:
    """UI connection: decode panel → POST /api/v1/decode-tac."""

    def test_decode_tac_response_matches_frontend_decode_tac_response(self, client: TestClient) -> None:
        tac = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
        response = client.post(
            "/api/v1/decode-tac",
            files={
                "manual_text": (None, tac),
                "product": (None, "METAR"),
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload["product"], str)
        assert isinstance(payload["segments"], list)
        assert isinstance(payload["residuals"], list)
        assert payload["segments"], "golden METAR must yield decode segments for UI"
        for seg in payload["segments"]:
            assert isinstance(seg["start"], int)
            assert isinstance(seg["end"], int)
            assert isinstance(seg["code"], str)
            assert isinstance(seg["explanation"], str)
        for residual in payload["residuals"]:
            assert isinstance(residual["start"], int)
            assert isinstance(residual["end"], int)
            assert isinstance(residual["text"], str)


class TestUiSoftPreviewConnection:
    """UI connection: soft-preview toggle → convert preview=true + Failed-TAC cue."""

    def test_convert_preview_envelope_matches_frontend_conversion_response(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/convert",
            files={
                "manual_text": (None, BAD_METAR_TAC),
                "product": (None, "METAR"),
                "profile": (None, "annex3"),
                "lint": (None, "false"),
                "preview": (None, "true"),
            },
        )
        assert response.status_code == 200
        payload = response.json()
        # Core ConversionResponse fields (api.ts)
        assert isinstance(payload["results"], list)
        assert isinstance(payload["errors"], list)
        assert isinstance(payload["total_processed"], int)
        assert isinstance(payload["successful"], int)
        assert isinstance(payload["failed"], int)
        # Soft-preview envelope (ADR-022 / FailedTacCue)
        assert "ok" in payload
        assert isinstance(payload["failed_spans"], list)
        assert payload["ok"] is False or len(payload["failed_spans"]) >= 1
        for span in payload["failed_spans"]:
            assert isinstance(span["start"], int)
            assert isinstance(span["end"], int)
            _assert_optional_offsets(span)


class TestUiWorkSessionsConnection:
    """F21 / F7.h: work-sessions HTTP is gone; FE uses IndexedDB."""

    def test_work_sessions_http_gone_for_frontend(self, client: TestClient) -> None:
        created = client.post(
            "/api/v1/work-sessions",
            headers={"Authorization": "Bearer t"},
            json={
                "product": "taf",
                "status": "draft",
                "title": "TAF draft",
                "manual_tac": "TAF KJFK 121730Z 1218/1324 18010KT=",
            },
        )
        assert created.status_code == 404, created.text

        listed = client.get(
            "/api/v1/work-sessions?product=metar,speci",
            headers={"Authorization": "Bearer t"},
        )
        assert listed.status_code == 404


class TestUiBrowserCorsConnection:
    """UI connection: browser Origin preflight for F7 live-assist routes."""

    @pytest.fixture
    def cors_client(self, monkeypatch: pytest.MonkeyPatch) -> TestClient:
        monkeypatch.setenv("DISABLE_AUTH", "false")
        monkeypatch.setenv("METAR_CONFIG_ENV", "local")
        monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")

        from src.utilities import security as sec

        monkeypatch.setattr(sec, "DISABLE_AUTH", False)

        async def _auth_user() -> dict[str, str]:
            return {"sub": "f7-cors-user", "aud": "test"}

        app.dependency_overrides[verify_supabase_token] = _auth_user
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.mark.parametrize(
        "path",
        ["/api/v1/lint-tac", "/api/v1/decode-tac", "/api/v1/convert"],
    )
    def test_options_f7_endpoints_allow_post(self, cors_client: TestClient, path: str) -> None:
        response = cors_client.options(
            path,
            headers={
                "Origin": BROWSER_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "POST" in allow_methods.upper()
        allow_origin = response.headers.get("access-control-allow-origin", "")
        assert allow_origin in {BROWSER_ORIGIN, "*"}
