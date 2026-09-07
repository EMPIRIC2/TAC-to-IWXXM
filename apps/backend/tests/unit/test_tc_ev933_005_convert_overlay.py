"""TC-EV933-005 — convert overlay_id fail-closed + apply metadata."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.api import app
from src.schemas.conversion_profiles import OverlayOut
from src.utilities.security import verify_optional_supabase_token

USER_ID = uuid4()
OVERLAY_ID = uuid4()
NOW = datetime(2026, 9, 4, tzinfo=UTC)


@pytest.fixture
def convert_client() -> Any:
    async def override_optional() -> dict[str, str]:
        return {"sub": str(USER_ID)}

    app.dependency_overrides[verify_optional_supabase_token] = override_optional
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _overlay() -> OverlayOut:
    return OverlayOut(
        id=OVERLAY_ID,
        user_id=USER_ID,
        slug="ov",
        base_profile_id="ICAO_2025",
        body={},
        signature="c" * 64,
        shared=False,
        created_at=NOW,
        updated_at=NOW,
    )


def test_convert_overlay_requires_auth() -> None:
    client = TestClient(app)
    res = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
            "product": "METAR",
            "overlay_id": str(OVERLAY_ID),
        },
    )
    assert res.status_code in {401, 403}


def test_convert_overlay_unknown_id(convert_client: Any) -> None:
    client = convert_client
    with patch("src.routers.conversion.ConversionProfilesService") as svc_cls:
        svc_cls.return_value.get_overlay.side_effect = HTTPException(status_code=404, detail="Overlay not found")
        res = client.post(
            "/api/v1/convert",
            data={
                "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
                "product": "METAR",
                "overlay_id": str(OVERLAY_ID),
            },
            headers={"Authorization": "Bearer t"},
        )
    assert res.status_code == 404


def test_convert_overlay_invalid_uuid(convert_client: Any) -> None:
    client = convert_client
    res = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
            "product": "METAR",
            "overlay_id": "not-a-uuid",
        },
        headers={"Authorization": "Bearer t"},
    )
    assert res.status_code == 400
    assert "Unknown overlay" in str(res.json().get("detail", ""))


def test_convert_overlay_applies_base_when_profile_empty(convert_client: Any) -> None:
    client = convert_client
    with (
        patch("src.routers.conversion.ConversionProfilesService") as svc_cls,
        patch("src.routers.conversion.tac_lint_fn", return_value=MagicMock(ok=True, issues=[])),
        patch(
            "src.api.convert_metar_tac_with_metadata",
            return_value=("<xml/>", {}),
        ),
    ):
        svc_cls.return_value.get_overlay.return_value = _overlay()
        res = client.post(
            "/api/v1/convert",
            data={
                "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
                "product": "METAR",
                "overlay_id": str(OVERLAY_ID),
                "semantic_profile": "",
                "profile": "",
                "lint": "false",
            },
            headers={"Authorization": "Bearer t"},
        )
    assert res.status_code != 401
    assert res.status_code != 403
    assert res.status_code != 404
    if res.status_code == 200:
        meta = res.json().get("metadata") or {}
        assert meta.get("overlay_id") == str(OVERLAY_ID)
        assert meta.get("overlay_base_profile") == "ICAO_2025"


def test_convert_overlay_keeps_explicit_profile(convert_client: Any) -> None:
    client = convert_client
    with (
        patch("src.routers.conversion.ConversionProfilesService") as svc_cls,
        patch("src.routers.conversion.tac_lint_fn", return_value=MagicMock(ok=True, issues=[])),
        patch(
            "src.api.convert_metar_tac_with_metadata",
            return_value=("<xml/>", {}),
        ),
    ):
        empty_base = _overlay().model_copy(update={"base_profile_id": ""})
        svc_cls.return_value.get_overlay.return_value = empty_base
        res = client.post(
            "/api/v1/convert",
            data={
                "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
                "product": "METAR",
                "overlay_id": str(OVERLAY_ID),
                "semantic_profile": "US_FAA_NWS",
                "lint": "false",
            },
            headers={"Authorization": "Bearer t"},
        )
    assert res.status_code != 401
    if res.status_code == 200:
        meta = res.json().get("metadata") or {}
        assert meta.get("overlay_id") == str(OVERLAY_ID)
        assert "overlay_base_profile" not in meta
