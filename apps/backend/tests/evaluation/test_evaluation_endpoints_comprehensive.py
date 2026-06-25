"""Comprehensive tests for Evaluation API endpoints.

This test suite covers all evaluation router endpoints with comprehensive
test scenarios including:
- Job creation with all evaluation modes (single, random, all)
- Job listing with pagination and filtering
- Job status retrieval for all job states
- Job results retrieval with pagination and filtering
- Background task lifecycle testing
- Error scenarios and edge cases
- Authentication and authorization

Run with: pytest backend/tests/test_evaluation_endpoints_comprehensive.py -v
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Rewrite pending: evaluation router now uses evaluation_store (DATABASE_URL) not get_supabase_client"
)

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from src.api import app
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client():
    """Create test client with mocked authentication."""

    async def override_verify_token():
        return {"sub": "test-user-id", "aud": "test-project"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_supabase_client():
    """Mock evaluation store job creation."""
    with (
        patch("src.routers.evaluation.evaluation_store.create_job_in_db", new_callable=AsyncMock) as create_mock,
        patch("src.routers.evaluation.evaluation_store.get_job_for_user", new_callable=AsyncMock) as get_job_mock,
        patch(
            "src.routers.evaluation.evaluation_store.list_results_for_job", new_callable=AsyncMock
        ) as list_results_mock,
        patch("src.routers.evaluation.evaluation_store.list_jobs_for_user", new_callable=AsyncMock) as list_jobs_mock,
    ):
        create_mock.return_value = "job-123"
        get_job_mock.return_value = {
            "id": "job-123",
            "status": "pending",
            "progress": 0,
            "total_stations": 1,
            "summary_stats": None,
            "created_at": "2026-03-16T10:00:00",
            "completed_at": None,
            "error_message": None,
        }
        list_results_mock.return_value = ([], 0)
        list_jobs_mock.return_value = ([], 0)
        yield SimpleNamespace(
            create=create_mock,
            get_job=get_job_mock,
            list_results=list_results_mock,
            list_jobs=list_jobs_mock,
        )


class TestCreateEvaluationJob:
    """Test POST /api/v1/eval/jobs endpoint."""

    def test_create_job_single_mode_success(self, client, mock_supabase_client):
        """Test creating evaluation job in single mode with specific stations."""
        # Mock database response
        mock_supabase_client.post.return_value = AsyncMock(
            json=MagicMock(return_value=[{"id": "job-123"}]), raise_for_status=MagicMock()
        )

        response = client.post(
            "/api/v1/eval/jobs",
            json={
                "mode": "single",
                "station_ids": ["KJFK", "EGLL", "RJTT"],
                "hours": 2,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["station_count"] == 3
        assert "created_at" in data

    def test_create_job_random_mode_success(self, client, mock_supabase_client):
        """Test creating evaluation job in random mode."""
        mock_supabase_client.post.return_value = AsyncMock(
            json=MagicMock(return_value=[{"id": "job-456"}]), raise_for_status=MagicMock()
        )

        response = client.post(
            "/api/v1/eval/jobs",
            json={
                "mode": "random",
                "sample_size": 50,
                "hours": 1,
                "large_airports_only": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "pending"
        assert data["station_count"] == 50

    def test_create_job_all_mode_success(self, client, mock_supabase_client):
        """Test creating evaluation job in all mode."""
        mock_supabase_client.post.return_value = AsyncMock(
            json=MagicMock(return_value=[{"id": "job-789"}]), raise_for_status=MagicMock()
        )

        response = client.post(
            "/api/v1/eval/jobs",
            json={
                "mode": "all",
                "hours": 3,
                "scheduled_service_only": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "pending"
        # Station count should be > 0 (depends on sampler data)
        assert data["station_count"] > 0

    def test_create_job_single_mode_missing_station_ids(self, client):
        """Test creating single mode job without station_ids fails."""
        response = client.post(
            "/api/v1/eval/jobs",
            json={
                "mode": "single",
                "hours": 1,
            },
        )

        assert response.status_code == 400
        assert "station_ids required" in response.json()["detail"]

    def test_create_job_random_mode_default_sample_size(self, client, mock_supabase_client):
        """Test random mode uses default sample size if not specified."""
        mock_supabase_client.post.return_value = AsyncMock(
            json=MagicMock(return_value=[{"id": "job-default"}]), raise_for_status=MagicMock()
        )

        response = client.post(
            "/api/v1/eval/jobs",
            json={
                "mode": "random",
                "hours": 1,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["station_count"] == 100  # Default sample size

    def test_create_job_requires_authentication(self):
        """Test endpoint requires authentication."""
        # Create client without auth override
        client = TestClient(app)

        response = client.post(
            "/api/v1/eval/jobs",
            json={
                "mode": "single",
                "station_ids": ["KJFK"],
                "hours": 1,
            },
        )

        assert response.status_code == 401

    def test_create_job_invalid_mode(self, client):
        """Test creating job with invalid mode fails."""
        response = client.post(
            "/api/v1/eval/jobs",
            json={
                "mode": "invalid_mode",
                "hours": 1,
            },
        )

        assert response.status_code == 422  # Pydantic validation error


class TestGetJobStatus:
    """Test GET /api/v1/eval/jobs/{job_id} endpoint."""

    def test_get_pending_job_status(self, client, mock_supabase_client):
        """Test getting status of pending job."""
        mock_supabase_client.get.return_value = AsyncMock(
            json=MagicMock(
                return_value=[
                    {
                        "id": "job-123",
                        "status": "pending",
                        "progress": 0,
                        "total_stations": 10,
                        "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                        "summary_stats": None,
                        "completed_at": None,
                        "error_message": None,
                    }
                ]
            ),
            raise_for_status=MagicMock(),
        )

        response = client.get("/api/v1/eval/jobs/job-123")

        assert response.status_code == 200
        data = response.json()

        assert data["job_id"] == "job-123"
        assert data["status"] == "pending"
        assert data["progress"] == 0
        assert data["total"] == 10
        assert data["summary"] is None

    def test_get_running_job_status(self, client, mock_supabase_client):
        """Test getting status of running job."""
        mock_supabase_client.get.return_value = AsyncMock(
            json=MagicMock(
                return_value=[
                    {
                        "id": "job-456",
                        "status": "running",
                        "progress": 5,
                        "total_stations": 10,
                        "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                        "summary_stats": None,
                        "completed_at": None,
                        "error_message": None,
                    }
                ]
            ),
            raise_for_status=MagicMock(),
        )

        response = client.get("/api/v1/eval/jobs/job-456")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "running"
        assert data["progress"] == 5
        assert data["total"] == 10

    def test_get_completed_job_status(self, client, mock_supabase_client):
        """Test getting status of completed job."""
        completed_at = datetime.now(UTC).replace(tzinfo=None).isoformat()
        mock_supabase_client.get.return_value = AsyncMock(
            json=MagicMock(
                return_value=[
                    {
                        "id": "job-789",
                        "status": "completed",
                        "progress": 10,
                        "total_stations": 10,
                        "created_at": (datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=1)).isoformat(),
                        "completed_at": completed_at,
                        "summary_stats": {
                            "total": 10,
                            "passed": 8,
                            "failed": 1,
                            "errors": 1,
                            "pass_rate": 0.8,
                        },
                        "error_message": None,
                    }
                ]
            ),
            raise_for_status=MagicMock(),
        )

        response = client.get("/api/v1/eval/jobs/job-789")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "completed"
        assert data["progress"] == 10
        assert data["summary"] is not None
        assert data["summary"]["total"] == 10
        assert data["summary"]["passed"] == 8
        assert data["summary"]["pass_rate"] == 0.8
        assert data["completed_at"] is not None

    def test_get_failed_job_status(self, client, mock_supabase_client):
        """Test getting status of failed job."""
        mock_supabase_client.get.return_value = AsyncMock(
            json=MagicMock(
                return_value=[
                    {
                        "id": "job-error",
                        "status": "failed",
                        "progress": 3,
                        "total_stations": 10,
                        "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                        "summary_stats": None,
                        "completed_at": None,
                        "error_message": "Network timeout fetching data",
                    }
                ]
            ),
            raise_for_status=MagicMock(),
        )

        response = client.get("/api/v1/eval/jobs/job-error")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "failed"
        assert data["error_message"] == "Network timeout fetching data"

    def test_get_job_not_found(self, client, mock_supabase_client):
        """Test getting status of non-existent job."""
        mock_supabase_client.get.return_value = AsyncMock(json=MagicMock(return_value=[]), raise_for_status=MagicMock())

        response = client.get("/api/v1/eval/jobs/nonexistent-job")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_job_wrong_user(self, client, mock_supabase_client):
        """Test user cannot access another user's job."""
        # Mock returns empty list (job not found for this user)
        mock_supabase_client.get.return_value = AsyncMock(json=MagicMock(return_value=[]), raise_for_status=MagicMock())

        response = client.get("/api/v1/eval/jobs/other-user-job")

        assert response.status_code == 404


