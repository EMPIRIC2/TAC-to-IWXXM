"""TC-EV080 — conversion template routes + convert apply."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.api import app
from src.routers import conversion_profiles as profiles_router
from src.schemas.conversion_profiles import (
    ConversionTemplateCreate,
    ConversionTemplateOut,
    ConversionTemplateSlot,
    ConversionTemplateUpdate,
)
from src.utilities.security import verify_optional_supabase_token, verify_supabase_token

USER_ID = uuid4()
TMPL_ID = uuid4()
NOW = datetime(2026, 9, 14, tzinfo=UTC)


def _fp_wind() -> ConversionTemplateOut:
    return ConversionTemplateOut(
        id="CV.WIND",
        user_id=None,
        slug="CV.WIND",
        name="Wind group",
        access="first_party",
        iwxxm_block="iwxxm:WindObservation",
        slots=[
            ConversionTemplateSlot(id="ddd", label="direction", type="digits", digits=3),
            ConversionTemplateSlot(id="ff", label="speed", type="digits", digits=2),
            ConversionTemplateSlot(
                id="gust",
                label="gust",
                type="digits",
                optional=True,
                digits=2,
                literal="G",
            ),
            ConversionTemplateSlot(id="uom", label="unit", type="unit", enum_values="KT|MPS"),
        ],
        sample="18012G20KT",
        shared=True,
        profiles=["ICAO_2025"],
    )


def _custom() -> ConversionTemplateOut:
    return ConversionTemplateOut(
        id=str(TMPL_ID),
        user_id=USER_ID,
        slug="my-wind",
        name="My wind",
        access="custom",
        iwxxm_block="iwxxm:WindObservation",
        slots=[ConversionTemplateSlot(id="ddd", label="direction", type="digits", digits=3)],
        sample="18012KT",
        fork_of="CV.WIND",
        shared=False,
        created_at=NOW,
        updated_at=NOW,
    )


class _FakeSvc:
    def __init__(self) -> None:
        self.custom = _custom()

    def list_conversion_templates(self) -> list[ConversionTemplateOut]:
        return [_fp_wind(), self.custom]

    def get_conversion_template(self, template_id: str, *, require_owner: bool = False) -> ConversionTemplateOut:
        if template_id == "CV.WIND":
            if require_owner:
                raise HTTPException(status_code=403, detail="First-party templates are read-only")
            return _fp_wind()
        if template_id == str(TMPL_ID):
            return self.custom
        raise HTTPException(status_code=404, detail="Conversion template not found")

    def create_conversion_template(self, payload: ConversionTemplateCreate) -> ConversionTemplateOut:
        self.custom = self.custom.model_copy(
            update={
                "slug": payload.slug,
                "name": payload.name,
                "iwxxm_block": payload.iwxxm_block,
                "slots": payload.slots,
                "fork_of": payload.fork_of,
            }
        )
        return self.custom

    def update_conversion_template(self, template_id: str, payload: ConversionTemplateUpdate) -> ConversionTemplateOut:
        if template_id == "CV.WIND":
            raise HTTPException(status_code=403, detail="First-party templates cannot be modified")
        if template_id != str(TMPL_ID):
            raise HTTPException(status_code=404, detail="Conversion template not found")
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        self.custom = self.custom.model_copy(update=data)
        return self.custom

    def delete_conversion_template(self, template_id: str) -> None:
        if template_id == "CV.WIND":
            raise HTTPException(status_code=403, detail="First-party templates cannot be deleted")
        if template_id != str(TMPL_ID):
            raise HTTPException(status_code=404, detail="Conversion template not found")


@pytest.fixture
def client() -> Any:
    fake = _FakeSvc()

    async def override_verify() -> dict[str, str]:
        return {"sub": str(USER_ID)}

    def override_service() -> _FakeSvc:
        return fake

    app.dependency_overrides[verify_supabase_token] = override_verify
    app.dependency_overrides[profiles_router.profiles_service] = override_service
    yield TestClient(app), fake
    app.dependency_overrides.clear()


def test_list_conversion_templates(client: Any) -> None:
    http, _fake = client
    res = http.get("/api/v1/profiles/conversion-templates")
    assert res.status_code == 200
    ids = {i["id"] for i in res.json()["items"]}
    assert "CV.WIND" in ids
    assert str(TMPL_ID) in ids


def test_preview_wind_bridge(client: Any) -> None:
    http, _fake = client
    res = http.post(
        "/api/v1/profiles/conversion-templates/preview",
        json={"templateId": "CV.WIND", "focusGroup": "18012G20KT"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["matched"] is True
    assert "WindObservation" in body["xmlBlock"]


def test_patch_first_party_forbidden(client: Any) -> None:
    http, _fake = client
    res = http.patch(
        "/api/v1/profiles/conversion-templates/CV.WIND",
        json={"name": "nope"},
    )
    assert res.status_code == 403


def test_create_fork(client: Any) -> None:
    http, fake = client
    res = http.post(
        "/api/v1/profiles/conversion-templates",
        json={
            "slug": "forked-wind",
            "name": "Forked wind",
            "iwxxmBlock": "iwxxm:WindObservation",
            "forkOf": "CV.WIND",
            "slots": [{"id": "ddd", "label": "direction", "type": "digits", "digits": 3}],
        },
    )
    assert res.status_code == 201
    assert fake.custom.slug == "forked-wind"


def test_convert_unknown_custom_template_fail_closed() -> None:
    async def override_optional() -> dict[str, str]:
        return {"sub": str(USER_ID)}

    app.dependency_overrides[verify_optional_supabase_token] = override_optional
    try:
        with patch("src.routers.conversion.ConversionProfilesService") as svc_cls:
            svc_cls.return_value.get_conversion_template.side_effect = HTTPException(
                status_code=404, detail="Conversion template not found"
            )
            res = TestClient(app).post(
                "/api/v1/convert",
                data={
                    "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
                    "product": "METAR",
                    "conversion_template_id": str(TMPL_ID),
                },
                headers={"Authorization": "Bearer t"},
            )
        assert res.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_convert_custom_requires_auth() -> None:
    res = TestClient(app).post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
            "product": "METAR",
            "conversion_template_id": str(TMPL_ID),
        },
    )
    assert res.status_code in {401, 403}


def test_convert_first_party_no_auth_required_for_resolve() -> None:
    res = TestClient(app).post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 18005KT 10SM SKC 20/10 A2992=",
            "product": "METAR",
            "conversion_template_id": "CV.WIND",
        },
    )
    assert res.status_code not in {401, 403}
