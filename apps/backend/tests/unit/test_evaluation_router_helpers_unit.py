"""Unit tests targeting uncovered branches in src/routers/evaluation.py.

Covers:
- get_supabase_client() body (lines 38-43)
- create_job_in_db() list/dict response branches (lines 52-66)
- update_job_status() all conditional branches (lines 77-93)
- save_result_to_db() with and without comparison (lines 98-111)
- run_evaluation_job() SINGLE mode stations assignment (line 124)
- run_evaluation_job() ALL mode get_all_major_airports (line 133)
- run_evaluation_job() unexpected Exception in conversion (lines 161-162)
- run_evaluation_job() Exception in comparison (lines 185-187)
- run_evaluation_job() elif errors: False branch (188->191)
- get_job_results() without status_filter (branches 334->337, 344->347)
"""

from __future__ import annotations

from datetime import datetime

import pytest

from src.routers import evaluation as eval_router
from src.schemas.evaluation import (
    ComparisonDetail,
    ComparisonStatus,
    EvaluationMode,
    EvaluationRequest,
    EvaluationResultDetail,
)

# ---------------------------------------------------------------------------
# Shared fake HTTP infrastructure
# ---------------------------------------------------------------------------


class _FakeHTTPResponse:
    """Minimal httpx-response stub."""

    def __init__(self, payload, headers=None):
        self._payload = payload
        self.headers = headers or {}

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _FakeHTTPClient:
    """Async-compatible HTTP client stub for Supabase operations."""

    def __init__(self, post_payload=None, patch_payload=None):
        self._post_payload = post_payload
        self._patch_payload = patch_payload
        # Capture the dict sent via PATCH so tests can inspect it
        self.last_patch_data: dict = {}

    async def post(self, _url, json=None):
        return _FakeHTTPResponse(self._post_payload)

    async def patch(self, _url, json=None):
        if json is not None:
            self.last_patch_data = dict(json)
        return _FakeHTTPResponse(self._patch_payload)


class _FakeHTTPClientCtx:
    """Async context manager that yields a _FakeHTTPClient."""

    def __init__(self, client):
        self._client = client

    async def __aenter__(self):
        return self._client

    async def __aexit__(self, *args):
        pass


def _make_supabase_factory(client):
    """Build a get_supabase_client() replacement that yields *client*."""

    async def _inner():
        return _FakeHTTPClientCtx(client)

    return _inner


# ---------------------------------------------------------------------------
# Stub for get_job_results tests (reuses pattern from other unit test file)
# ---------------------------------------------------------------------------


class _ResponseStub:
    def __init__(self, payload, headers=None):
        self._payload = payload
        self.headers = headers or {}

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _SupabaseClientStub:
    """Pops pre-configured responses for each sequential get() call."""

    def __init__(self, get_responses):
        self._responses = list(get_responses)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    async def get(self, _url, headers=None):
        return self._responses.pop(0)


# ---------------------------------------------------------------------------
# get_supabase_client() — lines 38-43
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_supabase_client_returns_httpx_async_client():
    """Directly calling get_supabase_client() should return an httpx.AsyncClient."""
    import httpx

    client = await eval_router.get_supabase_client()
    assert isinstance(client, httpx.AsyncClient)
    await client.aclose()


# ---------------------------------------------------------------------------
# create_job_in_db() — lines 52-66
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_job_in_db_extracts_id_from_list_response(monkeypatch):
    """create_job_in_db must return result[0]['id'] when the POST returns a list."""
    fake = _FakeHTTPClient(post_payload=[{"id": "list-id-abc"}])
    monkeypatch.setattr(eval_router, "get_supabase_client", _make_supabase_factory(fake))

    result = await eval_router.create_job_in_db("user-1", "random", 50)

    assert result == "list-id-abc"


