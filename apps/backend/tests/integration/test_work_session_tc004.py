"""TC-004 / F21 — server work-sessions API removed (IndexedDB is the operator store).

Historical TC-004 covered authenticated CRUD against ``tac_work_sessions``.
EV-017 / ADR-031 moves history to browser IndexedDB; the HTTP surface returns 404.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api import app

pytestmark = [pytest.mark.integration]


def test_tc004_work_sessions_api_gone() -> None:
    """Production app must not expose /api/v1/work-sessions (F7.h / F21)."""
    client = TestClient(app)
    headers = {"Authorization": "Bearer unused"}

    listed = client.get("/api/v1/work-sessions", headers=headers)
    assert listed.status_code == 404

    created = client.post(
        "/api/v1/work-sessions",
        headers=headers,
        json={"product": "metar", "manual_tac": "METAR KJFK"},
    )
    assert created.status_code == 404
