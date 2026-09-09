"""TC-EV1051-002..006 closeout — named ownership / secret / apply asserts.

Complements `test_tc_ev1051_001_convert_preset.py` and existing profiles/dissemination suites.
[Corpus: tests §TC-EV1051] [Corpus: product §F7.w]
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from src.schemas.conversion_profiles import DisseminationTemplateCreate
from src.services import conversion_profiles_service as svc

OWNER = uuid4()
READER = uuid4()
PRESET_ID = uuid4()
TEMPLATE_ID = uuid4()
NOW = datetime(2026, 9, 9, tzinfo=UTC)


class _Result:
    def __init__(self, row: dict[str, Any] | None = None, rows: list[dict[str, Any]] | None = None) -> None:
        self._row = row
        self._rows = rows if rows is not None else ([] if row is None else [row])
        self.rowcount = 1

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
    stmt.values.return_value = stmt
    return stmt


def _preset_row(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": PRESET_ID,
        "user_id": OWNER,
        "slug": "shared-ca",
        "name": "Shared CA",
        "semantic_profile": "CA_ECCC",
        "iwxxm_version": "3.0.0",
        "extensions": [],
        "report_variant": "LWIS",
        "overlay_id": None,
        "shared": True,
        "created_at": NOW,
        "updated_at": NOW,
    }
    base.update(overrides)
    return base


def _template_row(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": TEMPLATE_ID,
        "user_id": OWNER,
        "slug": "ops-sqlite",
        "name": "Ops SQLite",
        "sink_type": "sqlite",
        "product": "metar",
        "ddl": False,
        "params": {"table": "reports"},
        "shared": True,
        "created_at": NOW,
        "updated_at": NOW,
    }
    base.update(overrides)
    return base


def test_tc_ev1051_002_shared_preset_readable_by_other_user() -> None:
    """TC-EV1051-002: shared=true preset is readable by a non-owner."""
    reader = svc.ConversionProfilesService(str(READER))
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=_preset_row(shared=True, user_id=OWNER))
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        got = reader.get_preset(PRESET_ID)
    assert got.id == PRESET_ID
    assert got.shared is True
    assert got.user_id == OWNER


def test_tc_ev1051_002_private_preset_forbidden_for_other_user() -> None:
    """TC-EV1051-002: foreign private preset stays 403."""
    reader = svc.ConversionProfilesService(str(READER))
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=_preset_row(shared=False, user_id=OWNER))
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as forbidden,
    ):
        reader.get_preset(PRESET_ID)
    assert forbidden.value.status_code == 403


def test_tc_ev1051_004_template_rejects_password_and_uri() -> None:
    """TC-EV1051-004: secret-bearing / URI params fail closed."""
    owner = svc.ConversionProfilesService(str(OWNER))
    with pytest.raises(HTTPException) as password_exc:
        owner.create_template(
            DisseminationTemplateCreate(
                slug="bad-secret",
                name="Bad",
                sink_type="postgres",
                params={"password": "secret"},
            )
        )
    assert password_exc.value.status_code == 422

    with pytest.raises(HTTPException) as uri_exc:
        owner.create_template(
            DisseminationTemplateCreate(
                slug="bad-uri",
                name="Bad URI",
                sink_type="wis2",
                params={"endpoint": "mqtt://example.com"},
            )
        )
    assert uri_exc.value.status_code == 422


def test_tc_ev1051_004_template_accepts_non_secret_metadata() -> None:
    """TC-EV1051-004: non-secret metadata saves."""
    owner = svc.ConversionProfilesService(str(OWNER))
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.return_value = _Result()
    created = _template_row(params={"table": "reports", "schema": "public"})
    read_conn.execute.return_value = _Result(row=created)
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        out = owner.create_template(
            DisseminationTemplateCreate(
                slug="ops-sqlite",
                name="Ops SQLite",
                sink_type="sqlite",
                product="metar",
                params={"table": "reports", "schema": "public"},
                shared=True,
            )
        )
    assert out.sink_type == "sqlite"
    assert out.params == {"table": "reports", "schema": "public"}
    assert out.shared is True


def test_tc_ev1051_005_shared_template_readable_by_other_user() -> None:
    """TC-EV1051-005: shared template is readable by a non-owner (drawer load path)."""
    reader = svc.ConversionProfilesService(str(READER))
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value = _Result(row=_template_row(shared=True, user_id=OWNER))
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        got = reader.get_template(TEMPLATE_ID)
    assert got.id == TEMPLATE_ID
    assert got.shared is True
    assert "password" not in (got.params or {})
