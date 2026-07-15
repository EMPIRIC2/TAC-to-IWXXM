"""BUG-2026-07-15 — multi-line soft-preview failed_spans vs editor buffer.

When ``preview=true`` converts a multi-line ``manual_text``, each line is
converted separately. ``failed_spans`` must use offsets relative to the full
buffer so the workbench Failed-TAC cue highlights the failing line, not an
earlier one.
"""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.api import app  # noqa: E402
from src.utilities.security import verify_supabase_token  # noqa: E402

LINE_GOOD = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
LINE_BAD = "METAR XXXX NOT_A_REAL_REPORT GARBAGE="


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token():
        return {"sub": str(uuid4()), "aud": "test-project"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_multiline_soft_preview_failed_spans_align_to_full_buffer(
    client: TestClient,
) -> None:
    """Span slices of the full buffer must contain the bad second-line TAC."""
    buf = f"{LINE_GOOD}\n{LINE_BAD}"
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, buf),
            "preview": (None, "true"),
            "iwxxm_version": (None, "2023-1"),
            "product": (None, "METAR"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    spans = payload.get("failed_spans") or []
    assert spans, "expected at least one failed_span for the bad line"

    bad_line_start = buf.index(LINE_BAD)
    overlapping = []
    for span in spans:
        start = span["start"]
        end = span["end"]
        assert 0 <= start <= end <= len(buf)
        slice_text = buf[start:end]
        # Must not exclusively highlight the good first line.
        assert not (end <= bad_line_start and LINE_GOOD.startswith(slice_text[:20]))
        if start >= bad_line_start or (start < bad_line_start and end > bad_line_start):
            overlapping.append(slice_text)

    assert overlapping, (
        f"failed_spans did not overlap the bad second line; spans={spans!r} "
        f"bad_line_start={bad_line_start}"
    )
    # At least one span slice should be taken from the second line region.
    assert any(LINE_BAD[:8] in text or text in LINE_BAD for text in overlapping)