@pytest.mark.asyncio
async def test_create_job_in_db_extracts_id_from_dict_response(monkeypatch):
    """create_job_in_db must return result['id'] when the POST returns a dict."""
    fake = _FakeHTTPClient(post_payload={"id": "dict-id-xyz"})
    monkeypatch.setattr(eval_router, "get_supabase_client", _make_supabase_factory(fake))

    result = await eval_router.create_job_in_db("user-1", "single", 3)

    assert result == "dict-id-xyz"


# ---------------------------------------------------------------------------
# update_job_status() — lines 77-93
# All four `if` branches inside the function are exercised:
#   progress is not None, summary_stats is not None, error_message is not None,
#   status == "completed"  →  completed_at is added
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_job_status_with_all_optional_params(monkeypatch):
    """All four conditional branches in update_job_status must execute."""
    fake = _FakeHTTPClient(patch_payload=None)
    monkeypatch.setattr(eval_router, "get_supabase_client", _make_supabase_factory(fake))

    await eval_router.update_job_status(
        "job-99",
        "completed",
        progress=20,
        summary_stats={"total": 20, "passed": 18, "failed": 1, "errors": 1, "pass_rate": 0.9},
        error_message="test-msg",
    )

    data = fake.last_patch_data
    assert data["status"] == "completed"
    assert data["progress"] == 20
    assert "summary_stats" in data
    assert data["error_message"] == "test-msg"
    assert "completed_at" in data  # status == "completed" branch


@pytest.mark.asyncio
async def test_update_job_status_with_no_optional_params(monkeypatch):
    """No optional fields → none of the four conditional branches executes."""
    fake = _FakeHTTPClient(patch_payload=None)
    monkeypatch.setattr(eval_router, "get_supabase_client", _make_supabase_factory(fake))

    await eval_router.update_job_status("job-100", "running")

    data = fake.last_patch_data
    assert data["status"] == "running"
    assert "progress" not in data
    assert "summary_stats" not in data
    assert "error_message" not in data
    assert "completed_at" not in data


# ---------------------------------------------------------------------------
# save_result_to_db() — lines 98-111
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_result_to_db_with_comparison_calls_dict(monkeypatch):
    """When comparison is set, save_result_to_db calls comparison.dict()."""
    fake = _FakeHTTPClient(post_payload=None)
    monkeypatch.setattr(eval_router, "get_supabase_client", _make_supabase_factory(fake))

    comparison = ComparisonDetail(
        passed=True,
        our_elements=4,
        their_elements=4,
        missing_elements=[],
        extra_elements=[],
        value_mismatches=[],
    )
    result = EvaluationResultDetail(
        station_id="KJFK",
        timestamp=datetime.utcnow(),
        comparison_status=ComparisonStatus.PASS,
        comparison=comparison,
    )

    # Should complete without error
    await eval_router.save_result_to_db("job-xyz", result)


@pytest.mark.asyncio
async def test_save_result_to_db_without_comparison_passes_none(monkeypatch):
    """When comparison is None, save_result_to_db stores None for comparison_detail."""
    fake = _FakeHTTPClient(post_payload=None)
    monkeypatch.setattr(eval_router, "get_supabase_client", _make_supabase_factory(fake))

    result = EvaluationResultDetail(
        station_id="KSEA",
        timestamp=datetime.utcnow(),
        comparison_status=ComparisonStatus.ERROR,
        comparison=None,
    )

    await eval_router.save_result_to_db("job-xyz", result)


# ---------------------------------------------------------------------------
# run_evaluation_job() — line 124 (SINGLE assignment) and line 133 (ALL)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_evaluation_job_single_mode_assigns_station_ids(monkeypatch):
    """SINGLE mode must assign stations = request.station_ids (line 124)."""
    seen_stations = {}

    async def fake_update(*_a, **_kw):
        pass

    async def fake_save(_job_id, _result):
        pass

    class _Sampler:
        pass  # never called in SINGLE mode

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def fetch_metar_batch(self, stations, hours):
            seen_stations["stations"] = list(stations)
            return {}  # empty batch → no per-station work

    monkeypatch.setattr(eval_router, "update_job_status", fake_update)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)

    request = EvaluationRequest(mode=EvaluationMode.SINGLE, station_ids=["KJFK", "EGLL"])
    await eval_router.run_evaluation_job("job-single", request)

    assert seen_stations["stations"] == ["KJFK", "EGLL"]


