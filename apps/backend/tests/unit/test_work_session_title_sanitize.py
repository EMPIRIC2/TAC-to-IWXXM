"""Unit tests for work-session title sanitization (F-ADV-02)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from src.schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionProduct,
    WorkSessionStatus,
    sanitize_work_session_title,
)


def test_sanitize_work_session_title_passthrough_none_and_non_str() -> None:
    assert sanitize_work_session_title(None) is None
    assert sanitize_work_session_title(42) == 42


def test_sanitize_work_session_title_strips_markup() -> None:
    assert sanitize_work_session_title("<b>KJFK</b> 12Z") == "KJFK 12Z"
    assert "<script>" not in str(sanitize_work_session_title("<script>x</script>ok"))


def test_work_session_create_strips_html_title() -> None:
    payload = WorkSessionCreate(product="metar", title="<em>draft</em>")
    assert payload.title == "draft"


def test_work_session_response_strips_stored_html_title() -> None:
    now = datetime(2026, 9, 9, tzinfo=UTC)
    session = WorkSession(
        id=uuid4(),
        user_id=uuid4(),
        product=WorkSessionProduct.METAR,
        status=WorkSessionStatus.DRAFT,
        title="<script>alert(1)</script>legacy",
        created_at=now,
        updated_at=now,
    )
    assert "<script>" not in session.title.lower()
    assert "legacy" in session.title
