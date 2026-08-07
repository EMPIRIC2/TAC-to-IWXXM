"""TC-F33-004 — mass ingest requires JWT (EV-042 / #897).

[Corpus: product §F33] [Corpus: api] [Corpus: tests]
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.abuse_controls import get_limiter
from src.utilities.security import verify_supabase_token


@pytest.fixture
def mass_client() -> TestClient:
    """TestClient with rate-limiter reset; no auth override by default."""
    get_limiter().reset()
    with TestClient(api_module.app) as client:
        yield client
    api_module.app.dependency_overrides.clear()
    get_limiter().reset()


def test_tc_f33_004_mass_ingest_rejects_unauthenticated(mass_client: TestClient) -> None:
    """Unauthenticated POST /api/v1/ingest/mass → 401 or 403 (HTTPBearer)."""
    resp = mass_client.post(
        "/api/v1/ingest/mass",
        files=[("files", ("sample.tac", b"METAR KJFK 121251Z=\n", "text/plain"))],
    )
    assert resp.status_code in {401, 403}, resp.text


def test_tc_f33_001_mass_ingest_accepts_authenticated_tac(
    mass_client: TestClient,
) -> None:
    """Authenticated small TAC upload returns accepted per-file result."""

    async def override_verify_token() -> dict[str, Any]:
        return {"sub": "user-f33-test"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    resp = mass_client.post(
        "/api/v1/ingest/mass",
        files=[("files", ("sample.tac", b"METAR KJFK 121251Z=\n", "text/plain"))],
        headers={"Authorization": "Bearer test-token"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["accepted_count"] == 1
    assert body["rejected_count"] == 0
    assert body["results"][0]["accepted"] is True
    assert body["results"][0]["content"] is not None
    assert "METAR" in body["results"][0]["content"]