@pytest.mark.asyncio
async def test_run_evaluation_job_all_mode_calls_get_all_major_airports(monkeypatch):
    """ALL mode must invoke sampler.get_all_major_airports (line 133)."""
    sampler_calls = {}
    seen_stations = {}

    async def fake_update(*_a, **_kw):
        pass

    async def fake_save(_job_id, _result):
        pass

    class _Sampler:
        def get_all_major_airports(self, large_only=True, scheduled_service_only=True):
            sampler_calls["large_only"] = large_only
            sampler_calls["scheduled_service_only"] = scheduled_service_only
            return ["KJFK", "EGLL", "YSSY"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def fetch_metar_batch(self, stations, hours):
            seen_stations["stations"] = list(stations)
            return {}

    monkeypatch.setattr(eval_router, "update_job_status", fake_update)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)

    request = EvaluationRequest(
        mode=EvaluationMode.ALL,
        large_airports_only=True,
        scheduled_service_only=False,
    )
    await eval_router.run_evaluation_job("job-all", request)

    assert sampler_calls["large_only"] is True
    assert sampler_calls["scheduled_service_only"] is False
    assert seen_stations["stations"] == ["KJFK", "EGLL", "YSSY"]


# ---------------------------------------------------------------------------
# run_evaluation_job() — lines 161-162 (unexpected Exception in conversion)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_evaluation_job_records_unexpected_conversion_exception(monkeypatch):
    """A non-ConversionError during conversion must append 'Unexpected error' (lines 161-162)."""
    saved = []

    async def fake_update(*_a, **_kw):
        pass

    async def fake_save(_job_id, result):
        saved.append(result)

    class _Sampler:
        def sample_random_stations(self, **_kw):
            return ["KLAX"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def fetch_metar_batch(self, stations, hours):
            return {"KLAX": ("METAR KLAX TAC", "<their/>")}

    class _EvalService:
        def compare_iwxxm(self, _our, _theirs):
            raise AssertionError("compare should not run after unexpected error")

    def explode(_tac):
        raise RuntimeError("internal crash")  # NOT a ConversionError

    monkeypatch.setattr(eval_router, "update_job_status", fake_update)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)
    monkeypatch.setattr(eval_router, "convert_metar_tac", explode)

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1)
    await eval_router.run_evaluation_job("job-unexpected", request)

    assert saved, "a result should be saved"
    assert any("Unexpected error" in msg for msg in saved[0].errors)
    assert saved[0].comparison_status.value == "error"


# ---------------------------------------------------------------------------
# run_evaluation_job() — lines 185-187 (Exception inside compare_iwxxm)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_evaluation_job_records_comparison_exception(monkeypatch):
    """An exception from compare_iwxxm must append 'Comparison error' (lines 185-187)."""
    saved = []

    async def fake_update(*_a, **_kw):
        pass

    async def fake_save(_job_id, result):
        saved.append(result)

    class _Sampler:
        def sample_random_stations(self, **_kw):
            return ["KSFO"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def fetch_metar_batch(self, stations, hours):
            return {"KSFO": ("METAR KSFO TAC", "<their/>")}

    class _EvalService:
        def compare_iwxxm(self, _our, _theirs):
            raise ValueError("comparison boom")

    monkeypatch.setattr(eval_router, "update_job_status", fake_update)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)
    monkeypatch.setattr(eval_router, "convert_metar_tac", lambda _tac: "<our/>")

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1)
    await eval_router.run_evaluation_job("job-comp-err", request)

    assert saved, "a result should be saved"
    assert any("Comparison error" in msg for msg in saved[0].errors)


