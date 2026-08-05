"""BUG-2026-06-24 — F5 work-session persist 502 on production.

User report: after admin login, console shows
``[useWorkSessionSync] persist failed: Error: Work session database error``.

Production repro: POST /api/v1/work-sessions → 502 while GET list → 200.
Root cause: supabase-py 2.28 insert/update builders have no ``.select()``;
``insert(data).select('*').execute()`` raises AttributeError, mapped to 502.

S038 / EV-031 / F30: ``work_session_service`` persists via SQLAlchemy /
``DATABASE_URL`` (DO Postgres), not supabase-py. The legacy client fixture
test is skipped; source + ``_handle_db_error`` guards remain.
"""

from __future__ import annotations

import pathlib
import re
import sys
from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi import HTTPException

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"
SERVICE_FILE = BACKEND_ROOT / "src" / "services" / "work_session_service.py"

if not SERVICE_FILE.is_file():
    pytest.skip(
        "work_session_service.py missing — BUG-2026-06-24 N/A",
        allow_module_level=True,
    )

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.services import work_session_service as svc_mod  # noqa: E402

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


@pytest.mark.skip(
    reason="F30/EV-031: WorkSessionService uses SQLAlchemy, not supabase-py client"
)
def test_work_session_mutations_must_not_chain_select_on_insert() -> None:
    """Historical supabase-py 2.28 ``.select()`` chain repro — superseded by SQLAlchemy."""
    _ = (ROW, USER_ID, SESSION_ID, NOW)


def test_work_session_service_source_avoids_select_after_mutation() -> None:
    """Guard against reintroducing ``.<mutation>(...).select(...)`` (supabase-py hazard).

    Covers insert/update/delete/upsert so ``.select()`` cannot be reintroduced on
    mutation paths. Read-only ``select`` (SQLAlchemy ``select(...)``) remains allowed.
    """
    source = SERVICE_FILE.read_text(encoding="utf-8")
    mutation_select = re.compile(r"\.(insert|update|delete|upsert)\([^)]*\)\.select\(")
    assert mutation_select.search(source) is None
    assert "create_client" not in source
    assert "get_supabase_url" not in source


def test_create_session_maps_attribute_error_to_502_without_leak() -> None:
    """Document failure mode: AttributeError maps to opaque 502."""
    with pytest.raises(HTTPException) as exc:
        svc_mod._handle_db_error(
            AttributeError(
                "'SyncQueryRequestBuilder' object has no attribute 'select'"
            ),
        )
    assert exc.value.status_code == 502
    assert exc.value.detail == "Work session database error"
