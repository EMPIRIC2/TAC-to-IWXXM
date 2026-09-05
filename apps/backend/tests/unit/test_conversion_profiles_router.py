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
from src.schemas.conversion_profiles import (
    OverlayCreate,
    OverlayOut,
    OverlayUpdate,
    RulePackCreate,
    RulePackOut,
    RulePackUpdate,
)
from src.services import profile_catalog as catalog_mod
from src.utilities.security import verify_supabase_token

USER_ID = uuid4()
PACK_ID = uuid4()
OVERLAY_ID = uuid4()
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


def _sample_overlay() -> OverlayOut:
    return OverlayOut(
        id=OVERLAY_ID,
        user_id=USER_ID,
        slug="icao-soft",
        base_profile_id="ICAO_2025",
        body={"lint": {"severity": "warning"}},
        signature="a" * 64,
        shared=False,
        created_at=NOW,
        updated_at=NOW,
    )


class _FakeProfilesService:
    def __init__(self) -> None:
        self.pack = _sample_pack()
        self.overlay = _sample_overlay()

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

    def list_overlays(self) -> list[OverlayOut]:
        return [self.overlay]

    def get_overlay(self, overlay_id: UUID, *, require_owner: bool = False) -> OverlayOut:
        if overlay_id != self.overlay.id:
            raise HTTPException(status_code=404, detail="Overlay not found")
        return self.overlay

    def create_overlay(self, payload: OverlayCreate) -> OverlayOut:
        self.overlay = self.overlay.model_copy(
            update={
                "slug": payload.slug,
                "base_profile_id": payload.base_profile_id,
                "body": payload.body,
                "shared": payload.shared,
                "signature": "b" * 64,
            }
        )
        return self.overlay

    def update_overlay(self, overlay_id: UUID, payload: OverlayUpdate) -> OverlayOut:
        if overlay_id != self.overlay.id:
            raise HTTPException(status_code=404, detail="Overlay not found")
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        if "base_profile_id" in data and data["base_profile_id"] is not None:
            self.overlay = self.overlay.model_copy(update={"base_profile_id": data["base_profile_id"]})
        if "body" in data and data["body"] is not None:
            self.overlay = self.overlay.model_copy(update={"body": data["body"]})
        if "shared" in data and data["shared"] is not None:
            self.overlay = self.overlay.model_copy(update={"shared": data["shared"]})
        return self.overlay

    def delete_overlay(self, overlay_id: UUID) -> None:
        if overlay_id != self.overlay.id:
            raise HTTPException(status_code=404, detail="Overlay not found")


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

    by_id = {profile["id"]: profile for profile in body["profiles"]}
    icao = by_id["ICAO_2025"]
    assert icao["rule_pack_count"] == 1
    assert icao["overlay_count"] == 1
    assert icao["deltas_vs_icao"]
    assert isinstance(icao["iwxxm_line"], str)

    us = by_id["US_FAA_NWS"]
    assert us["rule_pack_count"] is None
    assert us["overlay_count"] is None
    assert len(us["deltas_vs_icao"]) <= 3
    assert "iwxxm-us" in (us["iwxxm_line"] or "")


def test_catalog_stays_available_when_profile_storage_is_unavailable() -> None:
    class _FailingProfilesService:
        def list_rule_packs(self) -> list[RulePackOut]:
            raise HTTPException(status_code=503, detail="Profile storage unavailable")

        def list_overlays(self) -> list[OverlayOut]:
            raise HTTPException(status_code=503, detail="Profile storage unavailable")

    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "user"}

    def override_service() -> _FailingProfilesService:
        return _FailingProfilesService()

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    app.dependency_overrides[profiles_router.profiles_service] = override_service
    client = TestClient(app)
    catalog_mod.clear_catalog_cache()

    res = client.get(
        "/api/v1/profiles/catalog",
        headers={"Authorization": "Bearer test-token"},
    )

    app.dependency_overrides.clear()
    catalog_mod.clear_catalog_cache()

    assert res.status_code == 200
    body = res.json()
    by_id = {profile["id"]: profile for profile in body["profiles"]}
    assert by_id["ICAO_2025"]["rule_pack_count"] is None
    assert by_id["ICAO_2025"]["overlay_count"] is None


def test_catalog_propagates_non_503_rule_pack_errors() -> None:
    class _FailingProfilesService:
        def list_rule_packs(self) -> list[RulePackOut]:
            raise HTTPException(status_code=403, detail="Forbidden")

        def list_overlays(self) -> list[OverlayOut]:
            return []

    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "user"}

    def override_service() -> _FailingProfilesService:
        return _FailingProfilesService()

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    app.dependency_overrides[profiles_router.profiles_service] = override_service
    client = TestClient(app)
    catalog_mod.clear_catalog_cache()

    res = client.get(
        "/api/v1/profiles/catalog",
        headers={"Authorization": "Bearer test-token"},
    )

    app.dependency_overrides.clear()
    catalog_mod.clear_catalog_cache()

    assert res.status_code == 403
    assert res.json()["detail"] == "Forbidden"


def test_catalog_propagates_non_503_overlay_errors() -> None:
    class _FailingProfilesService:
        def list_rule_packs(self) -> list[RulePackOut]:
            return []

        def list_overlays(self) -> list[OverlayOut]:
            raise HTTPException(status_code=403, detail="Forbidden")

    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "user"}

    def override_service() -> _FailingProfilesService:
        return _FailingProfilesService()

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    app.dependency_overrides[profiles_router.profiles_service] = override_service
    client = TestClient(app)
    catalog_mod.clear_catalog_cache()

    res = client.get(
        "/api/v1/profiles/catalog",
        headers={"Authorization": "Bearer test-token"},
    )

    app.dependency_overrides.clear()
    catalog_mod.clear_catalog_cache()

    assert res.status_code == 403
    assert res.json()["detail"] == "Forbidden"


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


def test_overlays_crud(profiles_client: Any) -> None:
    client, fake = profiles_client
    headers = {"Authorization": "Bearer test-token"}

    listed = client.get("/api/v1/profiles/overlays", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["items"][0]["slug"] == "icao-soft"

    created = client.post(
        "/api/v1/profiles/overlays",
        headers=headers,
        json={
            "slug": "us-soft",
            "baseProfileId": "US_FAA_NWS",
            "body": {"note": "soft"},
            "shared": False,
        },
    )
    assert created.status_code == 201
    assert created.json()["baseProfileId"] == "US_FAA_NWS"
    assert created.json()["signature"]

    got = client.get(f"/api/v1/profiles/overlays/{OVERLAY_ID}", headers=headers)
    assert got.status_code == 200

    patched = client.patch(
        f"/api/v1/profiles/overlays/{OVERLAY_ID}",
        headers=headers,
        json={"shared": True},
    )
    assert patched.status_code == 200
    assert patched.json()["shared"] is True
    assert fake.overlay.shared is True

    deleted = client.delete(f"/api/v1/profiles/overlays/{OVERLAY_ID}", headers=headers)
    assert deleted.status_code == 204


def test_overlays_require_auth() -> None:
    client = TestClient(app)
    assert client.get("/api/v1/profiles/overlays").status_code in {401, 403}
