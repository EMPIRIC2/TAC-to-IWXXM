"""Unit tests for DisseminationOpsService DB paths (mocked SQLAlchemy)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.schemas.dissemination_ops import (
    DisseminationPlanCreate,
    DisseminationPlanUpdate,
    MappingConfigCreate,
    MappingConfigUpdate,
)
from src.services import dissemination_ops_service as svc

USER_ID = uuid4()
NOW = datetime(2026, 9, 3, tzinfo=UTC)


def test_invalid_user_id_raises_401() -> None:
    with pytest.raises(HTTPException) as exc:
        svc.DisseminationOpsService("not-a-uuid")
    assert exc.value.status_code == 401


class _Result:
    def __init__(self, row: dict[str, Any] | None = None, rows: list[dict[str, Any]] | None = None) -> None:
        self._row = row
        self._rows = rows if rows is not None else ([] if row is None else [row])

    def mappings(self) -> _Result:
        return self

    def first(self) -> dict[str, Any] | None:
        return self._row

    def all(self) -> list[dict[str, Any]]:
        return self._rows


def _stmt_chain() -> MagicMock:
    stmt = MagicMock()
    stmt.where.return_value = stmt
    stmt.order_by.return_value = stmt
    stmt.offset.return_value = stmt
    stmt.limit.return_value = stmt
    return stmt


@pytest.fixture
def service() -> svc.DisseminationOpsService:
    return svc.DisseminationOpsService(str(USER_ID))


def _plan_row(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": uuid4(),
        "user_id": USER_ID,
        "slug": "default",
        "validity_policy": "valid-only",
        "destination_refs": ["amhs"],
        "transforms": [],
        "retry": None,
        "created_at": NOW,
        "updated_at": NOW,
    }
    base.update(overrides)
    return base


def test_sync_database_url_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@h/db?ssl=require")
    url = svc._sync_database_url()
    assert url.startswith("postgresql+psycopg://")
    assert "sslmode=require" in url

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://u:p@h/db")
    assert svc._sync_database_url().startswith("postgresql+psycopg://")

    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    assert svc._sync_database_url().startswith("postgresql+psycopg://")

    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    assert svc._sync_database_url() == "sqlite:///:memory:"

    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(HTTPException) as exc:
        svc._sync_database_url()
    assert exc.value.status_code == 503


def test_create_plan_ok(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = conn
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
    ):
        out = service.create_plan(DisseminationPlanCreate(slug="p1", destination_refs=["amhs"]))
    assert out.slug == "p1"
    assert out.user_id == USER_ID
    conn.execute.assert_called_once()


def test_create_plan_integrity_conflict(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    engine.begin.return_value.__enter__.side_effect = IntegrityError("stmt", {}, Exception("dup"))
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=MagicMock()),
        pytest.raises(HTTPException) as exc,
    ):
        service.create_plan(DisseminationPlanCreate(slug="p1"))
    assert exc.value.status_code == 409


def test_create_plan_generic_db_error(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=MagicMock()),
        pytest.raises(HTTPException) as exc,
    ):
        service.create_plan(DisseminationPlanCreate(slug="p1"))
    assert exc.value.status_code == 503


def test_get_plan_found_and_missing(service: svc.DisseminationOpsService) -> None:
    row = _plan_row()
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        assert service.get_plan(row["id"]).slug == "default"

    conn.execute.return_value = _Result(None)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.get_plan(uuid4())
    assert exc.value.status_code == 404


def test_update_plan(service: svc.DisseminationOpsService) -> None:
    row = _plan_row()
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    engine.begin.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row)
    table = MagicMock()
    table.update.return_value.where.return_value.values.return_value = "upd"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=table),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        out = service.update_plan(row["id"], DisseminationPlanUpdate(validity_policy="warn-ok"))
    assert out.validity_policy == "warn-ok"


def test_record_and_list_and_get_audit(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = conn
    engine.connect.return_value.__enter__.return_value = conn
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
    ):
        recorded = service.record_audit(
            status_value="SKIPPED",
            gateway="amhs",
            detail="dry_run",
            product="metar",
            station="KJFK",
            profile="annex3",
            iwxxm_version="2025-2",
            message_id="m1",
            destinations={"amhs": "SKIPPED"},
        )
    assert recorded.status == "SKIPPED"

    audit_row = recorded.model_dump()
    conn.execute.return_value = _Result(rows=[audit_row])
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        items, total = service.list_audit(
            product="metar",
            station="KJFK",
            profile="annex3",
            status_filter="SKIPPED",
            page=1,
            limit=20,
        )
    assert total == 1
    assert items[0].gateway == "amhs"

    conn.execute.return_value = _Result(audit_row)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        assert service.get_audit(recorded.id).id == recorded.id

    conn.execute.return_value = _Result(None)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException),
    ):
        service.get_audit(uuid4())


def test_mapping_crud(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = conn
    engine.connect.return_value.__enter__.return_value = conn
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
    ):
        created = service.create_mapping(MappingConfigCreate(name="m1", mode="sink", config={"iwxxm": "x"}))
    assert created.name == "m1"

    row = created.model_dump()
    conn.execute.return_value = _Result(row)
    table = MagicMock()
    table.update.return_value.where.return_value.values.return_value = "upd"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=table),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        assert service.get_mapping(created.id).mode == "sink"
        updated = service.update_mapping(created.id, MappingConfigUpdate(mode="source"))
    assert updated.mode == "source"

    conn.execute.return_value = _Result(None)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException),
    ):
        service.get_mapping(uuid4())


def test_get_engine_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    svc._engine = None
    svc._tables.clear()
    with patch.object(svc, "create_engine", return_value=MagicMock()) as ce:
        e1 = svc._get_engine()
        e2 = svc._get_engine()
    assert e1 is e2
    ce.assert_called_once()
    svc._engine = None


def test_table_autoload_caches() -> None:
    svc._tables.clear()
    engine = MagicMock()
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "Table", return_value=MagicMock()) as table_ctor,
    ):
        t1 = svc._table("tac_dissemination_plans")
        t2 = svc._table("tac_dissemination_plans")
    assert t1 is t2
    table_ctor.assert_called_once()
    svc._tables.clear()


def test_list_audit_db_error(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    engine.connect.return_value.__enter__.side_effect = SQLAlchemyError("x")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.list_audit()
    assert exc.value.status_code == 503


def test_get_plan_db_error(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    engine.connect.return_value.__enter__.side_effect = SQLAlchemyError("x")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.get_plan(uuid4())
    assert exc.value.status_code == 503


def test_list_audit_page_total_branch(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    rows = [
        {
            "id": uuid4(),
            "user_id": USER_ID,
            "message_id": None,
            "station": None,
            "profile": None,
            "iwxxm_version": None,
            "product": None,
            "status": "DELIVERED",
            "gateway": "amhs",
            "detail": None,
            "destinations": {},
            "created_at": NOW,
        }
        for _ in range(2)
    ]
    conn.execute.return_value = _Result(rows=rows)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        _, total = service.list_audit(page=2, limit=2)
    assert total == 4


def test_reject_nested_list_secrets() -> None:
    with pytest.raises(HTTPException):
        svc._reject_secrets({"items": [{"token": "x"}]})


def test_record_audit_rejects_secret_destinations(
    service: svc.DisseminationOpsService,
) -> None:
    with pytest.raises(HTTPException):
        service.record_audit(
            status_value="FAILED",
            gateway="amhs",
            destinations={"uri": "secret"},
        )


def _db_error_on_begin(service: svc.DisseminationOpsService, fn) -> None:
    engine = MagicMock()
    engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("x")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        fn()
    assert exc.value.status_code == 503


def test_update_plan_db_error(service: svc.DisseminationOpsService) -> None:
    row = _plan_row()
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row)
    engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("x")
    table = MagicMock()
    table.update.return_value.where.return_value.values.return_value = "upd"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=table),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.update_plan(row["id"], DisseminationPlanUpdate(transforms=["a"]))
    assert exc.value.status_code == 503


def test_record_audit_db_error(service: svc.DisseminationOpsService) -> None:
    _db_error_on_begin(
        service,
        lambda: service.record_audit(status_value="FAILED", gateway="amhs"),
    )


def test_get_audit_db_error(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    engine.connect.return_value.__enter__.side_effect = SQLAlchemyError("x")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.get_audit(uuid4())
    assert exc.value.status_code == 503


def test_create_mapping_db_error(service: svc.DisseminationOpsService) -> None:
    _db_error_on_begin(
        service,
        lambda: service.create_mapping(MappingConfigCreate(name="m", mode="sink", config={})),
    )


def test_get_mapping_db_error(service: svc.DisseminationOpsService) -> None:
    engine = MagicMock()
    engine.connect.return_value.__enter__.side_effect = SQLAlchemyError("x")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.get_mapping(uuid4())
    assert exc.value.status_code == 503


def test_update_mapping_db_error(service: svc.DisseminationOpsService) -> None:
    row = {
        "id": uuid4(),
        "user_id": USER_ID,
        "name": "m",
        "mode": "sink",
        "config": {},
        "created_at": NOW,
        "updated_at": NOW,
    }
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row)
    engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("x")
    table = MagicMock()
    table.update.return_value.where.return_value.values.return_value = "upd"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=table),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.update_mapping(row["id"], MappingConfigUpdate(mode="source"))
    assert exc.value.status_code == 503
