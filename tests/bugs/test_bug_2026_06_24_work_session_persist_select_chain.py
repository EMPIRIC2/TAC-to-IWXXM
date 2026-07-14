"""BUG-2026-06-24 — F5 work-session persist 502 on production.

User report: after admin login, console shows
``[useWorkSessionSync] persist failed: Error: Work session database error``.

Production repro: POST /api/v1/work-sessions → 502 while GET list → 200.
Root cause: supabase-py 2.28 insert/update builders have no ``.select()``;
``insert(data).select('*').execute()`` raises AttributeError, mapped to 502.
"""

from __future__ import annotations

import pathlib
import re
import sys
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi import HTTPException

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"
SERVICE_FILE = BACKEND_ROOT / "src" / "services" / "work_session_service.py"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.schemas.work_session import WorkSessionCreate, WorkSessionUpdate  # noqa: E402
from src.services import work_session_service as svc_mod  # noqa: E402
from src.services.work_session_service import WorkSessionService  # noqa: E402

SESSION_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = "27f7a37c-5575-4e19-a6d6-338755caec1d"
NOW = datetime(2026, 6, 25, 2, 0, tzinfo=UTC)

ROW = {
    "id": str(SESSION_ID),
    "user_id": USER_ID,
    "product": "METAR",
    "status": "draft",
    "title": "METAR 2026-06-25 02:00 UTC",
    "manual_tac": "METAR TEST",
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


class _LegacyInsertBuilder:
    """Mimics supabase-py 2.28 SyncQueryRequestBuilder — no ``select`` method."""

    def __init__(self, response: SimpleNamespace) -> None:
        self._response = response

    def execute(self) -> SimpleNamespace:
        return self._response


class _LegacyUpdateBuilder:
    """Mimics supabase-py 2.28 update chain ending at filter builder — no ``select``."""

    def __init__(self, response: SimpleNamespace) -> None:
        self._response = response

    def eq(self, *_args, **_kwargs) -> _LegacyUpdateBuilder:
        return self

    def is_(self, *_args, **_kwargs) -> _LegacyUpdateBuilder:
        return self

    @property
    def not_(self) -> _LegacyUpdateBuilder:
        return self

    def execute(self) -> SimpleNamespace:
        return self._response


class _LegacyTable:
    def __init__(self) -> None:
        self.last_insert: dict | None = None
        self.last_update: dict | None = None

    def insert(self, data: dict) -> _LegacyInsertBuilder:
        self.last_insert = data
        return _LegacyInsertBuilder(SimpleNamespace(data=ROW))

    def update(self, data: dict) -> _LegacyUpdateBuilder:
        self.last_update = data
        return _LegacyUpdateBuilder(SimpleNamespace(data=ROW))

    def select(self, *_args, **_kwargs) -> None:
        raise AssertionError("list/get paths not used in this repro")


@pytest.fixture
def legacy_client(monkeypatch: pytest.MonkeyPatch) -> _LegacyTable:
    table = _LegacyTable()
    monkeypatch.setattr(
        svc_mod, "get_supabase_url", lambda: "https://example.supabase.co"
    )
    monkeypatch.setattr(
        svc_mod, "get_supabase_publishable_key", lambda: "publishable-key"
    )
    # Single create_client override wiring table and postgrest.auth in one place,
    # mirroring supabase.create_client().table().
    full_client = SimpleNamespace(
        postgrest=SimpleNamespace(auth=lambda _t: None),
        table=lambda _name: table,
    )
    monkeypatch.setattr(svc_mod, "create_client", lambda *_a, **_k: full_client)
    return table


def test_work_session_mutations_must_not_chain_select_on_insert(
    legacy_client: _LegacyTable,
) -> None:
    """Create/update must work when insert/update builders lack ``select`` (supabase-py 2.28)."""
    service = WorkSessionService("token")
    service._client = SimpleNamespace(table=lambda _name: legacy_client)  # type: ignore[attr-defined]

    created = service.create_session(
        USER_ID, WorkSessionCreate(manual_tac="METAR TEST", product="METAR")
    )
    assert created.id == SESSION_ID
    assert legacy_client.last_insert is not None
    assert legacy_client.last_insert["user_id"] == USER_ID

    updated = service.update_session(
        SESSION_ID, WorkSessionUpdate(manual_tac="METAR UPDATED")
    )
    assert updated.id == SESSION_ID
    assert legacy_client.last_update is not None

    # soft_delete must also work with legacy builders that lack ``select()``.
    prev_update = legacy_client.last_update
    deleted = service.soft_delete(SESSION_ID)
    assert deleted.id == SESSION_ID
    assert legacy_client.last_update is not None
    assert legacy_client.last_update is not prev_update

    # restore_session must likewise work with legacy builders that lack ``select()``.
    prev_soft_delete_update = legacy_client.last_update
    restored = service.restore_session(SESSION_ID)
    assert restored.id == SESSION_ID
    assert legacy_client.last_update is not None
    assert legacy_client.last_update is not prev_soft_delete_update


def test_work_session_service_source_avoids_select_after_mutation() -> None:
    """Guard against reintroducing ``.<mutation>(...).select(...)`` incompatible with prod supabase-py.

    Covers insert/update/delete/upsert so ``.select()`` cannot be reintroduced on
    ``create_session``, ``update_session``, ``soft_delete``, or ``restore_session``.
    Read-only ``select`` (list/get paths) remains allowed.
    """
    source = SERVICE_FILE.read_text(encoding="utf-8")
    mutation_select = re.compile(r"\.(insert|update|delete|upsert)\([^)]*\)\.select\(")
    assert mutation_select.search(source) is None


def test_create_session_maps_attribute_error_to_502_without_fix() -> None:
    """Document failure mode: AttributeError on missing select becomes opaque 502."""
    with pytest.raises(HTTPException) as exc:
        svc_mod._handle_db_error(
            AttributeError(
                "'SyncQueryRequestBuilder' object has no attribute 'select'"
            ),
        )
    assert exc.value.status_code == 502
    assert exc.value.detail == "Work session database error"
