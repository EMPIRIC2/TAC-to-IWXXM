"""TC-EV933 / EV-bridge — overlay_id hard-cut on Convert (unlinked from Convert)."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_optional_supabase_token

_SAMPLE_METAR = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="
OVERLAY_ID = uuid4()


@pytest.fixture
def convert_client() -> Any:
    async def _guest():
        return None

    api_module.app.dependency_overrides[verify_optional_supabase_token] = _guest
    client = TestClient(api_module.app)
    yield client
    api_module.app.dependency_overrides.clear()


def test_convert_overlay_id_rejected(convert_client: Any) -> None:
    res = convert_client.post(
        "/api/v1/convert",
        data={
            "manual_text": _SAMPLE_METAR,
            "product": "METAR",
            "overlay_id": str(OVERLAY_ID),
            "lint": "false",
        },
    )
    assert res.status_code == 422, res.text[:500]
    assert "overlay_id" in res.text
    assert "Legacy convert fields" in res.text


def test_convert_json_body_overlay_id_rejected(convert_client: Any) -> None:
    res = convert_client.post(
        "/api/v1/convert",
        json={
            "metars": [_SAMPLE_METAR],
            "version": "2025-2",
            "overlay_id": str(OVERLAY_ID),
        },
    )
    assert res.status_code == 422, res.text[:500]
    assert "overlay_id" in res.text
