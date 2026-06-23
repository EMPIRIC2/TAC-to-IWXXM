"""Unit tests for evaluation_store SQL helpers."""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.schemas.evaluation import ComparisonDetail, ComparisonStatus, EvaluationResultDetail, JobSummaryStats
from src.services import evaluation_store


class _FakeResult:
    def __init__(self, row=None, rows=None):
        self._row = row
        self._rows = rows or []

    def fetchone(self):
        return self._row

    def mappings(self):
        return self

    def first(self):
        return self._rows[0] if self._rows else None

    def scalar_one(self):
        return self._rows[0] if self._rows else 0

    def __iter__(self):
        return iter(self._rows)


@pytest.mark.asyncio
async def test_create_job_in_db_raises_when_insert_returns_no_row(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock(return_value=_FakeResult(row=None))
    session.commit = AsyncMock()

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    with pytest.raises(RuntimeError, match="Failed to create evaluation job"):
        await evaluation_store.create_job_in_db("user-1", "random", 10)


@pytest.mark.asyncio
async def test_create_job_in_db_returns_id(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock(return_value=_FakeResult(row=("job-abc",)))
    session.commit = AsyncMock()

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    job_id = await evaluation_store.create_job_in_db("user-1", "random", 10)
    assert job_id == "job-abc"


@pytest.mark.asyncio
async def test_update_job_status_accepts_summary_dict(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    await evaluation_store.update_job_status(
        "job-1",
        "completed",
        summary_stats={"total": 2, "passed": 1, "failed": 1, "errors": 0, "pass_rate": 0.5},
    )
    assert session.execute.await_count == 1


@pytest.mark.asyncio
async def test_update_job_status_completed_includes_summary(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    summary = JobSummaryStats(total=1, passed=1, failed=0, errors=0, pass_rate=1.0)
    await evaluation_store.update_job_status("job-1", "completed", progress=1, summary_stats=summary)
    assert session.execute.await_count == 1
    assert session.commit.await_count == 1


@pytest.mark.asyncio
async def test_save_result_to_db_executes_insert(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    result = EvaluationResultDetail(
        station_id="KJFK",
        timestamp=MagicMock(),
        tac_input="METAR",
        our_iwxxm="<a/>",
        their_iwxxm="<b/>",
        comparison_status=ComparisonStatus.PASS,
        comparison=None,
        errors=[],
    )
    await evaluation_store.save_result_to_db("job-1", result)
    assert session.execute.await_count == 1


@pytest.mark.asyncio
async def test_save_result_to_db_with_comparison_detail(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    result = EvaluationResultDetail(
        station_id="KJFK",
        timestamp=MagicMock(),
        tac_input="METAR",
        our_iwxxm="<a/>",
        their_iwxxm="<b/>",
        comparison_status=ComparisonStatus.PASS,
        comparison=ComparisonDetail(
            passed=True,
            our_elements=1,
            their_elements=1,
            missing_elements=[],
            extra_elements=[],
            value_mismatches=[],
            error_message=None,
        ),
        errors=[],
    )
    await evaluation_store.save_result_to_db("job-1", result)
    assert session.execute.await_count == 1


@pytest.mark.asyncio
async def test_update_job_status_progress_only(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    await evaluation_store.update_job_status("job-1", "running", progress=3)
    assert session.execute.await_count == 1


@pytest.mark.asyncio
async def test_get_job_for_user_returns_none_when_missing(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock(
        return_value=MagicMock(mappings=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    assert await evaluation_store.get_job_for_user("job-x", "user-1") is None


@pytest.mark.asyncio
async def test_get_job_for_user_returns_row(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock(
        return_value=MagicMock(
            mappings=MagicMock(
                return_value=MagicMock(first=MagicMock(return_value={"id": "job-1", "status": "pending"}))
            )
        )
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    row = await evaluation_store.get_job_for_user("job-1", "user-1")
    assert row is not None
    assert row["id"] == "job-1"


@pytest.mark.asyncio
async def test_list_results_for_job_without_filter(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[
            MagicMock(mappings=MagicMock(return_value=iter([{"station_id": "KORD"}]))),
            MagicMock(scalar_one=MagicMock(return_value=1)),
        ]
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    rows, total = await evaluation_store.list_results_for_job("job-1", limit=10, offset=0)
    assert total == 1
    assert rows[0]["station_id"] == "KORD"


@pytest.mark.asyncio
async def test_list_results_for_job_with_filter(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[
            MagicMock(mappings=MagicMock(return_value=iter([{"station_id": "KJFK", "comparison_status": "pass"}]))),
            MagicMock(scalar_one=MagicMock(return_value=1)),
        ]
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    rows, total = await evaluation_store.list_results_for_job("job-1", limit=10, offset=0, status_filter="pass")
    assert total == 1
    assert rows[0]["station_id"] == "KJFK"


@pytest.mark.asyncio
async def test_update_job_status_error_message_only(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    await evaluation_store.update_job_status("job-1", "failed", error_message="boom")
    assert session.execute.await_count == 1


@pytest.mark.asyncio
async def test_list_jobs_for_user_returns_total(monkeypatch):
    session = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[
            MagicMock(mappings=MagicMock(return_value=iter([{"id": "job-1", "status": "pending"}]))),
            MagicMock(scalar_one=MagicMock(return_value=1)),
        ]
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield session

    monkeypatch.setattr(evaluation_store, "get_db_session", fake_get_db_session)

    rows, total = await evaluation_store.list_jobs_for_user("user-1", 10, 0)
    assert total == 1
    assert rows[0]["id"] == "job-1"
