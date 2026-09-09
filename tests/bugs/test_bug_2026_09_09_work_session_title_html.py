"""BUG-2026-09-09 — work-session titles must strip HTML on write."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.schemas.work_session import WorkSessionCreate, WorkSessionUpdate  # noqa: E402


def test_bug_2026_09_09_create_strips_script_tags_from_title() -> None:
    """F-ADV-02: raw script markup must not be persisted as-is."""
    payload = WorkSessionCreate(
        product="metar",
        title="<script>alert(1)</script>KJFK morning",
    )
    assert payload.title is not None
    assert "<script>" not in payload.title.lower()
    assert "alert(1)" in payload.title
    assert "KJFK morning" in payload.title


def test_bug_2026_09_09_update_strips_html_from_title() -> None:
    payload = WorkSessionUpdate(title='<img src=x onerror="alert(1)">TAF draft')
    assert payload.title is not None
    assert "<img" not in payload.title.lower()
    assert "TAF draft" in payload.title


def test_bug_2026_09_09_plain_title_unchanged() -> None:
    payload = WorkSessionCreate(product="taf", title="  KJFK 12Z  ")
    assert payload.title == "KJFK 12Z"
