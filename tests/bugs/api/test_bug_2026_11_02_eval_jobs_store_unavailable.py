"""BUG-2026-11-02 — GET/POST /api/v1/eval/jobs must not 500 when store is down.

Staging adversarial probe: ``evaluation_jobs`` relation missing → uncaught
SQLAlchemy ``UndefinedTableError`` → HTTP 500. Also historically passed
literal ``anonymous`` into ``CAST(... AS uuid)``. Fail closed with 503.

[Corpus: api] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from fastapi import BackgroundTasks, HTTPException
from src.routers import evaluation as eval_router
from src.schemas.evaluation import EvaluationMode, EvaluationRequest


@pytest.mark.asyncio
async def test_bug_2026_11_02_list_eval_jobs_missing_table_returns_503(
    monkeypatch,
) -> None:
    async def boom(user_id, limit, offset):
        raise RuntimeError('relation "evaluation_jobs" does not exist')

    monkeypatch.setattr(eval_router, "list_jobs_for_user", boom)
    with pytest.raises(HTTPException) as exc:
        await eval_router.list_user_jobs(page=1, per_page=20)
    assert exc.value.status_code == 503
    assert exc.value.detail == "Evaluation store unavailable"


@pytest.mark.asyncio
async def test_bug_2026_11_02_create_eval_job_missing_table_returns_503(
    monkeypatch,
) -> None:
    async def boom(**_kwargs):
        raise RuntimeError('relation "evaluation_jobs" does not exist')

    monkeypatch.setattr(eval_router, "create_job_in_db", boom)
    request = EvaluationRequest(mode=EvaluationMode.SINGLE, station_ids=["KJFK"])
    with pytest.raises(HTTPException) as exc:
        await eval_router.create_evaluation_job(request, BackgroundTasks())
    assert exc.value.status_code == 503
    assert exc.value.detail == "Evaluation store unavailable"


def test_bug_2026_11_02_anonymous_eval_user_id_is_uuid() -> None:
    uid = eval_router._eval_user_id()
    assert uid == "00000000-0000-0000-0000-000000000000"
