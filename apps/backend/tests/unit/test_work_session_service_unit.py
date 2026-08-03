"""Unit tests for WorkSessionService URL helpers + DB error mapping (F31 / ADR-033)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.schemas.work_session import (
    WorkSessionCreate,
    WorkSessionProduct,
    WorkSessionStatus,
    WorkSessionUpdate,
)
from src.services import work_session_service as svc


def test_sync_database_url_rewrites_asyncpg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://u:p@localhost:5432/db",
    )
    assert svc._sync_database_url().startswith("postgresql+psycopg://")


def test_sync_database_url_plain_and_psycopg2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    assert svc._sync_database_url().startswith("postgresql+psycopg://")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://u:p@localhost/db")
    assert svc._sync_database_url().startswith("postgresql+psycopg://")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    assert svc._sync_database_url() == "postgresql+psycopg://u:p@localhost/db"


def test_get_engine_and_table_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    svc._engine = None
    svc._sessions_table = None
    fake_engine = MagicMock()
    fake_table = MagicMock()
    with (
        patch("src.services.work_session_service.create_engine", return_value=fake_engine) as ce,
        patch("src.services.work_session_service.Table", return_value=fake_table) as tb,
    ):
        assert svc._get_engine() is fake_engine
        assert svc._get_engine() is fake_engine
        ce.assert_called_once()
        assert svc._table() is fake_table
        assert svc._table() is fake_table
        tb.assert_called_once()
    svc._engine = None
    svc._sessions_table = None


def test_handle_db_error_integrity_one_wip() -> None:
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(HTTPException) as exc:
        svc._handle_db_error(IntegrityError("stmt", {}, Exception("one_wip")))
    assert exc.value.status_code == 409


def test_sync_database_url_missing_raises_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(HTTPException) as exc:
        svc._sync_database_url()
    assert exc.value.status_code == 503


def test_handle_db_error_wip_conflict() -> None:
    with pytest.raises(HTTPException) as exc:
        svc._handle_db_error(Exception("23505 tac_work_sessions_one_wip_per_user"))
    assert exc.value.status_code == 409


def test_handle_db_error_missing_table() -> None:
    with pytest.raises(HTTPException) as exc:
        svc._handle_db_error(Exception('relation "tac_work_sessions" does not exist 42P01'))
    assert exc.value.status_code == 503


def test_handle_db_error_generic_502() -> None:
    with pytest.raises(HTTPException) as exc:
        svc._handle_db_error(Exception("connection refused"))
    assert exc.value.status_code == 502


def test_payload_dict_normalizes_enums() -> None:
    payload = WorkSessionCreate(
        product=WorkSessionProduct.METAR,
        status=WorkSessionStatus.DRAFT,
        manual_tac="METAR X",
    )
    data = svc._payload_dict(payload, user_id="u1")
    assert data["product"] == "metar"
    assert data["status"] == "draft"
    assert data["user_id"] == "u1"


def test_create_session_inserts_row(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    session_id = uuid4()
    user_id = uuid4()
    now = datetime.now(UTC)
    row = {
        "id": session_id,
        "user_id": user_id,
        "product": "metar",
        "status": "draft",
        "title": "",
        "manual_tac": "METAR X",
        "pending_files": [],
        "converted_results": [],
        "errors": [],
        "issues": [],
        "conversion_params": {},
        "kv_upload_key": None,
        "deleted_at": None,
        "created_at": now,
        "updated_at": now,
    }

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.return_value.mappings.return_value.one.return_value = row

    mock_engine = MagicMock()
    mock_engine.begin.return_value = mock_conn

    mock_table = MagicMock()
    mock_table.insert.return_value.values.return_value = "insert"
    mock_table.c.id = MagicMock()

    select_stmt = MagicMock()
    select_stmt.where.return_value = select_stmt

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=mock_table),
        patch("src.services.work_session_service.select", return_value=select_stmt),
    ):
        service = svc.WorkSessionService(str(user_id))
        created = service.create_session(
            str(user_id),
            WorkSessionCreate(product=WorkSessionProduct.METAR, manual_tac="METAR X"),
        )
    assert created.id == session_id
    assert created.manual_tac == "METAR X"


def test_get_session_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.return_value.mappings.return_value.first.return_value = None
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    mock_table = MagicMock()
    select_stmt = MagicMock()
    select_stmt.where.return_value = select_stmt

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=mock_table),
        patch("src.services.work_session_service.select", return_value=select_stmt),
    ):
        service = svc.WorkSessionService(str(uuid4()))
        with pytest.raises(HTTPException) as exc:
            service.get_session(uuid4())
    assert exc.value.status_code == 404


def test_soft_delete_sets_deleted_at(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    session_id = uuid4()
    user_id = uuid4()
    now = datetime.now(UTC)
    live = {
        "id": session_id,
        "user_id": user_id,
        "product": "metar",
        "status": "draft",
        "title": "",
        "manual_tac": "",
        "pending_files": [],
        "converted_results": [],
        "errors": [],
        "issues": [],
        "conversion_params": {},
        "kv_upload_key": None,
        "deleted_at": None,
        "created_at": now,
        "updated_at": now,
    }
    deleted = {**live, "deleted_at": now}

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mappings = MagicMock()
    mappings.first.return_value = live
    mappings.one.return_value = deleted
    mock_conn.execute.return_value.mappings.return_value = mappings

    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    mock_engine.begin.return_value = mock_conn
    mock_table = MagicMock()
    select_stmt = MagicMock()
    select_stmt.where.return_value = select_stmt
    update_stmt = MagicMock()
    update_stmt.where.return_value = update_stmt
    update_stmt.values.return_value = update_stmt

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=mock_table),
        patch("src.services.work_session_service.select", return_value=select_stmt),
        patch("src.services.work_session_service.update", return_value=update_stmt),
    ):
        service = svc.WorkSessionService(str(user_id))
        out = service.soft_delete(session_id)
    assert out.deleted_at is not None


def test_list_sessions_returns_items(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    user_id = uuid4()
    now = datetime.now(UTC)
    row = {
        "id": uuid4(),
        "user_id": user_id,
        "product": "swxa",
        "status": "draft",
        "title": "t",
        "manual_tac": "",
        "pending_files": [],
        "converted_results": [],
        "errors": [],
        "issues": [],
        "conversion_params": {},
        "kv_upload_key": None,
        "deleted_at": None,
        "created_at": now,
        "updated_at": now,
    }
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.return_value.scalar_one.return_value = 1
    mock_conn.execute.return_value.mappings.return_value = [row]
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    mock_table = MagicMock()
    stmt = MagicMock()
    stmt.where.return_value = stmt
    stmt.order_by.return_value = stmt
    stmt.offset.return_value = stmt
    stmt.limit.return_value = stmt
    stmt.subquery.return_value = MagicMock()

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=mock_table),
        patch("src.services.work_session_service.select", return_value=stmt),
        patch("src.services.work_session_service.text", return_value="count(*)"),
    ):
        service = svc.WorkSessionService(str(user_id))
        items, total = service.list_sessions(
            status_filter=WorkSessionStatus.DRAFT,
            products=[WorkSessionProduct.SWXA],
        )
    assert total == 1
    assert items[0].product == WorkSessionProduct.SWXA


def test_update_and_restore(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    session_id = uuid4()
    user_id = uuid4()
    now = datetime.now(UTC)
    row = {
        "id": session_id,
        "user_id": user_id,
        "product": "metar",
        "status": "wip",
        "title": "t",
        "manual_tac": "x",
        "pending_files": [],
        "converted_results": [],
        "errors": [],
        "issues": [],
        "conversion_params": {},
        "kv_upload_key": None,
        "deleted_at": now,
        "created_at": now,
        "updated_at": now,
    }
    restored = {**row, "deleted_at": None}

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mappings = MagicMock()
    mappings.first.return_value = row
    mappings.one.return_value = restored
    mock_conn.execute.return_value.mappings.return_value = mappings
    mock_conn.execute.return_value.rowcount = 1

    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    mock_engine.begin.return_value = mock_conn
    mock_table = MagicMock()
    select_stmt = MagicMock()
    select_stmt.where.return_value = select_stmt
    update_stmt = MagicMock()
    update_stmt.where.return_value = update_stmt
    update_stmt.values.return_value = update_stmt

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=mock_table),
        patch("src.services.work_session_service.select", return_value=select_stmt),
        patch("src.services.work_session_service.update", return_value=update_stmt),
    ):
        service = svc.WorkSessionService(str(user_id))
        updated = service.update_session(
            session_id,
            WorkSessionUpdate(title="new"),
        )
        assert updated.status == WorkSessionStatus.WIP
        out = service.restore_session(session_id)
    assert out.deleted_at is None


def test_sqlalchemy_errors_map_on_crud(monkeypatch: pytest.MonkeyPatch) -> None:
    from sqlalchemy.exc import SQLAlchemyError

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.side_effect = SQLAlchemyError("boom")
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    mock_engine.begin.return_value = mock_conn
    mock_table = MagicMock()
    select_stmt = MagicMock()
    select_stmt.where.return_value = select_stmt
    select_stmt.order_by.return_value = select_stmt
    select_stmt.offset.return_value = select_stmt
    select_stmt.limit.return_value = select_stmt
    select_stmt.subquery.return_value = MagicMock()

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=mock_table),
        patch("src.services.work_session_service.select", return_value=select_stmt),
        patch("src.services.work_session_service.text", return_value="count(*)"),
    ):
        service = svc.WorkSessionService(str(uuid4()))
        with pytest.raises(HTTPException) as exc:
            service.list_sessions()
        assert exc.value.status_code == 502
        with pytest.raises(HTTPException):
            service.get_session(uuid4())
        with pytest.raises(HTTPException):
            service.create_session(
                str(uuid4()),
                WorkSessionCreate(product=WorkSessionProduct.METAR),
            )


def test_update_session_rowcount_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    session_id = uuid4()
    user_id = uuid4()
    now = datetime.now(UTC)
    live = {
        "id": session_id,
        "user_id": user_id,
        "product": "metar",
        "status": "draft",
        "title": "",
        "manual_tac": "",
        "pending_files": [],
        "converted_results": [],
        "errors": [],
        "issues": [],
        "conversion_params": {},
        "kv_upload_key": None,
        "deleted_at": None,
        "created_at": now,
        "updated_at": now,
    }
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mappings = MagicMock()
    mappings.first.return_value = live
    mock_conn.execute.return_value.mappings.return_value = mappings
    mock_conn.execute.return_value.rowcount = 0
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    mock_engine.begin.return_value = mock_conn
    select_stmt = MagicMock()
    select_stmt.where.return_value = select_stmt
    update_stmt = MagicMock()
    update_stmt.where.return_value = update_stmt
    update_stmt.values.return_value = update_stmt

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch("src.services.work_session_service.select", return_value=select_stmt),
        patch("src.services.work_session_service.update", return_value=update_stmt),
    ):
        service = svc.WorkSessionService(str(user_id))
        with pytest.raises(HTTPException) as exc:
            service.update_session(session_id, WorkSessionUpdate(title="x"))
    assert exc.value.status_code == 404


def test_list_sessions_date_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    user_id = uuid4()
    now = datetime.now(UTC)
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.return_value.scalar_one.return_value = 0
    mock_conn.execute.return_value.mappings.return_value = []
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    stmt = MagicMock()
    stmt.where.return_value = stmt
    stmt.order_by.return_value = stmt
    stmt.offset.return_value = stmt
    stmt.limit.return_value = stmt
    stmt.subquery.return_value = MagicMock()
    mock_table = MagicMock()
    updated_at = MagicMock()
    updated_at.__ge__ = MagicMock(return_value=True)
    updated_at.__le__ = MagicMock(return_value=True)
    mock_table.c.updated_at = updated_at
    mock_table.c.user_id = MagicMock()
    mock_table.c.deleted_at = MagicMock()
    mock_table.c.deleted_at.is_ = MagicMock(return_value=True)

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=mock_table),
        patch("src.services.work_session_service.select", return_value=stmt),
        patch("src.services.work_session_service.text", return_value="count(*)"),
    ):
        service = svc.WorkSessionService(str(user_id))
        items, total = service.list_sessions(
            from_dt=now,
            to_dt=now,
            include_deleted=True,
        )
    assert items == []
    assert total == 0


def test_soft_delete_db_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from sqlalchemy.exc import SQLAlchemyError

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    session_id = uuid4()
    user_id = uuid4()
    now = datetime.now(UTC)
    live = {
        "id": session_id,
        "user_id": user_id,
        "product": "metar",
        "status": "draft",
        "title": "",
        "manual_tac": "",
        "pending_files": [],
        "converted_results": [],
        "errors": [],
        "issues": [],
        "conversion_params": {},
        "kv_upload_key": None,
        "deleted_at": None,
        "created_at": now,
        "updated_at": now,
    }
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mappings = MagicMock()
    mappings.first.return_value = live
    mock_conn.execute.return_value.mappings.return_value = mappings

    begin_conn = MagicMock()
    begin_conn.__enter__ = MagicMock(return_value=begin_conn)
    begin_conn.__exit__ = MagicMock(return_value=False)
    begin_conn.execute.side_effect = SQLAlchemyError("boom")

    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    mock_engine.begin.return_value = begin_conn
    select_stmt = MagicMock()
    select_stmt.where.return_value = select_stmt
    update_stmt = MagicMock()
    update_stmt.where.return_value = update_stmt
    update_stmt.values.return_value = update_stmt

    with (
        patch.object(svc, "_get_engine", return_value=mock_engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch("src.services.work_session_service.select", return_value=select_stmt),
        patch("src.services.work_session_service.update", return_value=update_stmt),
    ):
        service = svc.WorkSessionService(str(user_id))
        with pytest.raises(HTTPException) as exc:
            service.soft_delete(session_id)
    assert exc.value.status_code == 502

    from fastapi.security import HTTPAuthorizationCredentials

    from src.utilities.security import verify_supabase_token

    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_JWKS_URL", raising=False)

    async def _run() -> None:
        with pytest.raises(HTTPException) as exc:
            await verify_supabase_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="x"))
        assert exc.value.status_code == 503

    import asyncio

    asyncio.run(_run())


def test_verify_supabase_token_jwks_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.security import HTTPAuthorizationCredentials

    from src.utilities import security as sec

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")

    async def _run() -> None:
        with patch.object(
            sec,
            "verify_access_token",
            return_value={"sub": "user-1"},
        ):
            claims = await sec.verify_supabase_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok"))
        assert claims["sub"] == "user-1"

    import asyncio

    asyncio.run(_run())
