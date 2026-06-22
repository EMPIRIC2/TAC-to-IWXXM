"""Unit tests for statistics service branch coverage."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from src.schemas.icao_opmet import TranslationStatus
from src.services import statistics as stats


class _Result:
    def __init__(self, first_row=None, all_rows=None):
        self._first = first_row
        self._all = all_rows or []

    def first(self):
        return self._first

    def all(self):
        return self._all


class _FakeSession:
    def __init__(self, results=None, commit_error: Exception | None = None):
        self._results = results or []
        self._idx = 0
        self.commit_error = commit_error
        self.added = []

    def add(self, record):
        self.added.append(record)

    async def commit(self):
        if self.commit_error:
            raise self.commit_error

    async def execute(self, _query):
        result = self._results[self._idx]
        self._idx += 1
        return result


class _Expr:
    def cast(self, _type):
        return self

    def label(self, _name):
        return self

    def within_group(self, _arg):
        return self

    def desc(self):
        return self


class _Column(_Expr):
    def __ge__(self, _other):
        return _Expr()

    def __lt__(self, _other):
        return _Expr()

    def __eq__(self, _other):
        return _Expr()

    def __ne__(self, _other):
        return _Expr()


class _Func:
    def count(self, _arg):
        return _Expr()

    def sum(self, _arg):
        return _Expr()

    def avg(self, _arg):
        return _Expr()

    def percentile_cont(self, _arg):
        return _Expr()


class _Query:
    def where(self, _arg):
        return self

    def group_by(self, *_args):
        return self

    def order_by(self, *_args):
        return self

    def limit(self, _arg):
        return self


def test_normalize_icao_code_valid_and_invalid_inputs():
    assert stats._normalize_icao_code("kjfk") == "KJFK"
    assert stats._normalize_icao_code("ZZ9Z") == "ZZ9Z"
    assert stats._normalize_icao_code("A") == "ZZZZ"
    assert stats._normalize_icao_code(None) == "ZZZZ"


@pytest.mark.asyncio
async def test_log_translation_returns_none_when_disabled(monkeypatch):
    monkeypatch.setattr(stats, "should_log_statistics", lambda: False)

    result = await stats.StatisticsService.log_translation(
        tac_message="METAR KJFK 010000Z",
        iwxxm_version="2025-2",
        icao_airport_code="KJFK",
        translation_status=TranslationStatus.SUCCESS,
        translation_duration_ms=100,
    )

    assert result is None


@pytest.mark.asyncio
async def test_log_translation_successful_insert_and_metric(monkeypatch):
    fake_session = _FakeSession()
    metric_calls = []

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "should_log_statistics", lambda: True)
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)
    monkeypatch.setattr(stats, "get_icao_region", lambda _icao: "NAM")
    monkeypatch.setattr(stats, "record_translation_metric", lambda **kwargs: metric_calls.append(kwargs))

    translation_id = await stats.StatisticsService.log_translation(
        tac_message="METAR KJFK 010000Z",
        iwxxm_version="2025-2",
        icao_airport_code="KJFK",
        translation_status=TranslationStatus.SUCCESS,
        translation_duration_ms=120,
    )

    assert translation_id is not None
    assert len(fake_session.added) == 1
    assert metric_calls and metric_calls[0]["status"] == "success"


@pytest.mark.asyncio
async def test_log_translation_record_creation_failure_returns_none(monkeypatch):
    def _raise_on_init(**_kwargs):
        raise RuntimeError("record creation failed")

    monkeypatch.setattr(stats, "should_log_statistics", lambda: True)
    monkeypatch.setattr(stats, "TranslationStatisticsModel", _raise_on_init)
    monkeypatch.setattr(stats, "get_icao_region", lambda _icao: "NAM")

    result = await stats.StatisticsService.log_translation(
        tac_message="METAR KJFK 010000Z",
        iwxxm_version="2025-2",
        icao_airport_code="KJFK",
        translation_status=TranslationStatus.SUCCESS,
        translation_duration_ms=120,
    )

    assert result is None


@pytest.mark.asyncio
async def test_log_translation_commit_failure_returns_none(monkeypatch):
    fake_session = _FakeSession(commit_error=RuntimeError("commit failed"))

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "should_log_statistics", lambda: True)
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)
    monkeypatch.setattr(stats, "get_icao_region", lambda _icao: "NAM")

    result = await stats.StatisticsService.log_translation(
        tac_message="METAR KJFK 010000Z",
        iwxxm_version="2025-2",
        icao_airport_code="KJFK",
        translation_status=TranslationStatus.SUCCESS,
        translation_duration_ms=120,
    )

    assert result is None


@pytest.mark.asyncio
async def test_log_translation_invalid_icao_uses_fallback(monkeypatch):
    fake_session = _FakeSession()

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "should_log_statistics", lambda: True)
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)
    monkeypatch.setattr(stats, "get_icao_region", lambda _icao: "NAM")

    await stats.StatisticsService.log_translation(
        tac_message="METAR XXXX 010000Z",
        iwxxm_version="2025-2",
        icao_airport_code="bad",
        translation_status=TranslationStatus.FAILED,
        translation_duration_ms=0,
    )

    assert fake_session.added[0].icao_airport_code == "ZZZZ"


@pytest.mark.asyncio
async def test_log_translation_region_value_error_defaults_to_nam(monkeypatch):
    fake_session = _FakeSession()
    metric_calls = []

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    def _raise_value_error(_icao):
        raise ValueError("invalid code")

    monkeypatch.setattr(stats, "should_log_statistics", lambda: True)
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)
    monkeypatch.setattr(stats, "get_icao_region", _raise_value_error)
    monkeypatch.setattr(stats, "record_translation_metric", lambda **kwargs: metric_calls.append(kwargs))

    translation_id = await stats.StatisticsService.log_translation(
        tac_message="METAR XXXX 010000Z",
        iwxxm_version="2025-2",
        icao_airport_code="XXXX",
        translation_status=TranslationStatus.SUCCESS,
        translation_duration_ms=75,
    )

    assert translation_id is not None
    assert metric_calls
    assert metric_calls[0]["icao_region"] == "NAM"


@pytest.mark.asyncio
async def test_log_translation_accepts_string_status(monkeypatch):
    fake_session = _FakeSession()
    metric_calls = []

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "should_log_statistics", lambda: True)
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)
    monkeypatch.setattr(stats, "get_icao_region", lambda _icao: "EUR")
    monkeypatch.setattr(stats, "record_translation_metric", lambda **kwargs: metric_calls.append(kwargs))

    translation_id = await stats.StatisticsService.log_translation(
        tac_message="METAR EGLL 010000Z",
        iwxxm_version="2023-1",
        icao_airport_code="EGLL",
        translation_status="partial",
        translation_duration_ms=88,
    )

    assert translation_id is not None
    assert fake_session.added[0].translation_status == "partial"
    assert metric_calls[0]["status"] == "partial"


@pytest.mark.asyncio
async def test_get_statistics_returns_fallback_on_query_build_failure(monkeypatch):
    @asynccontextmanager
    async def fake_get_db_session():
        yield _FakeSession()

    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics(
        start_date=start,
        end_date=end,
        include_airport_breakdown=True,
        include_error_details=True,
    )

    assert payload["total_translations"] == 0
    assert payload["translations_by_region"] == {}
    assert payload["translations_by_airport"] is None
    assert payload["common_validation_errors"] is None


@pytest.mark.asyncio
async def test_get_statistics_exception_returns_empty_payload(monkeypatch):
    @asynccontextmanager
    async def bad_session():
        raise RuntimeError("db down")
        yield

    monkeypatch.setattr(stats, "get_db_session", bad_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics(start_date=start, end_date=end)

    assert payload["total_translations"] == 0
    assert payload["translations_by_region"] == {}


@pytest.mark.asyncio
async def test_get_statistics_by_region_returns_fallback_on_query_build_failure(monkeypatch):
    @asynccontextmanager
    async def fake_get_db_session():
        yield _FakeSession()

    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics_by_region(start, end)

    assert payload == {}


@pytest.mark.asyncio
async def test_get_statistics_by_region_exception_returns_empty(monkeypatch):
    @asynccontextmanager
    async def bad_session():
        raise RuntimeError("db down")
        yield

    monkeypatch.setattr(stats, "get_db_session", bad_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics_by_region(start, end)

    assert payload == {}


class _RaisingSession(_FakeSession):
    async def execute(self, _query):
        raise TypeError("SQLAlchemy cast(int) typing failure")


@pytest.mark.asyncio
async def test_get_statistics_with_breakdown_flags_returns_fallback_payload(monkeypatch):
    fake_session = _RaisingSession()

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics(
        start_date=start,
        end_date=end,
        include_airport_breakdown=True,
        include_error_details=True,
    )

    # When query execution fails, the service returns a safe fallback payload.
    assert payload["total_translations"] == 0
    assert payload["translations_by_region"] == {}
    assert payload["translations_by_airport"] is None
    assert payload["common_validation_errors"] is None


@pytest.mark.asyncio
async def test_get_statistics_by_region_rows_path_returns_fallback_on_cast_issue(monkeypatch):
    fake_session = _RaisingSession()

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics_by_region(start, end)

    assert payload == {}


@pytest.mark.asyncio
async def test_get_statistics_aggregates_with_synthetic_sql_layer(monkeypatch):
    class _Model:
        id = _Column()
        translation_timestamp = _Column()
        translation_status = _Column()
        translation_duration_ms = _Column()
        icao_region = _Column()
        iwxxm_version = _Column()
        icao_airport_code = _Column()

    fake_session = _FakeSession(
        results=[
            _Result(
                first_row=SimpleNamespace(
                    total=4, successful=3, failed=1, partial=0, avg_duration=100.5, median_duration=90.0
                )
            ),
            _Result(all_rows=[SimpleNamespace(icao_region="NAM", count=4)]),
            _Result(all_rows=[SimpleNamespace(iwxxm_version="2025-2", count=4)]),
            _Result(all_rows=[SimpleNamespace(icao_airport_code="KJFK", count=2)]),
            _Result(all_rows=[SimpleNamespace(translation_status="failed", count=1)]),
        ]
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "TranslationStatisticsModel", _Model)
    monkeypatch.setattr(stats, "select", lambda *_args: _Query())
    monkeypatch.setattr(stats, "and_", lambda *_args: _Expr())
    monkeypatch.setattr(stats, "func", _Func())
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics(
        start_date=start,
        end_date=end,
        include_airport_breakdown=True,
        include_error_details=True,
    )

    assert payload["total_translations"] == 4
    assert payload["successful_translations"] == 3
    assert payload["success_rate"] == 75.0
    assert payload["translations_by_region"] == {"NAM": 4}
    assert payload["translations_by_airport"] == {"KJFK": 2}
    assert payload["common_validation_errors"] == [{"status": "failed", "count": 1}]


@pytest.mark.asyncio
async def test_get_statistics_applies_optional_filters(monkeypatch):
    class _Model:
        id = _Column()
        translation_timestamp = _Column()
        translation_status = _Column()
        translation_duration_ms = _Column()
        icao_region = _Column()
        iwxxm_version = _Column()
        icao_airport_code = _Column()

    fake_session = _FakeSession(
        results=[
            _Result(
                first_row=SimpleNamespace(
                    total=1, successful=1, failed=0, partial=0, avg_duration=50.0, median_duration=50.0
                )
            ),
            _Result(all_rows=[SimpleNamespace(icao_region="NAM", count=1)]),
            _Result(all_rows=[SimpleNamespace(iwxxm_version="2025-2", count=1)]),
        ]
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "TranslationStatisticsModel", _Model)
    monkeypatch.setattr(stats, "select", lambda *_args: _Query())
    monkeypatch.setattr(stats, "and_", lambda *_args: _Expr())
    monkeypatch.setattr(stats, "func", _Func())
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics(
        start_date=start,
        end_date=end,
        icao_region="NAM",
        iwxxm_version="2025-2",
        airport_code="KJFK",
    )

    assert payload["total_translations"] == 1


@pytest.mark.asyncio
async def test_get_statistics_by_region_aggregates_with_synthetic_sql_layer(monkeypatch):
    class _Model:
        id = _Column()
        translation_timestamp = _Column()
        translation_status = _Column()
        translation_duration_ms = _Column()
        icao_region = _Column()

    fake_session = _FakeSession(
        results=[
            _Result(
                all_rows=[
                    SimpleNamespace(icao_region="NAM", total=4, successful=3, avg_duration=100.0),
                    SimpleNamespace(icao_region="EUR", total=2, successful=2, avg_duration=80.0),
                ]
            )
        ]
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "TranslationStatisticsModel", _Model)
    monkeypatch.setattr(stats, "select", lambda *_args: _Query())
    monkeypatch.setattr(stats, "and_", lambda *_args: _Expr())
    monkeypatch.setattr(stats, "func", _Func())
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics_by_region(start, end)

    assert payload["NAM"]["success_rate"] == 75.0
    assert payload["EUR"]["total_translations"] == 2


@pytest.mark.asyncio
async def test_get_statistics_handles_empty_aggregate_row(monkeypatch):
    class _Model:
        id = _Column()
        translation_timestamp = _Column()
        translation_status = _Column()
        translation_duration_ms = _Column()
        icao_region = _Column()
        iwxxm_version = _Column()
        icao_airport_code = _Column()

    fake_session = _FakeSession(
        results=[
            _Result(first_row=None),
            _Result(all_rows=[]),
            _Result(all_rows=[]),
            _Result(all_rows=[]),
            _Result(all_rows=[]),
        ]
    )

    @asynccontextmanager
    async def fake_get_db_session():
        yield fake_session

    monkeypatch.setattr(stats, "TranslationStatisticsModel", _Model)
    monkeypatch.setattr(stats, "select", lambda *_args: _Query())
    monkeypatch.setattr(stats, "and_", lambda *_args: _Expr())
    monkeypatch.setattr(stats, "func", _Func())
    monkeypatch.setattr(stats, "get_db_session", fake_get_db_session)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    payload = await stats.StatisticsService.get_statistics(
        start_date=start,
        end_date=end,
        include_airport_breakdown=True,
        include_error_details=True,
    )

    assert payload["total_translations"] == 0
    assert payload["successful_translations"] == 0
    assert payload["success_rate"] == 0.0
    assert payload["median_duration_ms"] is None
