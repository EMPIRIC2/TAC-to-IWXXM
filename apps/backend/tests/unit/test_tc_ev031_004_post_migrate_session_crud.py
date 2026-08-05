"""T5.4 / TC-EV031-004 + TC-F30-002 — post-migrate session CRUD; Auth-only Supabase.

After Supabase → DO product migrate (T5.3), logged-in work-session CRUD must use
``DATABASE_URL`` / SQLAlchemy and must not touch Supabase PostgREST. JWT verify
remains Supabase Auth JWKS-only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
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
from src.services import work_session_service as svc
from src.utilities.security import verify_supabase_token

_BACKEND_SRC = Path(__file__).resolve().parents[2] / "src"
_PRODUCT_PATHS = (
    _BACKEND_SRC / "services" / "work_session_service.py",
    _BACKEND_SRC / "routers" / "work_sessions.py",
    _BACKEND_SRC / "utilities" / "security.py",
    _BACKEND_SRC / "api.py",
)

USER_ID = uuid4()
SESSION_ID = uuid4()
NOW = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)


def _sample_session(*, status: WorkSessionStatus = WorkSessionStatus.DRAFT) -> WorkSession:
    return WorkSession(
        id=SESSION_ID,
        user_id=USER_ID,
        product=WorkSessionProduct.METAR,
        status=status,
        title="post-migrate",
        manual_tac="METAR KJFK 031200Z 18010KT 10SM CLR 22/12 A3012",
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


class _TrackingService:
    """In-memory CRUD stand-in for post-migrate DO Postgres store."""

    def __init__(self) -> None:
        self.sessions: dict[UUID, WorkSession] = {}
        self.calls: list[str] = []

    def list_sessions(self, **_kwargs: Any) -> tuple[list[WorkSession], int]:
        self.calls.append("list")
        items = list(self.sessions.values())
        return items, len(items)

    def get_session(self, session_id: UUID) -> WorkSession:
        self.calls.append("get")
        from fastapi import HTTPException

        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Work session not found")
        return self.sessions[session_id]

    def create_session(self, user_id: str, payload: WorkSessionCreate) -> WorkSession:
        self.calls.append("create")
        row = _sample_session(status=payload.status or WorkSessionStatus.DRAFT)
        row = row.model_copy(update={"user_id": UUID(user_id), "title": payload.title or ""})
        self.sessions[row.id] = row
        return row

    def update_session(self, session_id: UUID, payload: WorkSessionUpdate) -> WorkSession:
        self.calls.append("update")
        row = self.get_session(session_id)
        updates: dict[str, Any] = {}
        if payload.title is not None:
            updates["title"] = payload.title
        if payload.status is not None:
            updates["status"] = payload.status
        updated = row.model_copy(update=updates)
        self.sessions[session_id] = updated
        return updated

    def soft_delete(self, session_id: UUID) -> WorkSession:
        self.calls.append("soft_delete")
        row = self.get_session(session_id)
        updated = row.model_copy(update={"deleted_at": NOW})
        self.sessions[session_id] = updated
        return updated

    def restore_session(self, session_id: UUID) -> WorkSession:
        self.calls.append("restore")
        row = self.get_session(session_id)
        updated = row.model_copy(update={"deleted_at": None})
        self.sessions[session_id] = updated
        return updated


@pytest.fixture
def post_migrate_client() -> TestClient:
    fake = _TrackingService()

    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "authenticated"}

    def override_service() -> _TrackingService:
        return fake

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    app.dependency_overrides[ws_router.work_session_service] = override_service
    client = TestClient(app)
    client.fake_service = fake  # type: ignore[attr-defined]
    yield client
    app.dependency_overrides.clear()


@pytest.mark.unit
def test_tc_f30_002_product_modules_have_zero_postgrest_imports() -> None:
    """TC-F30-002 — Auth-only Supabase; no PostgREST product clients on default path."""
    for path in _PRODUCT_PATHS:
        assert path.is_file(), f"missing {path}"
        text = path.read_text(encoding="utf-8")
        assert "create_client" not in text, path.name
        assert "from supabase" not in text, path.name
        assert "postgrest" not in text.lower(), path.name
        assert "SUPABASE_SERVICE_ROLE" not in text, path.name


@pytest.mark.unit
def test_tc_f30_002_jwt_verify_is_jwks_only() -> None:
    text = (_BACKEND_SRC / "utilities" / "security.py").read_text(encoding="utf-8")
    assert "verify_access_token" in text
    assert "JWKS" in text or "jwks" in text
    assert "SUPABASE_JWT_SECRET" not in text


@pytest.mark.unit
def test_tc_ev031_004_session_crud_happy_path(post_migrate_client: TestClient) -> None:
    """TC-EV031-004 — create / list / get / patch / soft-delete / restore via JWT gate."""
    headers = {"Authorization": "Bearer test-token"}
    create = post_migrate_client.post(
        "/api/v1/work-sessions",
        headers=headers,
        json={
            "product": "metar",
            "status": "draft",
            "title": "post-migrate",
            "manual_tac": "METAR KJFK",
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    sid = body["id"]

    listed = post_migrate_client.get("/api/v1/work-sessions", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    got = post_migrate_client.get(f"/api/v1/work-sessions/{sid}", headers=headers)
    assert got.status_code == 200
    assert got.json()["id"] == sid

    patched = post_migrate_client.patch(
        f"/api/v1/work-sessions/{sid}",
        headers=headers,
        json={"title": "renamed-after-migrate"},
    )
    assert patched.status_code == 200
    assert patched.json()["title"] == "renamed-after-migrate"

    deleted = post_migrate_client.delete(f"/api/v1/work-sessions/{sid}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["deleted_at"] is not None

    restored = post_migrate_client.post(
        f"/api/v1/work-sessions/{sid}/restore",
        headers=headers,
    )
    assert restored.status_code == 200
    assert restored.json()["deleted_at"] is None

    fake: _TrackingService = post_migrate_client.fake_service  # type: ignore[attr-defined]
    assert "create" in fake.calls
    assert "list" in fake.calls
    assert "get" in fake.calls
    assert "update" in fake.calls
    assert "soft_delete" in fake.calls
    assert "restore" in fake.calls


@pytest.mark.unit
def test_tc_ev031_004_service_binds_database_url_not_supabase_rest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Post-migrate service resolves DO ``DATABASE_URL`` (sync psycopg dialect)."""
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://do_user:secret@db.example.digitalocean.com:25060/defaultdb",
    )
    svc._engine = None
    url = svc._sync_database_url()
    assert url.startswith("postgresql+psycopg://")
    assert "digitalocean.com" in url
    assert "supabase" not in url.lower()
    svc._engine = None


@pytest.mark.unit
def test_tc_f30_002_convert_path_has_no_supabase_db_client() -> None:
    """Instrumented static gate: public convert stays free of PostgREST product clients."""
    api = (_BACKEND_SRC / "api.py").read_text(encoding="utf-8")
    assert "create_client" not in api
    assert "from supabase" not in api
    assert "postgrest" not in api.lower()
    assert "/api/v1/convert" in api


@pytest.mark.unit
def test_tc_ev031_004_service_module_is_sqlalchemy_do_plane() -> None:
    """Work-session service is the post-migrate DO data plane (not Supabase REST)."""
    text = (_BACKEND_SRC / "services" / "work_session_service.py").read_text(encoding="utf-8")
    assert "sqlalchemy" in text
    assert "tac_work_sessions" in text
    assert "DATABASE_URL" in text
    assert "create_client" not in text
    assert "from supabase" not in text
