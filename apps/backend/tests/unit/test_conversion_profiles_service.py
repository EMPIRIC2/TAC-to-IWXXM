"""Unit tests for ConversionProfilesService DB paths (mocked SQLAlchemy)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.schemas.conversion_profiles import RulePackCreate, RulePackUpdate
from src.services import conversion_profiles_service as svc

USER_ID = uuid4()
PACK_ID = uuid4()
NOW = datetime(2026, 9, 3, tzinfo=UTC)


def test_invalid_user_id_raises_401() -> None:
    with pytest.raises(HTTPException) as exc:
        svc.ConversionProfilesService("not-a-uuid")
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
    return stmt


def _pack_row(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": PACK_ID,
        "user_id": USER_ID,
        "slug": "metar-soft",
        "profile": "ICAO_2025",
        "product": "METAR",
        "stage": "lint",
        "severity": "warning",
        "when_expr": "x",
        "message": "m",
        "standard_reference": "ref",
        "created_at": NOW,
        "updated_at": NOW,
    }
    base.update(overrides)
    return base


@pytest.fixture
def service() -> svc.ConversionProfilesService:
    return svc.ConversionProfilesService(str(USER_ID))


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


def test_reject_secrets() -> None:
    with pytest.raises(HTTPException) as exc:
        svc._reject_secrets({"password": "x"})
    assert exc.value.status_code == 422
    svc._reject_secrets({"ok": {"nested": "fine"}})


def test_list_and_get(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    row = _pack_row()
    conn.execute.return_value = _Result(row=row, rows=[row])
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        items = service.list_rule_packs()
        assert items[0].slug == "metar-soft"
        got = service.get_rule_pack(PACK_ID)
        assert got.id == PACK_ID


def test_get_missing(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=None)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.get_rule_pack(PACK_ID)
    assert exc.value.status_code == 404


def test_create_ok(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    read_conn.execute.return_value = _Result(row=_pack_row(slug="new"))
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        out = service.create_rule_pack(
            RulePackCreate(
                slug="new",
                profile="ICAO_2025",
                product="METAR",
                stage="lint",
                severity="info",
            )
        )
    assert out.slug == "new"


def test_create_integrity(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    engine.begin.return_value.__enter__.side_effect = IntegrityError("stmt", {}, Exception("dup"))
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=MagicMock()),
        pytest.raises(HTTPException) as exc,
    ):
        service.create_rule_pack(
            RulePackCreate(
                slug="x",
                profile="ICAO_2025",
                product="METAR",
                stage="lint",
                severity="info",
            )
        )
    assert exc.value.status_code == 409


def test_create_db_error(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=MagicMock()),
        pytest.raises(HTTPException) as exc,
    ):
        service.create_rule_pack(
            RulePackCreate(
                slug="x",
                profile="ICAO_2025",
                product="METAR",
                stage="lint",
                severity="info",
            )
        )
    assert exc.value.status_code == 503


def test_update_and_delete(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.return_value.rowcount = 1
    read_conn.execute.return_value = _Result(row=_pack_row(severity="error"))
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        out = service.update_rule_pack(PACK_ID, RulePackUpdate(severity="error"))
        assert out.severity == "error"
        service.delete_rule_pack(PACK_ID)


def test_update_empty_and_missing(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=_pack_row())
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        out = service.update_rule_pack(PACK_ID, RulePackUpdate())
        assert out.slug == "metar-soft"

    begin_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    begin_conn.execute.return_value.rowcount = 0
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "update", return_value=upd),
        pytest.raises(HTTPException) as exc,
    ):
        service.update_rule_pack(PACK_ID, RulePackUpdate(severity="x"))
    assert exc.value.status_code == 404


def test_delete_missing(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    begin_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    begin_conn.execute.return_value.rowcount = 0
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "delete", return_value=dele),
        pytest.raises(HTTPException) as exc,
    ):
        service.delete_rule_pack(PACK_ID)
    assert exc.value.status_code == 404


def test_list_db_error(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    engine.connect.return_value.__enter__.side_effect = SQLAlchemyError("boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.list_rule_packs()
    assert exc.value.status_code == 503


def test_get_update_delete_db_errors(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    engine.connect.return_value.__enter__.side_effect = SQLAlchemyError("boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.get_rule_pack(PACK_ID)
    assert exc.value.status_code == 503

    engine2 = MagicMock()
    engine2.begin.return_value.__enter__.side_effect = SQLAlchemyError("boom")
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=engine2),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "update", return_value=upd),
        pytest.raises(HTTPException) as exc2,
    ):
        service.update_rule_pack(PACK_ID, RulePackUpdate(severity="x"))
    assert exc2.value.status_code == 503

    with (
        patch.object(svc, "_get_engine", return_value=engine2),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "delete", return_value=dele),
        pytest.raises(HTTPException) as exc3,
    ):
        service.delete_rule_pack(PACK_ID)
    assert exc3.value.status_code == 503


def test_table_autoload_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    svc._engine = None
    svc._tables.clear()
    engine = MagicMock()
    table = MagicMock()
    with (
        patch.object(svc, "create_engine", return_value=engine),
        patch.object(svc, "Table", return_value=table) as table_ctor,
    ):
        t1 = svc._table("tac_profile_rule_packs")
        t2 = svc._table("tac_profile_rule_packs")
        assert t1 is t2 is table
        table_ctor.assert_called_once()
    svc._engine = None
    svc._tables.clear()


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
