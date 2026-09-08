"""Direct coverage for TD-3b extracted routers."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src import api as api_module
from src.routers import conversion_meta, health, tac_quality
from starlette.responses import Response

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


def test_tac_quality_advisory_explanation_variants() -> None:
    assert tac_quality._advisory_explanation("VONA", "DTG") == "Issue time"
    assert tac_quality._advisory_explanation("VONA", "VOLCANO") == "Volcano"
    assert tac_quality._advisory_explanation("VONA", "UNKNOWN_LABEL") == "Unknown Label"
    assert tac_quality._advisory_explanation("SWXA", "SWXC") == "Center"
    assert tac_quality._advisory_explanation("SWXA", "FCST SWX +6 HR") == "Forecast +6 hours"
    assert tac_quality._advisory_explanation("SWXA", "ODD_LABEL") == "Odd Label"


def test_tac_quality_enrich_advisory_decode_passthrough_and_empty_cases() -> None:
    segments, residuals, summary = tac_quality._enrich_advisory_decode(
        "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034=",
        product="METAR",
        segments=[SimpleNamespace(start=0, end=5, code="METAR", explanation="Type")],
        residuals=[SimpleNamespace(start=6, end=10, text="rest")],
        summary="existing summary",
    )
    assert summary == "existing summary"
    assert [(s.start, s.end, s.code, s.explanation) for s in segments] == [(0, 5, "METAR", "Type")]
    assert [(r.start, r.end, r.text) for r in residuals] == [(6, 10, "rest")]

    empty_segments, empty_residuals, empty_summary = tac_quality._enrich_advisory_decode(
        "",
        product="VONA",
        segments=[],
        residuals=[],
        summary=None,
    )
    assert empty_segments == []
    assert empty_residuals == []
    assert empty_summary == ""


def test_tac_quality_enrich_advisory_decode_vona_builds_segments_and_summary() -> None:
    tac = """VONA
DTG: 20240216/0130Z
VOLCANO: KARYMSKY 300130
CURRENT COLOUR CODE: YELLOW
RMK: Line one
 continuation text
"""
    segments, residuals, summary = tac_quality._enrich_advisory_decode(
        tac,
        product="VONA",
        segments=[],
        residuals=[SimpleNamespace(start=0, end=len(tac), text=tac)],
        summary=None,
    )
    assert residuals == []
    assert any(s.explanation == "Notice type" and s.code == "VONA" for s in segments)
    assert any(s.explanation == "Issue time" and s.code == "20240216/0130Z" for s in segments)
    assert any(s.explanation == "Volcano" and s.code == "KARYMSKY 300130" for s in segments)
    assert any(s.explanation == "Current colour code" and s.code == "YELLOW" for s in segments)
    assert any(s.explanation == "Remarks" and s.code == "Line one continuation text" for s in segments)
    assert summary == "VONA for KARYMSKY 300130. Current colour code YELLOW."


def test_tac_quality_enrich_advisory_decode_swxa_builds_segments_and_summary() -> None:
    tac = """SWX ADVISORY
SWXC: DONLON
SWX EFFECT: HF COM
NXT ADVISORY: WILL BE ISSUED BY 20201108/0700Z
"""
    segments, residuals, summary = tac_quality._enrich_advisory_decode(
        tac,
        product="SWXA",
        segments=[],
        residuals=[SimpleNamespace(start=0, end=len(tac), text=tac)],
        summary="fallback",
    )
    assert residuals == []
    assert any(s.explanation == "Advisory header" and s.code == "SWX ADVISORY" for s in segments)
    assert any(s.explanation == "Center" and s.code == "DONLON" for s in segments)
    assert any(s.explanation == "Effect" and s.code == "HF COM" for s in segments)
    assert any(s.explanation == "Next advisory" and s.code == "WILL BE ISSUED BY 20201108/0700Z" for s in segments)
    assert summary == "SWX advisory from DONLON. Effect: HF COM."


def test_tac_quality_enrich_advisory_decode_returns_original_residuals_when_unparsed() -> None:
    residual = SimpleNamespace(start=2, end=7, text="leftover")
    segments, residuals, summary = tac_quality._enrich_advisory_decode(
        "plain text without advisory labels",
        product="SWXA",
        segments=[],
        residuals=[residual],
        summary="fallback summary",
    )
    assert segments == []
    assert [(r.start, r.end, r.text) for r in residuals] == [(2, 7, "leftover")]
    assert summary == "fallback summary"


def test_tac_quality_enrich_advisory_decode_branch_gaps_without_optional_fields() -> None:
    vona_tac = """VONA

DTG: 20240216/0130Z
"""
    vona_segments, vona_residuals, vona_summary = tac_quality._enrich_advisory_decode(
        vona_tac,
        product="VONA",
        segments=[],
        residuals=[SimpleNamespace(start=0, end=len(vona_tac), text=vona_tac)],
        summary="fallback summary",
    )
    assert vona_residuals == []
    assert any(s.explanation == "Notice type" for s in vona_segments)
    assert any(s.explanation == "Issue time" for s in vona_segments)
    assert vona_summary == "fallback summary"

    swxa_tac = """SWX ADVISORY

SWXC: DONLON
"""
    swxa_segments, swxa_residuals, swxa_summary = tac_quality._enrich_advisory_decode(
        swxa_tac,
        product="SWXA",
        segments=[],
        residuals=[SimpleNamespace(start=0, end=len(swxa_tac), text=swxa_tac)],
        summary="fallback summary",
    )
    assert swxa_residuals == []
    assert any(s.explanation == "Advisory header" for s in swxa_segments)
    assert any(s.explanation == "Center" for s in swxa_segments)
    assert swxa_summary == "SWX advisory from DONLON."


def test_tac_quality_enrich_advisory_decode_swxa_without_center_keeps_effect_summary() -> None:
    swxa_tac = """SWX ADVISORY
SWX EFFECT: HF COM
"""
    segments, residuals, summary = tac_quality._enrich_advisory_decode(
        swxa_tac,
        product="SWXA",
        segments=[],
        residuals=[SimpleNamespace(start=0, end=len(swxa_tac), text=swxa_tac)],
        summary="fallback summary",
    )
    assert residuals == []
    assert any(s.explanation == "Advisory header" for s in segments)
    assert any(s.explanation == "Effect" and s.code == "HF COM" for s in segments)
    assert summary == "Effect: HF COM."


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
