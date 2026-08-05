"""T7.4: worker live store/quarantine row (F8 / UJ-014 / TC-F30-003).

Writes via DATABASE_URL (SQLAlchemy PostgresStore). Skips when DATABASE_URL unset.
"""

from __future__ import annotations

import os
import time

import pytest
from metar_worker.pipeline import PipelineResult
from metar_worker.poller import IngestJob
from metar_worker.store import (
    QUARANTINE_TABLE,
    RESULTS_TABLE,
    PostgresStore,
    write_result,
)

pytestmark = [pytest.mark.live]


@pytest.mark.live
def test_t74_ingest_tables_accept_worker_rows() -> None:
    """Assert ingest tables are writable via DATABASE_URL (post-Alembic)."""
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        pytest.skip("DATABASE_URL not set")

    store = PostgresStore(database_url=database_url)
    job_id = f"t74-probe-{int(time.time())}"
    job = IngestJob(
        job_id=job_id,
        product="METAR",
        tac="METAR KJFK 231751Z NIL=",
        source_url="https://example.test/t74",
    )
    ok = PipelineResult(
        job_id=job_id,
        ok=True,
        product="METAR",
        profile="annex3",
        xml="<iwxxm:METAR/>",
        issues=[],
    )
    assert write_result(store, job, ok) == RESULTS_TABLE
    rows = store.fetch_by_job_id(RESULTS_TABLE, job_id)
    assert any(r.get("job_id") == job_id for r in rows)

    q_job = IngestJob(
        job_id=f"{job_id}-q",
        product="METAR",
        tac="METAR KJFK 231751Z NIL=",
        source_url="https://example.test/t74",
    )
    fail = PipelineResult(
        job_id=f"{job_id}-q",
        ok=False,
        product="METAR",
        profile="annex3",
        xml=None,
        issues=[{"stage": "lint", "code": "x", "message": "probe"}],
        stage_failed="lint",
    )
    assert write_result(store, q_job, fail) == QUARANTINE_TABLE
    qrows = store.fetch_by_job_id(QUARANTINE_TABLE, f"{job_id}-q")
    assert any(r.get("stage_failed") == "lint" for r in qrows)
