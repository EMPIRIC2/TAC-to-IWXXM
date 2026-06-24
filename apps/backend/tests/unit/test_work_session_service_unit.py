"""Unit tests for WorkSessionService with mocked Supabase client."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from src.schemas.work_session import (
    PendingFilePayload,
    WorkSessionCreate,
    WorkSessionStatus,
    WorkSessionUpdate,
)
from src.services import work_session_service as svc_mod
from src.services.work_session_service import (
    WorkSessionService,
    _handle_db_error,
    _payload_dict,
    _row_list,
    _single_row,
)

SESSION_ID = UUID("11111111-1111-1111-1111-111111111111")
NOW = datetime(2026, 6, 24, 12, 0, 0, tzinfo=timezone.utc)

ROW = {
    "id": str(SESSION_ID),
    "user_id": "22222222-2222-2222-2222-222222222222",
    "status": "draft",
    "title": "KJFK",
    "manual_tac": "METAR KJFK",
    "pending_files": [],
    "converted_results": [],
    "errors": [],
    "issues": [],
    "conversion_params": {},
    "kv_upload_key": None,
    "deleted_at": None,
    "created_at": NOW.isoformat(),
    "updated_at": NOW.isoformat(),
}


class _FakeQuery:
    def __init__(self, response: SimpleNamespace) -> None:
        self._response = response

    def select(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def is_(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def eq(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def gte(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def lte(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def order(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def range(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def insert(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def update(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    @property
    def not_(self) -> _FakeQuery:
        return self

    def is_(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def maybe_single(self) -> _FakeQuery:
        return self

    def execute(self) -> SimpleNamespace:
        return self._response


@pytest.fixture
def mock_client(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    client = MagicMock()
    monkeypatch.setattr(svc_mod, "get_supabase_url", lambda: "https://example.supabase.co")
    monkeypatch.setattr(svc_mod, "get_supabase_publishable_key", lambda: "publishable-key")
    monkeypatch.setattr(svc_mod, "create_client", lambda *_args, **_kwargs: client)
    return client


def test_handle_db_error_maps_wip_conflict() -> None:
    with pytest.raises(HTTPException) as exc:
        _handle_db_error(Exception("23505 duplicate metar_work_sessions_one_wip_per_user"))
    assert exc.value.status_code == 409


def test_list_sessions_returns_rows(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=[ROW], count=1))
    service = WorkSessionService("token")
    items, total = service.list_sessions(status_filter=WorkSessionStatus.DRAFT, page=1, limit=5)
    assert total == 1
    assert items[0].id == SESSION_ID


def test_get_session_not_found(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=None))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.get_session(SESSION_ID)
    assert exc.value.status_code == 404


def test_create_session_defaults(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=ROW))
    service = WorkSessionService("token")
    created = service.create_session(str(uuid4()), WorkSessionCreate(manual_tac="METAR"))
    assert created.status == WorkSessionStatus.DRAFT


def test_update_session_empty_payload_fetches_existing(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=ROW))
    service = WorkSessionService("token")
    updated = service.update_session(SESSION_ID, WorkSessionUpdate())
    assert updated.id == SESSION_ID


def test_soft_delete_and_restore(mock_client: MagicMock) -> None:
    deleted_row = {**ROW, "deleted_at": NOW.isoformat()}
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=deleted_row))
    service = WorkSessionService("token")
    deleted = service.soft_delete(SESSION_ID)
    assert deleted.deleted_at is not None

    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=ROW))
    restored = service.restore_session(SESSION_ID)
    assert restored.deleted_at is None


def test_list_sessions_db_error(mock_client: MagicMock) -> None:
    class _ErrorQuery(_FakeQuery):
        def execute(self) -> SimpleNamespace:
            raise RuntimeError("db down")

    mock_client.table.return_value = _ErrorQuery(SimpleNamespace(data=[], count=0))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.list_sessions()
    assert exc.value.status_code == 502


def test_update_session_not_found(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=[]))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.update_session(SESSION_ID, WorkSessionUpdate(manual_tac="x"))
    assert exc.value.status_code == 404


def test_get_session_none_response(mock_client: MagicMock) -> None:
    service = WorkSessionService("token")
    with patch.object(service, "_client") as client:
        client.table.return_value.select.return_value.eq.return_value.is_.return_value.maybe_single.return_value.execute.return_value = None
        with pytest.raises(HTTPException) as exc:
            service.get_session(SESSION_ID)
    assert exc.value.status_code == 404


def test_create_session_generates_title_when_missing(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data={**ROW, "title": "METAR 2026-06-24 12:00 UTC"}))
    service = WorkSessionService("token")
    created = service.create_session(str(uuid4()), WorkSessionCreate(manual_tac="METAR"))
    assert created.title


def test_list_sessions_with_date_filters(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=[ROW], count=1))
    service = WorkSessionService("token")
    items, total = service.list_sessions(
        from_dt=NOW,
        to_dt=NOW,
        include_deleted=True,
        page=2,
        limit=10,
    )
    assert total == 1
    assert len(items) == 1


def test_restore_session_not_found(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=[]))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.restore_session(SESSION_ID)
    assert exc.value.status_code == 404


def test_update_session_db_error(mock_client: MagicMock) -> None:
    class _ErrorQuery(_FakeQuery):
        def execute(self) -> SimpleNamespace:
            raise RuntimeError("update failed")

    mock_client.table.return_value = _ErrorQuery(SimpleNamespace(data=ROW))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.update_session(SESSION_ID, WorkSessionUpdate(manual_tac="METAR"))
    assert exc.value.status_code == 502


def test_get_session_db_error(mock_client: MagicMock) -> None:
    class _ErrorQuery(_FakeQuery):
        def execute(self) -> SimpleNamespace:
            raise RuntimeError("select failed")

    mock_client.table.return_value = _ErrorQuery(SimpleNamespace(data=ROW))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.get_session(SESSION_ID)
    assert exc.value.status_code == 502


def test_create_session_with_provided_title(mock_client: MagicMock) -> None:
    titled_row = {**ROW, "title": "Custom title"}
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=titled_row))
    service = WorkSessionService("token")
    created = service.create_session(
        str(uuid4()),
        WorkSessionCreate(title="Custom title", manual_tac="METAR"),
    )
    assert created.title == "Custom title"


def test_create_session_db_error(mock_client: MagicMock) -> None:
    class _ErrorQuery(_FakeQuery):
        def execute(self) -> SimpleNamespace:
            raise RuntimeError("insert failed")

    mock_client.table.return_value = _ErrorQuery(SimpleNamespace(data=ROW))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.create_session(str(uuid4()), WorkSessionCreate(manual_tac="METAR"))
    assert exc.value.status_code == 502


def test_soft_delete_not_found(mock_client: MagicMock) -> None:
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=[]))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.soft_delete(SESSION_ID)
    assert exc.value.status_code == 404


def test_row_list_and_payload_helpers() -> None:
    assert _row_list("not-a-list") == []
    assert _row_list([ROW]) == [ROW]
    data = _payload_dict(
        WorkSessionCreate(
            pending_files=[PendingFilePayload(name="a.txt", content="METAR")],
            status=WorkSessionStatus.WIP,
        ),
        user_id="user-1",
    )
    assert data["user_id"] == "user-1"
    assert data["status"] == "wip"
    assert data["pending_files"][0]["name"] == "a.txt"


def test_single_row_raises_when_empty() -> None:
    with pytest.raises(HTTPException):
        _single_row([])


def test_client_for_token_missing_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(svc_mod, "get_supabase_url", lambda: "")
    monkeypatch.setattr(svc_mod, "get_supabase_publishable_key", lambda: "")
    with pytest.raises(HTTPException) as exc:
        WorkSessionService("token")
    assert exc.value.status_code == 503


def test_single_row_from_list() -> None:
    assert _single_row([ROW]) == ROW


def test_row_list_skips_non_dict_entries() -> None:
    assert _row_list([ROW, "skip-me", None, 42]) == [ROW]


def test_create_session_preserves_explicit_status(mock_client: MagicMock) -> None:
    wip_row = {**ROW, "status": "wip"}
    mock_client.table.return_value = _FakeQuery(SimpleNamespace(data=wip_row))
    service = WorkSessionService("token")
    created = service.create_session(
        str(uuid4()),
        WorkSessionCreate(manual_tac="METAR", status=WorkSessionStatus.WIP),
    )
    assert created.status == WorkSessionStatus.WIP


def test_soft_delete_db_error(mock_client: MagicMock) -> None:
    class _ErrorQuery(_FakeQuery):
        def execute(self) -> SimpleNamespace:
            raise RuntimeError("delete failed")

    mock_client.table.return_value = _ErrorQuery(SimpleNamespace(data=ROW))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.soft_delete(SESSION_ID)
    assert exc.value.status_code == 502


def test_restore_session_db_error(mock_client: MagicMock) -> None:
    class _ErrorQuery(_FakeQuery):
        def execute(self) -> SimpleNamespace:
            raise RuntimeError("restore failed")

    mock_client.table.return_value = _ErrorQuery(SimpleNamespace(data=ROW))
    service = WorkSessionService("token")
    with pytest.raises(HTTPException) as exc:
        service.restore_session(SESSION_ID)
    assert exc.value.status_code == 502