# ---------------------------------------------------------------------------
# run_evaluation_job() — branch 188->191  (elif errors: is False)
# This happens when conversion succeeds but their_iwxxm is None — no errors
# were recorded, so elif errors: evaluates to False.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_evaluation_job_no_reference_iwxxm_and_no_errors(monkeypatch):
    """When our conversion succeeds but no reference IWXXM exists, errors is
    empty so the elif-errors branch at line 188 is False; error_count stays 0."""
    saved = []
    statuses = []

    async def fake_update(_job_id, status, progress=None, summary_stats=None, **_kw):
        statuses.append({"status": status, "summary": summary_stats})

    async def fake_save(_job_id, result):
        saved.append(result)

    class _Sampler:
        def sample_random_stations(self, **_kw):
            return ["KATL"]

    class _AviationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def fetch_metar_batch(self, stations, hours):
            # TAC succeeds; no reference IWXXM available from source
            return {"KATL": ("METAR KATL TAC", None)}

    class _EvalService:
        def compare_iwxxm(self, _our, _theirs):
            raise AssertionError("compare must not be called")

    monkeypatch.setattr(eval_router, "update_job_status", fake_update)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _AviationClient)
    monkeypatch.setattr(eval_router, "EvaluationService", _EvalService)
    monkeypatch.setattr(eval_router, "convert_metar_tac", lambda _tac: "<our/>")

    request = EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1)
    await eval_router.run_evaluation_job("job-no-ref", request)

    assert saved, "result should still be stored"
    # No errors were added (conversion succeeded, just no reference)
    assert saved[0].errors == []
    # The completed summary reports errors=0 (elif errors: was False)
    completed = [s for s in statuses if s["status"] == "completed"]
    assert completed, "job should reach completed state"
    assert completed[0]["summary"]["errors"] == 0


# ---------------------------------------------------------------------------
# get_job_results() without status_filter — branches 334->337 and 344->347
# The existing tests always pass a status_filter; this test uses None so that
# both `if status_filter:` guards evaluate to False.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_job_results_without_status_filter(monkeypatch):
    """Calling get_job_results with status_filter=None covers the False paths of
    both if-status_filter branches (334->337 and 344->347)."""
    responses = [
        _ResponseStub([{"id": "job-1"}]),  # job ownership
        _ResponseStub([]),  # results (empty)
        _ResponseStub([], headers={"Content-Range": "0-0/0"}),  # count
    ]

    async def fake_get_supabase_client():
        return _SupabaseClientStub(responses)

    monkeypatch.setattr(eval_router, "get_supabase_client", fake_get_supabase_client)

    result = await eval_router.get_job_results(
        "job-1",
        page=1,
        per_page=20,
        status_filter=None,
        user={"sub": "u1"},
    )

    assert result.page == 1
    assert result.total_results == 0
    assert result.results == []
    assert result.total_pages == 0


# ---------------------------------------------------------------------------
# run_evaluation_job() — line 124 (raise ValueError for SINGLE without ids)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_evaluation_job_single_mode_raises_when_no_station_ids(monkeypatch):
    """When SINGLE mode is called without station_ids the inner ValueError is
    raised and caught by the outer try/except, marking the job as failed (line 124)."""
    statuses = []

    async def fake_update(_job_id, status, progress=None, summary_stats=None, error_message=None):
        statuses.append({"status": status, "error": error_message})

    class _Sampler:
        pass  # never instantiated with meaningful data in SINGLE mode

    monkeypatch.setattr(eval_router, "update_job_status", fake_update)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)

    # station_ids intentionally omitted so the inner guard raises ValueError
    request = EvaluationRequest(mode=EvaluationMode.SINGLE, station_ids=None)
    await eval_router.run_evaluation_job("job-no-ids", request)

    assert statuses[0]["status"] == "running"
    assert statuses[-1]["status"] == "failed"
    assert "station_ids required" in statuses[-1]["error"]
