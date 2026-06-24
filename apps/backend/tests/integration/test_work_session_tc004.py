"""TC-004 integration — F5 work session lifecycle with mocked Supabase service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api import app
from src.routers import work_sessions as ws_router
from src.schemas.work_session import WorkSession, WorkSessionStatus, WorkSessionUpdate
from src.utilities.security import verify_supabase_token

pytestmark = [pytest.mark.integration]

USER_ID = uuid4()
SESSION_A = uuid4()
SESSION_B = uuid4()
NOW = datetime(2026, 6, 23, 12, 0, tzinfo=timezone.utc)


def _row(
    session_id: UUID,
    *,
    status: WorkSessionStatus = WorkSessionStatus.DRAFT,
    deleted_at: datetime | None = None,
) -> WorkSession:
    return WorkSession(
        id=session_id,
        user_id=USER_ID,
        status=status,
        title="KJFK session",
        manual_tac="METAR KJFK",
        pending_files=[],
        converted_results=[],
        errors=[],
        issues=[],
        conversion_params={},
        kv_upload_key=None,
        deleted_at=deleted_at,
        created_at=NOW,
        updated_at=NOW,
    )


class _LifecycleFake:
    def __init__(self) -> None:
        self.store: dict = {SESSION_A: _row(SESSION_A)}

    def list_sessions(self, **_kwargs):
        active = [s for s in self.store.values() if s.deleted_at is None]
        return active, len(active)

    def get_session(self, session_id):
        row = self.store.get(session_id)
        if row is None or row.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Work session not found")
        return row

    def create_session(self, user_id, payload):
        new_id = uuid4()
        status = payload.status or WorkSessionStatus.DRAFT
        row = _row(new_id, status=status)
        self.store[new_id] = row
        return row

    def update_session(self, session_id, payload: WorkSessionUpdate):
        row = self.get_session(session_id)
        if payload.status == WorkSessionStatus.WIP:
            for other in self.store.values():
                if other.id != session_id and other.status == WorkSessionStatus.WIP and other.deleted_at is None:
                    raise HTTPException(status_code=409, detail="Only one WIP session is allowed per user")
        if payload.status is not None:
            row = row.model_copy(update={"status": payload.status})
        if payload.kv_upload_key is not None:
            row = row.model_copy(
                update={"kv_upload_key": payload.kv_upload_key, "status": WorkSessionStatus.FINISHED},
            )
        if payload.errors:
            row = row.model_copy(update={"errors": payload.errors, "status": WorkSessionStatus.FAILED})
        self.store[session_id] = row
        return row

    def soft_delete(self, session_id):
        row = self.get_session(session_id)
        row = row.model_copy(update={"deleted_at": NOW})
        self.store[session_id] = row
        return row

    def restore_session(self, session_id):
        row = self.store.get(session_id)
        if row is None or row.deleted_at is None:
            raise HTTPException(status_code=404, detail="Work session not found or not deleted")
        row = row.model_copy(update={"deleted_at": None})
        self.store[session_id] = row
        return row


@pytest.fixture
def tc004_client() -> TestClient:
    fake = _LifecycleFake()

    async def _auth_user() -> dict[str, str]:
        return {"sub": str(USER_ID)}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    app.dependency_overrides[ws_router.work_session_service] = lambda: fake
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_tc004_work_session_lifecycle(tc004_client: TestClient) -> None:
    """Draft → WIP → Finished; WIP conflict; soft-delete + restore."""
    headers = {"Authorization": "Bearer tc004-token"}

    draft = tc004_client.post(
        "/api/v1/work-sessions",
        headers=headers,
        json={"manual_tac": "METAR EGLL", "status": "draft"},
    )
    assert draft.status_code == 201
    draft_id = draft.json()["id"]

    wip = tc004_client.patch(
        f"/api/v1/work-sessions/{draft_id}",
        headers=headers,
        json={"status": "wip"},
    )
    assert wip.status_code == 200
    assert wip.json()["status"] == "wip"

    second = tc004_client.post(
        "/api/v1/work-sessions",
        headers=headers,
        json={"manual_tac": "METAR KJFK", "status": "draft"},
    )
    assert second.status_code == 201
    second_id = second.json()["id"]

    conflict = tc004_client.patch(
        f"/api/v1/work-sessions/{second_id}",
        headers=headers,
        json={"status": "wip"},
    )
    assert conflict.status_code == 409

    finished = tc004_client.patch(
        f"/api/v1/work-sessions/{draft_id}",
        headers=headers,
        json={"kv_upload_key": "kv-12345"},
    )
    assert finished.status_code == 200
    assert finished.json()["status"] == "finished"
    assert finished.json()["kv_upload_key"] == "kv-12345"

    deleted = tc004_client.delete(f"/api/v1/work-sessions/{second_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["deleted_at"] is not None

    restored = tc004_client.post(
        f"/api/v1/work-sessions/{second_id}/restore",
        headers=headers,
    )
    assert restored.status_code == 200
    assert restored.json()["deleted_at"] is None

    listing = tc004_client.get("/api/v1/work-sessions", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 2
