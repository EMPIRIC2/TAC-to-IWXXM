"""Unit tests for evaluation router async flows with mocked dependencies."""

from __future__ import annotations

import httpx
import pytest
from fastapi import BackgroundTasks, HTTPException

from src.routers import evaluation as eval_router
from src.schemas.evaluation import ComparisonStatus, EvaluationMode, EvaluationRequest


@pytest.mark.asyncio
async def test_create_evaluation_job_requires_station_ids_for_single_mode():
    request = EvaluationRequest(mode=EvaluationMode.SINGLE, station_ids=None)

    with pytest.raises(HTTPException) as exc:
        await eval_router.create_evaluation_job(request, BackgroundTasks(), user={"sub": "u1"})

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_evaluation_job_random_mode_adds_background_task(monkeypatch):
    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=3)

    class _Sampler:
        def get_all_major_airports(self, **_kwargs):
            return ["KJFK", "KLAX"]

    async def fake_create_job_in_db(user_id, mode, total_stations):
        assert user_id == "u1"
        assert mode == "random"
        assert total_stations == 3
        return "job-123"

    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "create_job_in_db", fake_create_job_in_db)

    bg = BackgroundTasks()
    response = await eval_router.create_evaluation_job(request, bg, user={"sub": "u1"})

    assert response.job_id == "job-123"
    assert response.station_count == 3
    assert len(bg.tasks) == 1


@pytest.mark.asyncio
async def test_create_evaluation_job_single_mode_happy_path(monkeypatch):
    request = EvaluationRequest(mode=EvaluationMode.SINGLE, station_ids=["KJFK", "KLAX"])

    async def fake_create_job_in_db(user_id, mode, total_stations):
        assert user_id == "u1"
        assert mode == "single"
        assert total_stations == 2
        return "job-single"

    monkeypatch.setattr(eval_router, "create_job_in_db", fake_create_job_in_db)

    bg = BackgroundTasks()
    response = await eval_router.create_evaluation_job(request, bg, user={"sub": "u1"})

    assert response.job_id == "job-single"
    assert response.station_count == 2


@pytest.mark.asyncio
async def test_create_evaluation_job_all_mode_uses_sampler(monkeypatch):
    request = EvaluationRequest(mode=EvaluationMode.ALL)

    class _Sampler:
        def get_all_major_airports(self, **_kwargs):
            return ["KJFK", "KLAX", "KSEA"]

    async def fake_create_job_in_db(user_id, mode, total_stations):
        assert user_id == "u1"
        assert mode == "all"
        assert total_stations == 3
        return "job-all"

    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "create_job_in_db", fake_create_job_in_db)

    bg = BackgroundTasks()
    response = await eval_router.create_evaluation_job(request, bg, user={"sub": "u1"})

    assert response.job_id == "job-all"
    assert response.station_count == 3


@pytest.mark.asyncio
async def test_create_evaluation_job_db_error_propagates(monkeypatch):
    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=2)

    class _Sampler:
        def get_all_major_airports(self, **_kwargs):
            return ["KJFK", "KLAX"]

    async def fake_create_job_in_db(**_kwargs):
        raise RuntimeError("db unavailable")

    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "create_job_in_db", fake_create_job_in_db)

    with pytest.raises(RuntimeError):
        await eval_router.create_evaluation_job(request, BackgroundTasks(), user={"sub": "u1"})


class _SupabaseClientStub:
    def __init__(self, get_responses):
        self._responses = list(get_responses)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, _url, headers=None):
        _ = headers
        response = self._responses.pop(0)
        return response


class _ResponseStub:
    def __init__(self, payload, headers=None):
        self._payload = payload
        self.headers = headers or {}

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


