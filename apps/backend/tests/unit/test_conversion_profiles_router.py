"""Unit tests for EV-933 ConversionProfile catalog + rule-pack routes (TC-EV933-001..002)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.api import app
from src.routers import conversion_profiles as profiles_router
from src.schemas.conversion_profiles import RulePackCreate, RulePackOut, RulePackUpdate
from src.services import profile_catalog as catalog_mod
from src.utilities.security import verify_supabase_token

USER_ID = uuid4()
PACK_ID = uuid4()
NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)


def _sample_pack() -> RulePackOut:
    return RulePackOut(
        id=PACK_ID,
        user_id=USER_ID,
        slug="metar-soft",
        profile="ICAO_2025",
        product="METAR",
        stage="lint",
        severity="warning",
        when_expr="missing_terminator",
        message="Report should end with =",
        standard_reference="Annex 3",
        created_at=NOW,
        updated_at=NOW,
    )


class _FakeProfilesService:
    def __init__(self) -> None:
        self.pack = _sample_pack()

    def list_rule_packs(self) -> list[RulePackOut]:
        return [self.pack]

    def get_rule_pack(self, pack_id: UUID) -> RulePackOut:
        if pack_id != self.pack.id:
            raise HTTPException(status_code=404, detail="Rule pack not found")
        return self.pack

    def create_rule_pack(self, payload: RulePackCreate) -> RulePackOut:
        self.pack = self.pack.model_copy(
            update={
                "slug": payload.slug,
                "profile": payload.profile,
                "product": payload.product,
                "stage": payload.stage,
                "severity": payload.severity,
                "when_expr": payload.when_expr,
                "message": payload.message,
                "standard_reference": payload.standard_reference,
            }
        )
        return self.pack

    def update_rule_pack(self, pack_id: UUID, payload: RulePackUpdate) -> RulePackOut:
        if pack_id != self.pack.id:
            raise HTTPException(status_code=404, detail="Rule pack not found")
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        self.pack = self.pack.model_copy(update=data)
        return self.pack

    def delete_rule_pack(self, pack_id: UUID) -> None:
        if pack_id != self.pack.id:
            raise HTTPException(status_code=404, detail="Rule pack not found")


@pytest.fixture
def profiles_client() -> Any:
    fake = _FakeProfilesService()

    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "user"}

    def override_service() -> _FakeProfilesService:
        return fake

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    app.dependency_overrides[profiles_router.profiles_service] = override_service
    client = TestClient(app)
    yield client, fake
    app.dependency_overrides.clear()
    catalog_mod.clear_catalog_cache()


def test_profiles_service_factory() -> None:
    svc = profiles_router.profiles_service({"sub": str(USER_ID)})
    assert str(svc.user_id) == str(USER_ID)


def test_catalog_requires_auth() -> None:
    client = TestClient(app)
    assert client.get("/api/v1/profiles/catalog").status_code in {401, 403}


def test_catalog_returns_profiles(profiles_client: Any) -> None:
    client, _fake = profiles_client
    catalog_mod.clear_catalog_cache()
    res = client.get(
        "/api/v1/profiles/catalog",
        headers={"Authorization": "Bearer test-token"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "profiles" in body
    ids = {p["id"] for p in body["profiles"]}
    assert "ICAO_2025" in ids
    assert "US_FAA_NWS" in ids


def test_rule_packs_crud(profiles_client: Any) -> None:
    client, fake = profiles_client
    headers = {"Authorization": "Bearer test-token"}

    listed = client.get("/api/v1/profiles/rule-packs", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["items"][0]["slug"] == "metar-soft"

    created = client.post(
        "/api/v1/profiles/rule-packs",
        headers=headers,
        json={
            "slug": "taf-info",
            "profile": "US_FAA_NWS",
            "product": "TAF",
            "stage": "lint",
            "severity": "info",
            "when": "RMK",
            "message": "US RMK present",
            "standardReference": "FMH-1",
        },
    )
    assert created.status_code == 201
    assert created.json()["slug"] == "taf-info"
    assert created.json()["when"] == "RMK"
    assert created.json()["standardReference"] == "FMH-1"

    got = client.get(f"/api/v1/profiles/rule-packs/{PACK_ID}", headers=headers)
    assert got.status_code == 200

    patched = client.patch(
        f"/api/v1/profiles/rule-packs/{PACK_ID}",
        headers=headers,
        json={"severity": "error"},
    )
    assert patched.status_code == 200
    assert patched.json()["severity"] == "error"
    assert fake.pack.severity == "error"

    deleted = client.delete(f"/api/v1/profiles/rule-packs/{PACK_ID}", headers=headers)
    assert deleted.status_code == 204


def test_rule_packs_require_auth() -> None:
    client = TestClient(app)
    assert client.get("/api/v1/profiles/rule-packs").status_code in {401, 403}
