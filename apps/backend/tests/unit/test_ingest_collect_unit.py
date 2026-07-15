"""Unit tests for POST /api/v1/ingest-collect placeholder (ADR-024)."""

from __future__ import annotations

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


def test_ingest_collect_requires_multipart(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ingest-collect",
        data={"manual_text": "<collect/>", "profile": "annex3"},
    )
    assert response.status_code == 415


def test_ingest_collect_empty_payload_400(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ingest-collect",
        files={"manual_text": (None, "   "), "profile": (None, "annex3")},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "empty_collect"


def test_ingest_collect_placeholder_501(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ingest-collect",
        files={
            "manual_text": (None, "<iwxxm:MeteorologicalBulletin></iwxxm:MeteorologicalBulletin>"),
            "profile": (None, "annex3"),
            "iwxxm_version": (None, "2025-2"),
        },
    )
    assert response.status_code == 501
    detail = response.json()["detail"]
    assert detail["code"] == "not_implemented"


def test_ingest_collect_from_file_upload_501(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ingest-collect",
        files={
            "files": ("collect.xml", b"<collect>member</collect>", "application/xml"),
            "profile": (None, "annex3"),
        },
    )
    assert response.status_code == 501
    assert response.json()["detail"]["code"] == "not_implemented"


def test_ingest_collect_rejects_bad_upload(client: TestClient, monkeypatch) -> None:
    async def boom(_files):
        return None, "empty file"

    monkeypatch.setattr(api_module, "read_upload_files_text", boom)
    response = client.post(
        "/api/v1/ingest-collect",
        files={
            "files": ("empty.gz", b"", "application/gzip"),
            "profile": (None, "annex3"),
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "upload_rejected"


def test_convert_logs_include_nil_reasons_false(client: TestClient) -> None:
    """ADR-024: include_nil_reasons=false is accepted and logged."""
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="),
            "preview": (None, "true"),
            "product": (None, "METAR"),
            "include_nil_reasons": (None, "false"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200
