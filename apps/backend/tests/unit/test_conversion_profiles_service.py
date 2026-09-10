"""Unit tests for ConversionProfilesService DB paths (mocked SQLAlchemy)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.schemas.conversion_profiles import (
    DisseminationTemplateCreate,
    DisseminationTemplateUpdate,
    OverlayCreate,
    OverlayUpdate,
    PresetCreate,
    PresetUpdate,
    RulePackCreate,
    RulePackUpdate,
)
from src.services import conversion_profiles_service as svc
from src.services.profile_overlay import sign_overlay

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


def _preset_row(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": PACK_ID,
        "user_id": USER_ID,
        "slug": "icao-2025-default",
        "name": "ICAO 2025 default",
        "semantic_profile": "ICAO_2025",
        "iwxxm_version": "2025-2",
        "extensions": [],
        "report_variant": None,
        "overlay_id": None,
        "shared": False,
        "created_at": NOW,
        "updated_at": NOW,
    }
    base.update(overrides)
    return base


def _template_row(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": PACK_ID,
        "user_id": USER_ID,
        "slug": "ops-postgres",
        "name": "Ops Postgres",
        "sink_type": "postgres",
        "product": "metar",
        "ddl": False,
        "params": {"schema": "public"},
        "shared": True,
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


def test_preset_list_get_create_update_delete(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.return_value.rowcount = 1
    created_row = _preset_row(slug="us-default", name="US Default", semantic_profile="US_FAA_NWS", shared=True)
    updated_row = {**created_row, "name": "US Default 2"}
    read_conn.execute.side_effect = [
        _Result(rows=[created_row]),
        _Result(row=created_row),
        _Result(row=created_row),
        _Result(row=created_row),
        _Result(row=updated_row),
    ]
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="owner-or-shared"),
    ):
        items = service.list_presets()
        assert items[0].slug == "us-default"
        created = service.create_preset(
            PresetCreate(
                slug="us-default",
                name="US Default",
                semantic_profile="US_FAA_NWS",
                iwxxm_version="2025-2",
                extensions=["IWXXM_US_3"],
                shared=True,
            )
        )
        assert created.semantic_profile == "US_FAA_NWS"
        got = service.get_preset(PACK_ID)
        assert got.name == "US Default"
        updated = service.update_preset(PACK_ID, PresetUpdate(name="US Default 2"))
        assert updated.name == "US Default 2"
        service.delete_preset(PACK_ID)


def test_preset_not_found_forbidden_and_db_errors(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=None)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as missing,
    ):
        service.get_preset(PACK_ID)
    assert missing.value.status_code == 404

    other = uuid4()
    conn.execute.return_value = _Result(row=_preset_row(user_id=other, shared=False))
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as forbidden,
    ):
        service.get_preset(PACK_ID)
    assert forbidden.value.status_code == 403

    engine2 = MagicMock()
    engine2.begin.return_value.__enter__.side_effect = SQLAlchemyError("boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine2),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=MagicMock()),
        pytest.raises(HTTPException) as create_exc,
    ):
        service.create_preset(
            PresetCreate(
                slug="icao",
                name="ICAO",
                semantic_profile="ICAO_2025",
                iwxxm_version="2025-2",
            )
        )
    assert create_exc.value.status_code == 503


def test_template_list_get_create_update_delete(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.return_value.rowcount = 1
    created_row = _template_row()
    updated_row = {**created_row, "name": "Ops Postgres 2", "ddl": True}
    read_conn.execute.side_effect = [
        _Result(rows=[created_row]),
        _Result(row=created_row),
        _Result(row=created_row),
        _Result(row=created_row),
        _Result(row=updated_row),
    ]
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="owner-or-shared"),
    ):
        items = service.list_templates()
        assert items[0].slug == "ops-postgres"
        created = service.create_template(
            DisseminationTemplateCreate(
                slug="ops-postgres",
                name="Ops Postgres",
                sink_type="postgres",
                product="metar",
                ddl=False,
                params={"schema": "public"},
                shared=True,
            )
        )
        assert created.sink_type == "postgres"
        got = service.get_template(PACK_ID)
        assert got.name == "Ops Postgres"
        updated = service.update_template(PACK_ID, DisseminationTemplateUpdate(name="Ops Postgres 2", ddl=True))
        assert updated.name == "Ops Postgres 2"
        assert updated.ddl is True
        service.delete_template(PACK_ID)


def test_template_rejects_secret_values_and_handles_errors(service: svc.ConversionProfilesService) -> None:
    with pytest.raises(HTTPException) as uri_exc:
        service.create_template(
            DisseminationTemplateCreate(
                slug="bad-uri",
                name="Bad URI",
                sink_type="wis2",
                params={"endpoint": "mqtt://example.com"},
            )
        )
    assert uri_exc.value.status_code == 422

    with pytest.raises(HTTPException) as token_exc:
        service.create_template(
            DisseminationTemplateCreate(
                slug="bad-token",
                name="Bad Token",
                sink_type="wis2",
                params={"token": "secret"},
            )
        )
    assert token_exc.value.status_code == 422

    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=None)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as missing,
    ):
        service.get_template(PACK_ID)
    assert missing.value.status_code == 404

    other = uuid4()
    conn.execute.return_value = _Result(row=_template_row(user_id=other, shared=False))
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as forbidden,
    ):
        service.get_template(PACK_ID)
    assert forbidden.value.status_code == 403

    with pytest.raises(HTTPException) as list_uri_exc:
        svc._reject_template_values({"items": ["mqtt://example.com"]}, path="params")
    assert list_uri_exc.value.status_code == 422


def test_preset_and_template_extra_error_paths(service: svc.ConversionProfilesService) -> None:
    shared_other = uuid4()

    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.side_effect = [
        SQLAlchemyError("presets list boom"),
        SQLAlchemyError("preset get boom"),
        _Result(row=_preset_row(user_id=shared_other, shared=True)),
        SQLAlchemyError("templates list boom"),
        SQLAlchemyError("template get boom"),
        _Result(row=_template_row(user_id=shared_other, shared=True)),
        _Result(row=_template_row()),
        _Result(row=_template_row()),
    ]
    with (
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="owner-or-shared"),
    ):
        with patch.object(svc, "_get_engine", return_value=engine), pytest.raises(HTTPException) as exc:
            service.list_presets()
        assert exc.value.status_code == 503

        with patch.object(svc, "_get_engine", return_value=engine), pytest.raises(HTTPException) as exc:
            service.get_preset(PACK_ID)
        assert exc.value.status_code == 503

        with patch.object(svc, "_get_engine", return_value=engine), pytest.raises(HTTPException) as exc:
            service.get_preset(PACK_ID, require_owner=True)
        assert exc.value.status_code == 403

        with patch.object(svc, "_get_engine", return_value=engine), pytest.raises(HTTPException) as exc:
            service.list_templates()
        assert exc.value.status_code == 503

        with patch.object(svc, "_get_engine", return_value=engine), pytest.raises(HTTPException) as exc:
            service.get_template(PACK_ID)
        assert exc.value.status_code == 503

        with patch.object(svc, "_get_engine", return_value=engine), pytest.raises(HTTPException) as exc:
            service.get_template(PACK_ID, require_owner=True)
        assert exc.value.status_code == 403

    preset_engine = MagicMock()
    preset_conn = MagicMock()
    preset_engine.connect.return_value.__enter__.return_value = preset_conn
    preset_conn.execute.return_value = _Result(row=_preset_row())
    with (
        patch.object(svc, "_get_engine", return_value=preset_engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        preset = service.update_preset(PACK_ID, PresetUpdate())
    assert preset.id == PACK_ID

    template_engine = MagicMock()
    template_conn = MagicMock()
    template_engine.connect.return_value.__enter__.return_value = template_conn
    template_conn.execute.return_value = _Result(row=_template_row())
    with (
        patch.object(svc, "_get_engine", return_value=template_engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        template = service.update_template(PACK_ID, DisseminationTemplateUpdate())
    assert template.id == PACK_ID

    begin_engine = MagicMock()
    begin_engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("write boom")
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"

    with patch.object(svc, "_table", return_value=MagicMock()):
        with (
            patch.object(svc, "_get_engine", return_value=begin_engine),
            patch.object(svc, "insert", return_value=ins),
            pytest.raises(HTTPException) as exc,
        ):
            service.create_template(
                DisseminationTemplateCreate(
                    slug="ops-postgres",
                    name="Ops Postgres",
                    sink_type="postgres",
                    product="metar",
                    params={"schema": "public"},
                )
            )
        assert exc.value.status_code == 503

        with (
            patch.object(svc, "_get_engine", return_value=begin_engine),
            patch.object(svc, "update", return_value=upd),
            pytest.raises(HTTPException) as exc,
        ):
            service.update_preset(PACK_ID, PresetUpdate(name="changed"))
        assert exc.value.status_code == 503

        with (
            patch.object(svc, "_get_engine", return_value=begin_engine),
            patch.object(svc, "delete", return_value=dele),
            pytest.raises(HTTPException) as exc,
        ):
            service.delete_preset(PACK_ID)
        assert exc.value.status_code == 503

        with (
            patch.object(svc, "_get_engine", return_value=begin_engine),
            patch.object(svc, "update", return_value=upd),
            pytest.raises(HTTPException) as exc,
        ):
            service.update_template(PACK_ID, DisseminationTemplateUpdate(name="changed"))
        assert exc.value.status_code == 503

        with (
            patch.object(svc, "_get_engine", return_value=begin_engine),
            patch.object(svc, "delete", return_value=dele),
            pytest.raises(HTTPException) as exc,
        ):
            service.delete_template(PACK_ID)
        assert exc.value.status_code == 503


def test_reject_template_values_list_safe_item_returns() -> None:
    svc._reject_template_values(["safe-value"], path="params")


def test_preset_update_delete_not_found_and_db_error(service: svc.ConversionProfilesService) -> None:
    read_engine = MagicMock()
    read_conn = MagicMock()
    read_engine.connect.return_value.__enter__.return_value = read_conn
    read_conn.execute.return_value = _Result(row=_preset_row())

    missing_begin_engine = MagicMock()
    missing_begin_conn = MagicMock()
    missing_begin_engine.connect.return_value.__enter__.return_value = read_conn
    missing_begin_engine.begin.return_value.__enter__.return_value = missing_begin_conn
    missing_begin_conn.execute.return_value.rowcount = 0
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=missing_begin_engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
    ):
        with pytest.raises(HTTPException) as exc:
            service.update_preset(PACK_ID, PresetUpdate(name="changed"))
        assert exc.value.status_code == 404
        with pytest.raises(HTTPException) as exc:
            service.delete_preset(PACK_ID)
        assert exc.value.status_code == 404

    error_engine = MagicMock()
    error_engine.connect.return_value.__enter__.return_value = read_conn
    error_engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("boom")
    with (
        patch.object(svc, "_get_engine", return_value=error_engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
    ):
        with pytest.raises(HTTPException) as exc:
            service.update_preset(PACK_ID, PresetUpdate(name="changed"))
        assert exc.value.status_code == 503
        with pytest.raises(HTTPException) as exc:
            service.delete_preset(PACK_ID)
        assert exc.value.status_code == 503


def test_template_update_delete_not_found_and_db_error(service: svc.ConversionProfilesService) -> None:
    read_engine = MagicMock()
    read_conn = MagicMock()
    read_engine.connect.return_value.__enter__.return_value = read_conn
    read_conn.execute.return_value = _Result(row=_template_row())

    missing_begin_engine = MagicMock()
    missing_begin_conn = MagicMock()
    missing_begin_engine.connect.return_value.__enter__.return_value = read_conn
    missing_begin_engine.begin.return_value.__enter__.return_value = missing_begin_conn
    missing_begin_conn.execute.return_value.rowcount = 0
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=missing_begin_engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
    ):
        with pytest.raises(HTTPException) as exc:
            service.update_template(PACK_ID, DisseminationTemplateUpdate(name="changed"))
        assert exc.value.status_code == 404
        with pytest.raises(HTTPException) as exc:
            service.delete_template(PACK_ID)
        assert exc.value.status_code == 404

    error_engine = MagicMock()
    error_engine.connect.return_value.__enter__.return_value = read_conn
    error_engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("boom")
    with (
        patch.object(svc, "_get_engine", return_value=error_engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
    ):
        with pytest.raises(HTTPException) as exc:
            service.update_template(PACK_ID, DisseminationTemplateUpdate(name="changed"))
        assert exc.value.status_code == 503
        with pytest.raises(HTTPException) as exc:
            service.delete_template(PACK_ID)
        assert exc.value.status_code == 503


def test_update_template_with_safe_params(service: svc.ConversionProfilesService) -> None:
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.return_value.rowcount = 1
    existing_row = _template_row()
    updated_row = _template_row(params={"schema": "next"})
    read_conn.execute.side_effect = [_Result(row=existing_row), _Result(row=updated_row)]
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "update", return_value=upd),
    ):
        updated = service.update_template(
            PACK_ID,
            DisseminationTemplateUpdate(params={"schema": "next"}),
        )
    assert updated.params == {"schema": "next"}


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
    read_conn.execute.return_value = _Result(row=_pack_row(slug="metar-hard", severity="error"))
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
        out = service.update_rule_pack(PACK_ID, RulePackUpdate(slug="metar-hard", severity="error"))
        assert out.slug == "metar-hard"
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


def test_overlay_crud(service: svc.ConversionProfilesService, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROFILE_OVERLAY_HMAC_SECRET", "unit-secret")
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.return_value.rowcount = 1
    body = {"lint": {"severity": "warning"}}
    row = {
        "id": PACK_ID,
        "user_id": USER_ID,
        "slug": "ov1",
        "base_profile_id": "ICAO_2025",
        "body": body,
        "signature": sign_overlay(user_id=USER_ID, base_profile_id="ICAO_2025", body=body),
        "shared": False,
        "created_at": NOW,
        "updated_at": NOW,
    }
    updated_row = {**row, "slug": "ov2", "shared": True}
    read_conn.execute.side_effect = [
        _Result(row=row),
        _Result(rows=[row]),
        _Result(row=row),
        _Result(row=row),
        _Result(row=updated_row),
    ]
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="owner-or-shared"),
    ):
        created = service.create_overlay(OverlayCreate(slug="ov1", base_profile_id="ICAO_2025", body=body))
        assert created.slug == "ov1"
        assert service.list_overlays()[0].slug == "ov1"
        assert service.get_overlay(PACK_ID).base_profile_id == "ICAO_2025"
        updated = service.update_overlay(PACK_ID, OverlayUpdate(slug="ov2", shared=True))
        assert updated.slug == "ov2"
        assert updated.shared is True
        service.delete_overlay(PACK_ID)


def test_overlay_foreign_owner_forbidden(
    service: svc.ConversionProfilesService, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PROFILE_OVERLAY_HMAC_SECRET", "unit-secret")
    other = uuid4()
    body = {"x": 1}
    row = {
        "id": PACK_ID,
        "user_id": other,
        "slug": "foreign",
        "base_profile_id": "ICAO_2025",
        "body": body,
        "signature": sign_overlay(user_id=other, base_profile_id="ICAO_2025", body=body),
        "shared": False,
        "created_at": NOW,
        "updated_at": NOW,
    }
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=row)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as exc,
    ):
        service.get_overlay(PACK_ID)
    assert exc.value.status_code == 403


def test_overlay_get_db_error(service: svc.ConversionProfilesService, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROFILE_OVERLAY_HMAC_SECRET", "unit-secret")
    engine = MagicMock()
    engine.connect.return_value.__enter__.side_effect = SQLAlchemyError("get boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.get_overlay(PACK_ID)

    monkeypatch.setenv("PROFILE_OVERLAY_HMAC_SECRET", "unit-secret")
    sig = sign_overlay(user_id=USER_ID, base_profile_id="ICAO_2025", body={})
    row = {
        "id": PACK_ID,
        "user_id": USER_ID,
        "slug": "ov",
        "base_profile_id": "ICAO_2025",
        "body": "not-a-dict",
        "signature": sig,
        "shared": False,
        "created_at": NOW,
        "updated_at": NOW,
    }
    out = service._overlay_to_out(row)
    assert out.body == {}


def test_overlay_get_not_found_and_require_owner(
    service: svc.ConversionProfilesService, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PROFILE_OVERLAY_HMAC_SECRET", "unit-secret")
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=None)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as missing,
    ):
        service.get_overlay(PACK_ID)
    assert missing.value.status_code == 404

    other = uuid4()
    body = {"ok": True}
    shared_row = {
        "id": PACK_ID,
        "user_id": other,
        "slug": "shared",
        "base_profile_id": "ICAO_2025",
        "body": body,
        "signature": sign_overlay(user_id=other, base_profile_id="ICAO_2025", body=body),
        "shared": True,
        "created_at": NOW,
        "updated_at": NOW,
    }
    conn.execute.return_value = _Result(row=shared_row)
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        got = service.get_overlay(PACK_ID)
        assert got.shared is True
        with pytest.raises(HTTPException) as owner_exc:
            service.get_overlay(PACK_ID, require_owner=True)
        assert owner_exc.value.status_code == 403


def test_overlay_db_errors_and_empty_update(
    service: svc.ConversionProfilesService, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PROFILE_OVERLAY_HMAC_SECRET", "unit-secret")
    body = {"lint": True}
    row = {
        "id": PACK_ID,
        "user_id": USER_ID,
        "slug": "ov1",
        "base_profile_id": "ICAO_2025",
        "body": body,
        "signature": sign_overlay(user_id=USER_ID, base_profile_id="ICAO_2025", body=body),
        "shared": False,
        "created_at": NOW,
        "updated_at": NOW,
    }
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    read_conn.execute.return_value = _Result(row=row, rows=[row])
    begin_conn.execute.side_effect = SQLAlchemyError("boom")

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=MagicMock(values=MagicMock(return_value="i"))),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")) as handle,
        pytest.raises(HTTPException),
    ):
        service.create_overlay(OverlayCreate(slug="ov1", base_profile_id="ICAO_2025", body=body))
    handle.assert_called()

    begin_conn.execute.side_effect = None
    begin_conn.execute.return_value.rowcount = 0
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as upd_exc,
    ):
        service.update_overlay(PACK_ID, OverlayUpdate(shared=True))
    assert upd_exc.value.status_code == 404

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        unchanged = service.update_overlay(PACK_ID, OverlayUpdate())
        assert unchanged.slug == "ov1"

    begin_conn.execute.side_effect = SQLAlchemyError("list boom")
    engine.connect.return_value.__enter__.side_effect = SQLAlchemyError("list boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="x"),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.list_overlays()

    engine.connect.return_value.__enter__.side_effect = None
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.side_effect = None
    begin_conn.execute.return_value.rowcount = 0
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "delete", return_value=dele),
        pytest.raises(HTTPException) as del_exc,
    ):
        service.delete_overlay(PACK_ID)
    assert del_exc.value.status_code == 404

    begin_conn.execute.side_effect = SQLAlchemyError("del boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "delete", return_value=dele),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.delete_overlay(PACK_ID)

    begin_conn.execute.side_effect = SQLAlchemyError("upd boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.update_overlay(PACK_ID, OverlayUpdate(body={"y": 2}))
