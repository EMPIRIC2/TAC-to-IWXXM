"""Unit tests for F5 work session router — CRUD, WIP conflict, soft-delete, restore."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api import app
from src.routers import work_sessions as ws_router
from src.schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionProduct,
    WorkSessionStatus,
    WorkSessionUpdate,
)
from src.services.work_session_service import WorkSessionService
from src.utilities.security import verify_supabase_token

SESSION_ID = uuid4()
USER_ID = uuid4()
NOW = datetime(2026, 6, 23, 12, 0, tzinfo=timezone.utc)


def _sample_session(*, status: WorkSessionStatus = WorkSessionStatus.DRAFT) -> WorkSession:
    return WorkSession(
        id=SESSION_ID,
        user_id=USER_ID,
        product=WorkSessionProduct.METAR,
        status=status,
        title="KJFK 2026-06-23",
        manual_tac="METAR KJFK",
        pending_files=[],
        converted_results=[],
        errors=[],
        issues=[],
        conversion_params={"iwxxm_version": "2025-2"},
        kv_upload_key=None,
        deleted_at=None,
        created_at=NOW,
        updated_at=NOW,
    )


class _FakeService:
    def __init__(self) -> None:
        self.sessions: list[WorkSession] = [_sample_session()]

    def list_sessions(self, **_kwargs: Any) -> tuple[list[WorkSession], int]:
        return self.sessions, len(self.sessions)

    def get_session(self, session_id: UUID) -> WorkSession:
        for row in self.sessions:
            if row.id == session_id:
                return row
        raise HTTPException(status_code=404, detail="Work session not found")

    def create_session(self, user_id: str, payload: WorkSessionCreate) -> WorkSession:
        row = _sample_session(status=payload.status or WorkSessionStatus.DRAFT)
        self.sessions.append(row)
        return row

    def update_session(self, session_id: UUID, payload: WorkSessionUpdate) -> WorkSession:
        if payload.status == WorkSessionStatus.WIP and any(s.status == WorkSessionStatus.WIP for s in self.sessions):
            raise HTTPException(status_code=409, detail="Only one WIP session is allowed per user")
        row = self.get_session(session_id)
        if payload.status is not None:
            return row.model_copy(update={"status": payload.status})
        return row

    def soft_delete(self, session_id: UUID) -> WorkSession:
        row = self.get_session(session_id)
        return row.model_copy(update={"deleted_at": NOW})

    def restore_session(self, session_id: UUID) -> WorkSession:
        row = self.get_session(session_id)
        return row.model_copy(update={"deleted_at": None})


@pytest.fixture
def work_session_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    fake = _FakeService()

    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "user"}

    def override_service() -> _FakeService:
        return fake

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    app.dependency_overrides[ws_router.work_session_service] = override_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_list_work_sessions_returns_items(work_session_client: TestClient) -> None:
    response = work_session_client.get(
        "/api/v1/work-sessions",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert body["items"][0]["status"] == "draft"


def test_create_work_session_returns_201(work_session_client: TestClient) -> None:
    response = work_session_client.post(
        "/api/v1/work-sessions",
        headers={"Authorization": "Bearer test-token"},
        json={"product": "metar", "manual_tac": "METAR TEST"},
    )
    assert response.status_code == 201, response.json()
    assert response.json()["manual_tac"] == "METAR KJFK"


def test_patch_wip_conflict_returns_409(work_session_client: TestClient) -> None:
    fake = _FakeService()
    fake.sessions = [
        _sample_session(status=WorkSessionStatus.WIP),
        _sample_session(status=WorkSessionStatus.DRAFT).model_copy(update={"id": uuid4()}),
    ]

    def override_service() -> _FakeService:
        return fake

    app.dependency_overrides[ws_router.work_session_service] = override_service

    response = work_session_client.patch(
        f"/api/v1/work-sessions/{fake.sessions[1].id}",
        headers={"Authorization": "Bearer test-token"},
        json={"status": "wip"},
    )
    assert response.status_code == 409
    assert "WIP" in response.json()["detail"]


def test_soft_delete_and_restore(work_session_client: TestClient) -> None:
    delete_resp = work_session_client.delete(
        f"/api/v1/work-sessions/{SESSION_ID}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted_at"] is not None

    restore_resp = work_session_client.post(
        f"/api/v1/work-sessions/{SESSION_ID}/restore",
        headers={"Authorization": "Bearer test-token"},
    )
    assert restore_resp.status_code == 200
    assert restore_resp.json()["deleted_at"] is None


def test_get_work_session_by_id(work_session_client: TestClient) -> None:
    response = work_session_client.get(
        f"/api/v1/work-sessions/{SESSION_ID}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(SESSION_ID)


def test_admin_list_work_sessions_removed(work_session_client: TestClient) -> None:
    """S011 / ADR-021: admin work-sessions list is not mounted."""
    response = work_session_client.get(
        "/admin/work-sessions",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 404


def test_user_id_helper_uses_sub() -> None:
    assert ws_router._user_id({"sub": "abc"}) == "abc"
    assert ws_router._user_id({"user_id": "legacy"}) == "legacy"


def test_work_session_service_dependency_factory() -> None:
    from fastapi.security import HTTPAuthorizationCredentials

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    with patch.object(ws_router, "WorkSessionService") as mock_cls:
        mock_cls.return_value = _FakeService()
        service = ws_router.work_session_service(creds)
        assert service is mock_cls.return_value


def test_work_session_service_wip_conflict_maps_db_error() -> None:
    from src.services import work_session_service as svc_mod

    with pytest.raises(HTTPException) as exc:
        svc_mod._handle_db_error(Exception("23505 duplicate tac_work_sessions_one_wip_per_user"))
    assert exc.value.status_code == 409
