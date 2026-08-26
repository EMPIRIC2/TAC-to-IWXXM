"""Direct coverage for TD-3b extracted routers."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.responses import Response

from src import api as api_module
from src.routers import conversion_meta, health, tac_quality

METAR_TAC = "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034="


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_module.app)


def test_health_router_degraded_on_convert_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from src import api as api_surface

    def boom(*_a, **_k):
        raise RuntimeError("convert down")

    monkeypatch.setattr(api_surface, "convert_metar_tac_with_metadata", boom)
    result = health.health()
    assert result.status == "degraded"
    assert result.tac2iwxxm_available is False


def test_health_endpoint_via_router(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_conversion_meta_versions_and_schema_status() -> None:
    versions = conversion_meta.get_supported_versions()
    assert "default_version" in versions
    assert isinstance(versions["supported_versions"], list)

    status = conversion_meta.get_schema_status()
    assert "stable" in status
    assert "profile_pins" in status


def test_conversion_meta_endpoints(client: TestClient) -> None:
    versions = client.get("/api/v1/versions")
    assert versions.status_code == 200
    schema = client.get("/api/v1/schema-status")
    assert schema.status_code == 200


@pytest.mark.asyncio
async def test_tac_quality_lint_issue_catalog_returns_response() -> None:
    response = await tac_quality.lint_issue_catalog()
    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_tac_quality_lint_issue_catalog_invalid_family_and_issue_type_filter() -> None:
    response = await tac_quality.lint_issue_catalog(family="bogus", issue_type="nonexistent-type-xyz")
    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_tac_quality_decode_tac_wrong_content_type() -> None:
    request = MagicMock()
    request.headers.get.return_value = "application/json"
    with pytest.raises(HTTPException) as exc:
        await tac_quality.decode_tac_endpoint(
            request,
            product="METAR",
            manual_text=METAR_TAC,
            files=None,
        )
    assert exc.value.status_code == 415


@pytest.mark.asyncio
async def test_tac_quality_lint_tac_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    request = MagicMock()
    request.headers.get.return_value = "multipart/form-data"

    response = await tac_quality.lint_tac(request, manual_text=METAR_TAC, product="METAR", files=None)
    assert isinstance(response, Response)

    response_iwxxm = await tac_quality.lint_tac(request, manual_text="<xml/>", product="IWXXM", files=None)
    assert isinstance(response_iwxxm, Response)

    request.headers.get.return_value = "application/json"
    with pytest.raises(HTTPException) as exc:
        await tac_quality.lint_tac(request, manual_text=METAR_TAC, product="METAR", files=None)
    assert exc.value.status_code == 415


@pytest.mark.asyncio
async def test_tac_quality_decode_tac_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    request = MagicMock()
    request.headers.get.return_value = "multipart/form-data"
    response = await tac_quality.decode_tac_endpoint(
        request,
        product="METAR",
        manual_text=METAR_TAC,
        files=None,
    )
    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_tac_quality_lint_tac_upload_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    from src import api as api_surface

    request = MagicMock()
    request.headers.get.return_value = "multipart/form-data"
    upload = MagicMock()

    async def reject_files(_files):
        return None, "bad file"

    monkeypatch.setattr(api_surface, "read_upload_files_text", reject_files)
    with pytest.raises(HTTPException) as exc:
        await tac_quality.lint_tac(request, manual_text="", product="METAR", files=[upload])
    assert exc.value.status_code == 400

    async def accept_files(_files):
        return METAR_TAC, None

    monkeypatch.setattr(api_surface, "read_upload_files_text", accept_files)
    response = await tac_quality.lint_tac(request, manual_text="", product="METAR", files=[upload])
    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_tac_quality_decode_tac_upload_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    from src import api as api_surface

    request = MagicMock()
    request.headers.get.return_value = "multipart/form-data"

    async def reject_files(_files):
        return None, "bad file"

    monkeypatch.setattr(api_surface, "read_upload_files_text", reject_files)
    with pytest.raises(HTTPException):
        await tac_quality.decode_tac_endpoint(
            request,
            product="METAR",
            manual_text="",
            files=[MagicMock()],
        )


def test_tac_quality_http_routes(client: TestClient) -> None:
    lint = client.post(
        "/api/v1/lint-tac",
        files={"manual_text": (None, METAR_TAC), "product": (None, "METAR")},
    )
    assert lint.status_code == 200
    decode = client.post(
        "/api/v1/decode-tac",
        files={"manual_text": (None, METAR_TAC), "product": (None, "METAR")},
    )
    assert decode.status_code == 200
    catalog = client.get("/api/v1/lint-issue-catalog")
    assert catalog.status_code == 200
