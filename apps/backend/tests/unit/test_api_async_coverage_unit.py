"""Async coverage tests for api.py JSON body paths.

These tests use httpx.AsyncClient with ASGITransport to drive the FastAPI app
natively (no sync-to-async bridge).  Running as real async tests ensures that
coverage.py can trace every ``await`` resumption point in Python 3.11+, where
the sync TestClient approach sometimes misses lines after ``await`` expressions.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from src import api as api_module
from src.schemas.validation import (
    AggregatedValidationResult,
    ValidationLayer,
    ValidationResult,
)
from src.utilities.security import verify_supabase_token

# ---------------------------------------------------------------------------
# Helper stubs
# ---------------------------------------------------------------------------


class _PassValidationService:
    def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
        return AggregatedValidationResult.from_results(
            [
                ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO),
                ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX),
            ]
        )


class _FailValidationService:
    def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
        return AggregatedValidationResult.from_results(
            [ValidationResult(passed=False, layer=ValidationLayer.AIRPORT_ICAO)]
        )


class _AsyncStatsService:
    async def log_translation(self, **_kwargs: Any) -> str:
        return "test-id"


class _AsyncWebhookService:
    async def notify_translation_failed(self, **_kwargs: Any) -> None:
        return None

    async def notify_translation_success(self, **_kwargs: Any) -> None:
        return None

    async def notify_translation_completed(self, **_kwargs: Any) -> None:
        return None

    async def notify_bulk_completed(self, **_kwargs: Any) -> None:
        return None


def _fake_convert(
    _tac: str,
    iwxxm_version: str = "2025-2",
    validate: bool = False,
    **_kwargs: Any,
) -> tuple[str, None]:
    xml = f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>'
    return xml, None


async def _override_verify_token() -> dict:
    return {"sub": "test-user", "aud": "test-aud"}


# ---------------------------------------------------------------------------
# Async fixture - shared client
# ---------------------------------------------------------------------------


@pytest.fixture
async def async_client(monkeypatch):
    """httpx.AsyncClient backed by the real ASGI app with stubs injected."""
    monkeypatch.setattr(api_module, "ValidationService", _PassValidationService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", _fake_convert)
    monkeypatch.setattr(api_module, "statistics_service", _AsyncStatsService())
    monkeypatch.setattr(api_module, "webhook_service", _AsyncWebhookService())

    api_module.app.dependency_overrides[verify_supabase_token] = _override_verify_token

    transport = httpx.ASGITransport(app=api_module.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    api_module.app.dependency_overrides.clear()


@pytest.fixture
async def async_client_fail_validation(monkeypatch):
    """Like async_client but the validation service always fails."""
    monkeypatch.setattr(api_module, "ValidationService", _FailValidationService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", _fake_convert)
    monkeypatch.setattr(api_module, "statistics_service", _AsyncStatsService())
    monkeypatch.setattr(api_module, "webhook_service", _AsyncWebhookService())

    api_module.app.dependency_overrides[verify_supabase_token] = _override_verify_token

    transport = httpx.ASGITransport(app=api_module.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    api_module.app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# /api/v1/convert  -  JSON body path (covers lines ~977-994 + 1131-1339)
# ---------------------------------------------------------------------------


async def test_convert_json_body_success(async_client):
    """JSON metars list → successful conversion (covers request_body block + loop)."""
    response = await async_client.post(
        "/api/v1/convert",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"]},
        headers={"authorization": "Bearer test"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] >= 1


async def test_convert_json_body_multiple_metars(async_client):
    """Multiple JSON metars processed in the loop."""
    response = await async_client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KLAX 010000Z 00000KT CAVOK 15/10 Q1013",
                "",  # blank entry - exercises the 'continue' branch
            ]
        },
        headers={"authorization": "Bearer test"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 2


async def test_convert_json_body_validation_failed(async_client_fail_validation):
    """JSON metar fails input validation → all failed → 400."""
    response = await async_client_fail_validation.post(
        "/api/v1/convert",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"]},
        headers={"authorization": "Bearer test"},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["errors"]


async def test_convert_json_body_invalid_schema(async_client):
    """Invalid version in JSON body → 422 (covers pydantic error block ~871-876)."""
    response = await async_client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"],
            "version": "totally-invalid-version-xyz",
        },
        headers={"authorization": "Bearer test"},
    )
    assert response.status_code == 422


async def test_convert_json_body_invalid_json(async_client):
    """Malformed JSON body → 422 (covers JSON parse error block)."""
    response = await async_client.post(
        "/api/v1/convert",
        content=b"{bad-json",
        headers={
            "authorization": "Bearer test",
            "content-type": "application/json",
        },
    )
    assert response.status_code == 422


async def test_convert_json_body_stop_on_error(async_client_fail_validation):
    """stop_on_error=true with validation failure → loop breaks, all failed → 400."""
    response = await async_client_fail_validation.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KLAX 010000Z 00000KT CAVOK 15/10 Q1013",
            ],
            "stop_on_error": True,
        },
        headers={"authorization": "Bearer test"},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# /api/v1/convert/zip  -  JSON body path (covers lines ~2068-2207)
# ---------------------------------------------------------------------------


async def test_convert_zip_json_body_success(async_client):
    """JSON metars list to convert-zip → success (covers metars_list loop in convert_zip)."""
    response = await async_client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"]},
        headers={"authorization": "Bearer test"},
    )
    assert response.status_code == 200


async def test_convert_zip_json_body_multiple_metars(async_client):
    """Multiple JSON metars in convert-zip loop."""
    response = await async_client.post(
        "/api/v1/convert-zip",
        json={
            "metars": [
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KLAX 010000Z 00000KT CAVOK 15/10 Q1013",
                "",  # blank - exercises continue branch
            ]
        },
        headers={"authorization": "Bearer test"},
    )
    assert response.status_code == 200


async def test_convert_zip_json_body_validation_failed(async_client_fail_validation):
    """JSON metar fails validation in convert-zip loop → zip with errors.txt (200)."""
    response = await async_client_fail_validation.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"]},
        headers={"authorization": "Bearer test"},
    )
    assert response.status_code == 200
