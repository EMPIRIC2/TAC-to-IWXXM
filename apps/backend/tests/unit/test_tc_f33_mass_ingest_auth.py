"""TC-F33-004 - mass ingest requires JWT (EV-042 / #897).

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


def test_tc_f33_001_mass_ingest_accepts_authenticated_zip(
    mass_client: TestClient,
) -> None:
    """Authenticated zip upload expands members into results."""
    import io
    import zipfile

    async def override_verify_token() -> dict[str, Any]:
        return {"sub": "user-f33-zip"}

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("a.tac", "METAR KJFK 121251Z=\n")
    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    resp = mass_client.post(
        "/api/v1/ingest/mass",
        files=[("files", ("batch.zip", buf.getvalue(), "application/zip"))],
        headers={"Authorization": "Bearer test-token"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["accepted_count"] == 1
    assert body["results"][0]["accepted"] is True


def test_tc_f33_002_mass_ingest_rejects_too_many_files(
    mass_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """413 when expanded file count exceeds MASS_INGEST_MAX_FILES."""

    async def override_verify_token() -> dict[str, Any]:
        return {"sub": "user-f33-cap"}

    monkeypatch.setenv("MASS_INGEST_MAX_FILES", "1")
    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    resp = mass_client.post(
        "/api/v1/ingest/mass",
        files=[
            ("files", ("a.tac", b"METAR A=\n", "text/plain")),
            ("files", ("b.tac", b"METAR B=\n", "text/plain")),
        ],
        headers={"Authorization": "Bearer test-token"},
    )
    assert resp.status_code == 413, resp.text


def test_tc_f33_002_mass_ingest_rejects_total_bytes_cap(
    mass_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """413 when accepted content exceeds caps.max_total_bytes (handler path)."""
    from src.routers import mass_ingest as mass_router
    from src.services.mass_ingest import MassIngestCaps

    async def override_verify_token() -> dict[str, Any]:
        return {"sub": "user-f33-total"}

    # Keep middleware body limit high; force handler caps low so line 108 runs.
    monkeypatch.setattr(
        mass_router,
        "_caps",
        lambda: MassIngestCaps(max_files=200, max_file_bytes=5_000_000, max_total_bytes=20),
    )
    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    resp = mass_client.post(
        "/api/v1/ingest/mass",
        files=[
            ("files", ("a.tac", b"METAR AAAAAAAAA=\n", "text/plain")),
            ("files", ("b.tac", b"METAR BBBBBBBBB=\n", "text/plain")),
        ],
        headers={"Authorization": "Bearer test-token"},
    )
    assert resp.status_code == 413, resp.text
    assert "bytes" in resp.text.lower()


@pytest.mark.asyncio
async def test_tc_f33_002_mass_ingest_rejects_empty_file_list() -> None:
    """Empty upload list → 400 (covers handler guard)."""
    from fastapi import HTTPException
    from src.routers import mass_ingest as mass_router
    from starlette.requests import Request

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/ingest/mass",
        "raw_path": b"/api/v1/ingest/mass",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = Request(scope)

    with pytest.raises(HTTPException) as exc:
        await mass_router.mass_ingest(
            request=request,
            files=[],
            _user={"sub": "user-f33-empty"},
        )
    assert exc.value.status_code == 400