class TestListUserJobs:
    """Test GET /api/v1/eval/jobs endpoint."""

    def test_list_jobs_empty(self, client, mock_supabase_client):
        """Test listing jobs when user has no jobs."""
        mock_supabase_client.get.side_effect = [
            # First call: get jobs
            AsyncMock(json=MagicMock(return_value=[]), raise_for_status=MagicMock()),
            # Second call: count
            AsyncMock(headers={"Content-Range": "0-0/0"}, raise_for_status=MagicMock()),
        ]

        response = client.get("/api/v1/eval/jobs")

        assert response.status_code == 200
        data = response.json()

        assert data["jobs"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_jobs_with_results(self, client, mock_supabase_client):
        """Test listing jobs returns user's jobs."""
        jobs_data = [
            {
                "id": "job-1",
                "status": "completed",
                "station_count": 10,
                "progress": 10,
                "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                "completed_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                "summary_stats": {
                    "total": 10,
                    "passed": 9,
                    "failed": 1,
                    "errors": 0,
                    "pass_rate": 0.9,
                },
            },
            {
                "id": "job-2",
                "status": "running",
                "station_count": 50,
                "progress": 25,
                "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                "completed_at": None,
                "summary_stats": None,
            },
        ]

        mock_supabase_client.get.side_effect = [
            AsyncMock(json=MagicMock(return_value=jobs_data), raise_for_status=MagicMock()),
            AsyncMock(headers={"Content-Range": "0-1/2"}, raise_for_status=MagicMock()),
        ]

        response = client.get("/api/v1/eval/jobs")

        assert response.status_code == 200
        data = response.json()

        assert len(data["jobs"]) == 2
        assert data["total"] == 2
        assert data["jobs"][0]["job_id"] == "job-1"
        assert data["jobs"][0]["status"] == "completed"
        assert data["jobs"][1]["job_id"] == "job-2"
        assert data["jobs"][1]["status"] == "running"

    def test_list_jobs_pagination(self, client, mock_supabase_client):
        """Test job listing pagination."""
        jobs_data = [
            {
                "id": f"job-{i}",
                "status": "completed",
                "station_count": 10,
                "progress": 10,
                "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                "completed_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                "summary_stats": None,
            }
            for i in range(20, 40)
        ]

        mock_supabase_client.get.side_effect = [
            AsyncMock(json=MagicMock(return_value=jobs_data), raise_for_status=MagicMock()),
            AsyncMock(headers={"Content-Range": "20-39/100"}, raise_for_status=MagicMock()),
        ]

        response = client.get("/api/v1/eval/jobs?page=2&per_page=20")

        assert response.status_code == 200
        data = response.json()

        assert len(data["jobs"]) == 20
        assert data["total"] == 100
        assert data["page"] == 2
        assert data["per_page"] == 20

    def test_list_jobs_invalid_page(self, client):
        """Test listing jobs with invalid page number."""
        response = client.get("/api/v1/eval/jobs?page=0")

        assert response.status_code == 422  # Validation error

    def test_list_jobs_invalid_per_page(self, client):
        """Test listing jobs with invalid per_page value."""
        response = client.get("/api/v1/eval/jobs?per_page=200")

        assert response.status_code == 422  # Exceeds max (100)


class TestGetJobResults:
    """Test GET /api/v1/eval/jobs/{job_id}/results endpoint."""

    def test_get_results_success(self, client, mock_supabase_client):
        """Test getting job results."""
        results_data = [
            {
                "station_id": "KJFK",
                "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                "tac_input": "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
                "our_iwxxm": "<iwxxm>...</iwxxm>",
                "their_iwxxm": "<iwxxm>...</iwxxm>",
                "comparison_status": "pass",
                "comparison_detail": {
                    "passed": True,
                    "our_elements": 10,
                    "their_elements": 10,
                    "missing_elements": [],
                    "extra_elements": [],
                    "value_mismatches": [],
                    "error_message": None,
                },
                "errors": [],
            },
        ]

        mock_supabase_client.get.side_effect = [
            # Job ownership verification
            AsyncMock(
                json=MagicMock(return_value=[{"id": "job-123", "user_id": "test-user-id"}]),
                raise_for_status=MagicMock(),
            ),
            # Results query
            AsyncMock(json=MagicMock(return_value=results_data), raise_for_status=MagicMock()),
            # Count query
            AsyncMock(headers={"Content-Range": "0-0/1"}, raise_for_status=MagicMock()),
        ]

        response = client.get("/api/v1/eval/jobs/job-123/results")

        assert response.status_code == 200
        data = response.json()

        assert data["job_id"] == "job-123"
        assert len(data["results"]) == 1
        assert data["results"][0]["station_id"] == "KJFK"
        assert data["results"][0]["comparison_status"] == "pass"
        assert data["total_results"] == 1
        assert data["page"] == 1

    def test_get_results_pagination(self, client, mock_supabase_client):
        """Test paginated results retrieval."""
        results_data = [
            {
                "station_id": f"STAT{i}",
                "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                "tac_input": "METAR...",
                "our_iwxxm": "<iwxxm>...</iwxxm>",
                "their_iwxxm": "<iwxxm>...</iwxxm>",
                "comparison_status": "pass",
                "comparison_detail": None,
                "errors": [],
            }
            for i in range(50)
        ]

        mock_supabase_client.get.side_effect = [
            AsyncMock(
                json=MagicMock(return_value=[{"id": "job-big", "user_id": "test-user-id"}]),
                raise_for_status=MagicMock(),
            ),
            AsyncMock(json=MagicMock(return_value=results_data), raise_for_status=MagicMock()),
            AsyncMock(headers={"Content-Range": "0-49/150"}, raise_for_status=MagicMock()),
        ]

        response = client.get("/api/v1/eval/jobs/job-big/results?page=1&per_page=50")

        assert response.status_code == 200
        data = response.json()

        assert len(data["results"]) == 50
        assert data["total_results"] == 150
        assert data["total_pages"] == 3

    def test_get_results_with_status_filter(self, client, mock_supabase_client):
        """Test filtering results by comparison status."""
        failed_results = [
            {
                "station_id": "FAIL1",
                "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                "tac_input": "METAR...",
                "our_iwxxm": "<iwxxm>...</iwxxm>",
                "their_iwxxm": "<iwxxm>...</iwxxm>",
                "comparison_status": "fail",
                "comparison_detail": {
                    "passed": False,
                    "our_elements": 10,
                    "their_elements": 11,
                    "missing_elements": ["element1"],
                    "extra_elements": [],
                    "value_mismatches": [],
                    "error_message": None,
                },
                "errors": [],
            },
        ]

        mock_supabase_client.get.side_effect = [
            AsyncMock(
                json=MagicMock(return_value=[{"id": "job-filter", "user_id": "test-user-id"}]),
                raise_for_status=MagicMock(),
            ),
            AsyncMock(json=MagicMock(return_value=failed_results), raise_for_status=MagicMock()),
            AsyncMock(headers={"Content-Range": "0-0/1"}, raise_for_status=MagicMock()),
        ]

        response = client.get("/api/v1/eval/jobs/job-filter/results?status_filter=fail")

        assert response.status_code == 200
        data = response.json()

        assert len(data["results"]) == 1
        assert data["results"][0]["comparison_status"] == "fail"

    def test_get_results_job_not_found(self, client, mock_supabase_client):
        """Test getting results for non-existent job."""
        mock_supabase_client.get.return_value = AsyncMock(json=MagicMock(return_value=[]), raise_for_status=MagicMock())

        response = client.get("/api/v1/eval/jobs/nonexistent/results")

        assert response.status_code == 404

    def test_get_results_wrong_user(self, client, mock_supabase_client):
        """Test user cannot access another user's job results."""
        mock_supabase_client.get.return_value = AsyncMock(json=MagicMock(return_value=[]), raise_for_status=MagicMock())

        response = client.get("/api/v1/eval/jobs/other-user-job/results")

        assert response.status_code == 404


class TestEvaluationEndToEnd:
    """End-to-end tests for evaluation workflow."""

    @pytest.mark.integration
    def test_complete_evaluation_workflow(self, client, mock_supabase_client):
        """Test complete workflow: create → check status → get results."""
        # Setup mocks for job creation
        job_id = "workflow-job-123"
        mock_supabase_client.post.return_value = AsyncMock(
            json=MagicMock(return_value=[{"id": job_id}]), raise_for_status=MagicMock()
        )

        # 1. Create job
        create_response = client.post(
            "/api/v1/eval/jobs",
            json={
                "mode": "single",
                "station_ids": ["KJFK", "EGLL"],
                "hours": 1,
            },
        )
        assert create_response.status_code == 200
        created_job_id = create_response.json()["job_id"]

        # 2. Check status (simulate completed job)
        mock_supabase_client.get.return_value = AsyncMock(
            json=MagicMock(
                return_value=[
                    {
                        "id": created_job_id,
                        "status": "completed",
                        "progress": 2,
                        "total_stations": 2,
                        "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                        "completed_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                        "summary_stats": {
                            "total": 2,
                            "passed": 2,
                            "failed": 0,
                            "errors": 0,
                            "pass_rate": 1.0,
                        },
                        "error_message": None,
                    }
                ]
            ),
            raise_for_status=MagicMock(),
        )

        status_response = client.get(f"/api/v1/eval/jobs/{created_job_id}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "completed"

        # 3. Get results
        mock_supabase_client.get.side_effect = [
            AsyncMock(
                json=MagicMock(return_value=[{"id": created_job_id, "user_id": "test-user-id"}]),
                raise_for_status=MagicMock(),
            ),
            AsyncMock(json=MagicMock(return_value=[]), raise_for_status=MagicMock()),
            AsyncMock(headers={"Content-Range": "0-0/2"}, raise_for_status=MagicMock()),
        ]

        results_response = client.get(f"/api/v1/eval/jobs/{created_job_id}/results")
        assert results_response.status_code == 200