@pytest.mark.asyncio
async def test_get_job_status_not_found(monkeypatch):
    async def fake_get_job_for_user(job_id, user_id):
        return None

    monkeypatch.setattr(eval_router, "get_job_for_user", fake_get_job_for_user)

    with pytest.raises(HTTPException) as exc:
        await eval_router.get_job_status("job-x", user={"sub": "u1"})

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_job_status_completed_with_summary(monkeypatch):
    payload = {
        "id": "job-1",
        "status": "completed",
        "progress": 10,
        "total_stations": 10,
        "summary_stats": {"total": 10, "passed": 8, "failed": 1, "errors": 1, "pass_rate": 0.8},
        "created_at": "2026-03-16T10:00:00",
        "completed_at": "2026-03-16T10:10:00",
        "error_message": None,
    }

    async def fake_get_job_for_user(job_id, user_id):
        return payload

    monkeypatch.setattr(eval_router, "get_job_for_user", fake_get_job_for_user)

    result = await eval_router.get_job_status("job-1", user={"sub": "u1"})

    assert result.job_id == "job-1"
    assert result.summary.passed == 8
    assert result.completed_at is not None


@pytest.mark.asyncio
async def test_get_job_results_with_status_filter(monkeypatch):
    async def fake_get_job_for_user(job_id, user_id):
        return {"id": job_id}

    async def fake_list_results_for_job(job_id, *, limit, offset, status_filter=None):
        return (
            [
                {
                    "station_id": "KJFK",
                    "created_at": "2026-03-16T10:00:00",
                    "tac_input": "METAR KJFK",
                    "our_iwxxm": "<our/>",
                    "their_iwxxm": "<their/>",
                    "comparison_status": "pass",
                    "comparison_detail": {
                        "passed": True,
                        "our_elements": 1,
                        "their_elements": 1,
                        "missing_elements": [],
                        "extra_elements": [],
                        "value_mismatches": [],
                        "error_message": None,
                    },
                    "errors": [],
                }
            ],
            1,
        )

    monkeypatch.setattr(eval_router, "get_job_for_user", fake_get_job_for_user)
    monkeypatch.setattr(eval_router, "list_results_for_job", fake_list_results_for_job)

    result = await eval_router.get_job_results(
        "job-1",
        page=2,
        per_page=1,
        status_filter=ComparisonStatus.PASS,
        user={"sub": "u1"},
    )

    assert result.page == 2
    assert result.total_results == 1
    assert result.results[0].comparison_status == ComparisonStatus.PASS


@pytest.mark.asyncio
async def test_get_job_results_not_found(monkeypatch):
    async def fake_get_job_for_user(job_id, user_id):
        return None

    monkeypatch.setattr(eval_router, "get_job_for_user", fake_get_job_for_user)

    with pytest.raises(HTTPException) as exc:
        await eval_router.get_job_results("job-x", user={"sub": "u1"})

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_user_jobs_with_summary(monkeypatch):
    async def fake_list_jobs_for_user(user_id, limit, offset):
        return (
            [
                {
                    "id": "job-1",
                    "status": "completed",
                    "station_count": 5,
                    "progress": 5,
                    "summary_stats": {"total": 5, "passed": 5, "failed": 0, "errors": 0, "pass_rate": 1.0},
                    "created_at": "2026-03-16T10:00:00",
                    "completed_at": "2026-03-16T10:10:00",
                }
            ],
            1,
        )

    monkeypatch.setattr(eval_router, "list_jobs_for_user", fake_list_jobs_for_user)

    result = await eval_router.list_user_jobs(page=1, per_page=20, user={"sub": "u1"})

    assert result.total == 1
    assert result.jobs[0].summary.passed == 5


@pytest.mark.asyncio
async def test_run_evaluation_job_completes_and_updates_summary(monkeypatch):
    statuses = []
    saved_results = []

    async def fake_update_job_status(job_id, status, progress=None, summary_stats=None, error_message=None):
        statuses.append((status, progress, summary_stats, error_message))

    async def fake_save_result(job_id, result):
        saved_results.append((job_id, result.station_id, result.comparison_status.value))

    class _Sampler:
        def sample_random_stations(self, **_kwargs):
            return ["KJFK"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def fetch_metar_batch(self, stations, hours):
            _ = (stations, hours)
            return {"KJFK": ("METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", "<iwxxm/>")}

    class _CompareResult:
        passed = True
        our_elements = 1
        their_elements = 1
        missing_elements = []
        extra_elements = []
        value_mismatches = []
        error_message = None

    class _EvalService:
        def compare_iwxxm(self, our, theirs):
            _ = (our, theirs)
            return _CompareResult()

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save_result)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)
    monkeypatch.setattr(eval_router, "convert_metar_tac", lambda _tac: "<iwxxm/>")

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1, hours=1.5)
    await eval_router.run_evaluation_job("job-1", request)

    assert statuses[0][0] == "running"
    assert any(item[0] == "completed" for item in statuses)
    assert saved_results[0] == ("job-1", "KJFK", "pass")


