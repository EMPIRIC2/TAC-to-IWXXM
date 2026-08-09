"""T6.3: pipeline lint → convert → iwxxm-validate."""

from __future__ import annotations

import pytest
from metar_worker.pipeline import process_job
from metar_worker.poller import IngestJob

pytestmark = pytest.mark.unit


def test_t63_pipeline_metar_pass() -> None:
    job = IngestJob(
        job_id="p1",
        product="METAR",
        tac="METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        source_url="https://example.test/feed",
    )
    result = process_job(job, profile="annex3")
    assert result.ok is True
    assert result.xml
    assert result.stage_failed is None
    assert "METAR" in result.xml


def test_t63_pipeline_lint_fail_quarantines() -> None:
    job = IngestJob(
        job_id="p2",
        product="METAR",
        tac="NOT A METAR",
        source_url="https://example.test/feed",
    )
    result = process_job(job)
    assert result.ok is False
    assert result.stage_failed in {"lint", "convert"}
    assert result.issues
