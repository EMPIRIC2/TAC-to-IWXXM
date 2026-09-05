"""BUG-2026-09-05 - Static profile catalog must survive storage failures."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.api import app  # noqa: E402
from src.routers import conversion_profiles as profiles_router  # noqa: E402
from src.services import profile_catalog as catalog_mod  # noqa: E402
from src.utilities.security import verify_supabase_token  # noqa: E402

USER_ID = uuid4()


class _FailingProfilesService:
    def list_rule_packs(self) -> list[Any]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile storage unavailable",
        )

    def list_overlays(self) -> list[Any]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile storage unavailable",
        )


@pytest.fixture
def client_with_failing_profile_storage() -> TestClient:
    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "user"}

    def override_service() -> _FailingProfilesService:
        return _FailingProfilesService()

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    app.dependency_overrides[profiles_router.profiles_service] = override_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    catalog_mod.clear_catalog_cache()


def test_bug_2026_09_05_profile_catalog_stays_available_without_storage(
    client_with_failing_profile_storage: TestClient,
) -> None:
    response = client_with_failing_profile_storage.get(
        "/api/v1/profiles/catalog",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    body = response.json()
    ids = {profile["id"] for profile in body["profiles"]}
    assert "ICAO_2025" in ids
    assert "US_FAA_NWS" in ids

    by_id = {profile["id"]: profile for profile in body["profiles"]}
    assert by_id["ICAO_2025"]["rule_pack_count"] is None
    assert by_id["ICAO_2025"]["overlay_count"] is None