@pytest.mark.asyncio
async def test_run_evaluation_job_handles_missing_tac_as_error(monkeypatch):
    statuses = []
    saved_results = []

    async def fake_update_job_status(job_id, status, progress=None, summary_stats=None, error_message=None):
        statuses.append((status, progress, summary_stats, error_message))

    async def fake_save_result(job_id, result):
        saved_results.append(result)

    class _Sampler:
        def sample_random_stations(self, **_kwargs):
            return ["KSEA"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def fetch_metar_batch(self, stations, hours):
            _ = (stations, hours)
            return {"KSEA": (None, None)}

    class _EvalService:
        def compare_iwxxm(self, our, theirs):
            _ = (our, theirs)
            raise AssertionError("compare should not be called")

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save_result)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1, hours=1.5)
    await eval_router.run_evaluation_job("job-2", request)

    assert saved_results
    assert saved_results[0].comparison_status.value == "error"
    assert any("No raw TAC data from API" in msg for msg in saved_results[0].errors)
    assert any(item[0] == "completed" for item in statuses)


@pytest.mark.asyncio
async def test_run_evaluation_job_single_mode_conversion_error(monkeypatch):
    statuses = []
    saved_results = []

    async def fake_update_job_status(job_id, status, progress=None, summary_stats=None, error_message=None):
        statuses.append((status, progress, summary_stats, error_message))

    async def fake_save_result(job_id, result):
        _ = job_id
        saved_results.append(result)

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def fetch_metar_batch(self, stations, hours):
            _ = (stations, hours)
            return {"KJFK": ("METAR KJFK", "<iwxxm/>")}

    class _EvalService:
        def compare_iwxxm(self, _our, _theirs):
            raise AssertionError("comparison should not run")

    def fail_convert(_tac):
        raise eval_router.ConversionError("bad tac")

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save_result)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)
    monkeypatch.setattr(eval_router, "convert_metar_tac", fail_convert)

    request = EvaluationRequest(mode=EvaluationMode.SINGLE, station_ids=["KJFK"], hours=1.0)
    await eval_router.run_evaluation_job("job-3", request)

    assert saved_results[0].comparison_status.value == "error"
    assert any("Conversion error" in msg for msg in saved_results[0].errors)
    assert any(item[0] == "completed" for item in statuses)


@pytest.mark.asyncio
async def test_run_evaluation_job_comparison_fail_branch(monkeypatch):
    saved_results = []

    async def fake_update_job_status(*_args, **_kwargs):
        return None

    async def fake_save_result(_job_id, result):
        saved_results.append(result)

    class _Sampler:
        def sample_random_stations(self, **_kwargs):
            return ["KSEA"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def fetch_metar_batch(self, stations, hours):
            _ = (stations, hours)
            return {"KSEA": ("METAR KSEA", "<their/>")}

    class _CompareResult:
        passed = False
        our_elements = 1
        their_elements = 2
        missing_elements = ["x"]
        extra_elements = []
        value_mismatches = []
        error_message = None

    class _EvalService:
        def compare_iwxxm(self, _our, _theirs):
            return _CompareResult()

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save_result)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)
    monkeypatch.setattr(eval_router, "convert_metar_tac", lambda _tac: "<our/>")

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1, hours=1.0)
    await eval_router.run_evaluation_job("job-4", request)

    assert saved_results[0].comparison_status.value == "fail"


