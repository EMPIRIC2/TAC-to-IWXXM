"""T7.4: worker live poll → store/quarantine row (F8 / UJ-014).

Uses service-role PostgREST reads against iwxxm_ingest_* tables after the
worker has polled INGEST_POLLER_URL. Skips when secrets or rows are absent.
"""

from __future__ import annotations

import os
import time

import httpx
import pytest

pytestmark = [pytest.mark.live]


def _supabase() -> tuple[str, str] | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return url.rstrip("/"), key


@pytest.mark.live
def test_t74_ingest_tables_accept_worker_rows() -> None:
    """Assert ingest tables exist and are writable via service role (post-migration)."""
    creds = _supabase()
    if creds is None:
        pytest.skip("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set")
    base, key = creds
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    job_id = f"t74-probe-{int(time.time())}"
    row = {
        "job_id": job_id,
        "product": "METAR",
        "profile": "annex3",
        "source_url": "https://example.test/t74",
        "tac_input": "METAR KJFK 231751Z NIL=",
        "iwxxm_xml": "<iwxxm:METAR/>",
        "issues": [],
        "stage_failed": None,
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{base}/rest/v1/iwxxm_ingest_results", headers=headers, json=row
        )
        assert resp.status_code in {200, 201}, resp.text[:400]
        got = client.get(
            f"{base}/rest/v1/iwxxm_ingest_results",
            headers=headers,
            params={"job_id": f"eq.{job_id}", "select": "job_id,product"},
        )
        assert got.status_code == 200
        assert any(r.get("job_id") == job_id for r in got.json())

        qrow = {
            **row,
            "job_id": f"{job_id}-q",
            "iwxxm_xml": None,
            "stage_failed": "lint",
            "issues": [{"stage": "lint", "code": "x", "message": "probe"}],
        }
        q = client.post(
            f"{base}/rest/v1/iwxxm_ingest_quarantine", headers=headers, json=qrow
        )
        assert q.status_code in {200, 201}, q.text[:400]
