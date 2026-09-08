"""TC-EV1051-001 — convert preset_id fail-closed + apply metadata."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.schemas.conversion_profiles import PresetOut
from src.utilities.security import verify_optional_supabase_token

USER_ID = uuid4()
PRESET_ID = uuid4()
NOW = datetime(2026, 9, 7, tzinfo=UTC)


@pytest.fixture
def convert_client() -> Any:
    async def override_optional() -> dict[str, str]:
        return {"sub": str(USER_ID)}

    app.dependency_overrides[verify_optional_supabase_token] = override_optional
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _preset() -> PresetOut:
    return PresetOut(
        id=PRESET_ID,
        user_id=USER_ID,
        slug="ca-lwis",
        name="CA LWIS",
        semantic_profile="CA_ECCC",
        iwxxm_version="3.0.0",
        extensions=[],
        report_variant="LWIS",
        overlay_id=None,
        shared=False,
        created_at=NOW,
        updated_at=NOW,
    )


def test_convert_preset_requires_auth() -> None:
    client = TestClient(app)
    res = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
            "product": "METAR",
            "preset_id": str(PRESET_ID),
        },
    )
    assert res.status_code in {401, 403}


def test_convert_preset_applies_defaults_when_request_omits_them(convert_client: Any) -> None:
    client = convert_client
    seen: list[dict[str, Any]] = []

    def fake_convert(tac: str, **kwargs: Any) -> tuple[str, dict[str, Any] | None]:
        seen.append(kwargs)
        return "<xml/>", None

    with (
        patch("src.routers.conversion.ConversionProfilesService") as svc_cls,
        patch("src.routers.conversion.tac_lint_fn", return_value=MagicMock(ok=True, issues=[])),
        patch("src.api.convert_metar_tac_with_metadata", side_effect=fake_convert),
    ):
        svc_cls.return_value.get_preset.return_value = _preset()
        res = client.post(
            "/api/v1/convert",
            data={
                "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
                "product": "METAR",
                "preset_id": str(PRESET_ID),
                "semantic_profile": "",
                "report_variant": "",
                "iwxxm_version": "",
                "lint": "false",
            },
            headers={"Authorization": "Bearer t"},
        )

    assert res.status_code == 200, res.text
    assert seen
    assert seen[0]["profile"] == "ca_eccc"
    assert seen[0]["report_variant"] == "LWIS"
    meta = res.json().get("metadata") or {}
    assert meta.get("preset_id") == str(PRESET_ID)
    assert meta.get("semantic_profile") == "ca_eccc"
    assert meta.get("report_variant") == "LWIS"


def test_convert_preset_keeps_explicit_request_fields(convert_client: Any) -> None:
    client = convert_client
    seen: list[dict[str, Any]] = []

    def fake_convert(tac: str, **kwargs: Any) -> tuple[str, dict[str, Any] | None]:
        seen.append(kwargs)
        return "<xml/>", None

    with (
        patch("src.routers.conversion.ConversionProfilesService") as svc_cls,
        patch("src.routers.conversion.tac_lint_fn", return_value=MagicMock(ok=True, issues=[])),
        patch("src.api.convert_metar_tac_with_metadata", side_effect=fake_convert),
    ):
        svc_cls.return_value.get_preset.return_value = _preset()
        res = client.post(
            "/api/v1/convert",
            data={
                "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
                "product": "METAR",
                "preset_id": str(PRESET_ID),
                "semantic_profile": "ICAO_2025",
                "report_variant": "",
                "iwxxm_version": "2023-1",
                "lint": "false",
            },
            headers={"Authorization": "Bearer t"},
        )

    assert res.status_code == 200, res.text
    assert seen
    assert seen[0]["profile"] == "annex3"
    meta = res.json().get("metadata") or {}
    assert meta.get("preset_id") == str(PRESET_ID)
    assert meta.get("semantic_profile") == "icao_2025"


def test_convert_preset_applies_extensions_and_overlay_defaults(convert_client: Any) -> None:
    client = convert_client
    overlay_id = uuid4()
    seen: list[dict[str, Any]] = []

    def fake_convert(tac: str, **kwargs: Any) -> tuple[str, dict[str, Any] | None]:
        seen.append(kwargs)
        return "<xml/>", None

    preset = _preset().model_copy(update={"extensions": ["IWXXM_CA"], "overlay_id": overlay_id})
    with (
        patch("src.routers.conversion.ConversionProfilesService") as svc_cls,
        patch("src.routers.conversion.tac_lint_fn", return_value=MagicMock(ok=True, issues=[])),
        patch("src.api.convert_metar_tac_with_metadata", side_effect=fake_convert),
    ):
        svc_cls.return_value.get_preset.return_value = preset
        res = client.post(
            "/api/v1/convert",
            data={
                "manual_text": "METAR CYUL 010000Z 18005KT 10SM SKC 20/10 A2992=",
                "product": "METAR",
                "preset_id": str(PRESET_ID),
                "semantic_profile": "",
                "iwxxm_version": "",
                "lint": "false",
            },
            headers={"Authorization": "Bearer t"},
        )

    assert res.status_code == 200, res.text
    assert seen
    assert seen[0]["profile"] == "ca_eccc"


def test_convert_json_body_invalid_preset_id_returns_400(convert_client: Any) -> None:
    client = convert_client
    res = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992="],
            "product": "METAR",
            "preset_id": "not-a-uuid",
        },
        headers={"Authorization": "Bearer t"},
    )
    assert res.status_code == 400
    assert "preset" in res.text.lower()