@pytest.mark.asyncio
async def test_run_evaluation_job_top_level_failure_marks_failed(monkeypatch):
    statuses = []

    async def fake_update_job_status(job_id, status, progress=None, summary_stats=None, error_message=None):
        _ = (job_id, progress, summary_stats)
        statuses.append((status, error_message))

    class _Sampler:
        def sample_random_stations(self, **_kwargs):
            raise RuntimeError("sampler down")

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1)
    await eval_router.run_evaluation_job("job-5", request)

    assert statuses[0][0] == "running"
    assert statuses[-1][0] == "failed"
    assert "sampler down" in statuses[-1][1]


@pytest.mark.asyncio
async def test_run_evaluation_job_single_mode_without_station_ids_fails(monkeypatch):
    statuses = []

    async def fake_update_job_status(job_id, status, progress=None, summary_stats=None, error_message=None):
        _ = (job_id, progress, summary_stats)
        statuses.append((status, error_message))

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)

    request = EvaluationRequest(mode=EvaluationMode.SINGLE, station_ids=[])
    await eval_router.run_evaluation_job("job-6", request)

    assert statuses[-1][0] == "failed"
    assert "station_ids required" in statuses[-1][1]


@pytest.mark.asyncio
async def test_run_evaluation_job_all_mode_uses_sampler(monkeypatch):
    saved_results = []

    async def fake_update_job_status(*_args, **_kwargs):
        return None

    async def fake_save_result(_job_id, result):
        saved_results.append(result)

    class _Sampler:
        def get_all_major_airports(self, **_kwargs):
            return ["KORD"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def fetch_metar_batch(self, stations, hours):
            _ = (stations, hours)
            return {"KORD": ("METAR KORD", "<their/>")}

    class _CompareResult:
        passed = True
        our_elements = 1
        their_elements = 1
        missing_elements = []
        extra_elements = []
        value_mismatches = []
        error_message = None

    class _EvalService:
        def compare_iwxxm(self, _our, _theirs):
            return _CompareResult()

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save_result)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)
    monkeypatch.setattr(eval_router, "convert_metar_tac", lambda _tac: "<our/>")

    request = EvaluationRequest(mode=EvaluationMode.ALL, hours=1.0)
    await eval_router.run_evaluation_job("job-7", request)

    assert saved_results[0].station_id == "KORD"


@pytest.mark.asyncio
async def test_run_evaluation_job_unexpected_conversion_error(monkeypatch):
    saved_results = []

    async def fake_update_job_status(*_args, **_kwargs):
        return None

    async def fake_save_result(_job_id, result):
        saved_results.append(result)

    class _Sampler:
        def sample_random_stations(self, **_kwargs):
            return ["KJFK"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def fetch_metar_batch(self, stations, hours):
            _ = (stations, hours)
            return {"KJFK": ("METAR KJFK", "<their/>")}

    def boom_convert(_tac):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save_result)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "convert_metar_tac", boom_convert)

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1, hours=1.0)
    await eval_router.run_evaluation_job("job-8", request)

    assert any("Unexpected error" in msg for msg in saved_results[0].errors)


@pytest.mark.asyncio
async def test_run_evaluation_job_comparison_exception(monkeypatch):
    saved_results = []

    async def fake_update_job_status(*_args, **_kwargs):
        return None

    async def fake_save_result(_job_id, result):
        saved_results.append(result)

    class _Sampler:
        def sample_random_stations(self, **_kwargs):
            return ["KJFK"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def fetch_metar_batch(self, stations, hours):
            _ = (stations, hours)
            return {"KJFK": ("METAR KJFK", "<their/>")}

    class _EvalService:
        def compare_iwxxm(self, _our, _theirs):
            raise RuntimeError("compare failed")

    monkeypatch.setattr(eval_router, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save_result)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)
    monkeypatch.setattr(eval_router, "convert_metar_tac", lambda _tac: "<our/>")

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1, hours=1.0)
    await eval_router.run_evaluation_job("job-9", request)

    assert any("Comparison error" in msg for msg in saved_results[0].errors)
    assert saved_results[0].comparison_status.value == "error"
