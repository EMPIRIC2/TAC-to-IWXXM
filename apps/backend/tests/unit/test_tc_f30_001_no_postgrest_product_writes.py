"""T2.6 / TC-F30-001 — API product path must not write via Supabase PostgREST."""

from __future__ import annotations

from pathlib import Path

import pytest

_BACKEND_SRC = Path(__file__).resolve().parents[2] / "src"

# Product data plane modules restored under F30/F31.
_PRODUCT_MODULES = (
    _BACKEND_SRC / "services" / "work_session_service.py",
    _BACKEND_SRC / "routers" / "work_sessions.py",
)


@pytest.mark.unit
def test_work_session_stack_has_no_supabase_postgrest_client() -> None:
    """Logged-in sessions use DATABASE_URL / SQLAlchemy — not supabase-py PostgREST."""
    for path in _PRODUCT_MODULES:
        assert path.is_file(), f"missing {path}"
        text = path.read_text(encoding="utf-8")
        assert "create_client" not in text
        assert "from supabase" not in text
        assert "postgrest" not in text.lower()
        assert "DATABASE_URL" in text or "WorkSessionService" in text


@pytest.mark.unit
def test_work_session_service_uses_sqlalchemy() -> None:
    text = (_BACKEND_SRC / "services" / "work_session_service.py").read_text(encoding="utf-8")
    assert "sqlalchemy" in text
    assert "tac_work_sessions" in text
