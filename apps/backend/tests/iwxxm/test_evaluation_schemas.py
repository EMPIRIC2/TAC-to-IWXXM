"""Tests for evaluation schemas."""

from datetime import datetime

import pytest

from src.schemas.evaluation import (
    ComparisonDetail,
    ComparisonStatus,
    EvaluationJobResponse,
    EvaluationJobStatus,
    EvaluationMode,
    EvaluationRequest,
    EvaluationResultDetail,
    EvaluationResultsResponse,
    JobListItem,
    JobListResponse,
    JobStatus,
    JobSummaryStats,
)


@pytest.mark.unit
class TestEvaluationSchemas:
    """Test evaluation schemas and enums."""

    def test_evaluation_mode_enum(self):
        """Test EvaluationMode enum values."""
        assert EvaluationMode.SINGLE.value == "single"
        assert EvaluationMode.RANDOM.value == "random"
        assert EvaluationMode.ALL.value == "all"
        assert len(EvaluationMode) == 3

    def test_job_status_enum(self):
        """Test JobStatus enum values."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert len(JobStatus) == 4

    def test_comparison_status_enum(self):
        """Test ComparisonStatus enum values."""
        assert ComparisonStatus.PASS.value == "pass"
        assert ComparisonStatus.FAIL.value == "fail"
        assert ComparisonStatus.ERROR.value == "error"
        assert len(ComparisonStatus) == 3

    def test_evaluation_request_creation(self):
        """Test creating EvaluationRequest."""
        request = EvaluationRequest(mode=EvaluationMode.SINGLE, station_ids=["KJFK", "KLAX"], hours=1.5)

        assert request.mode == EvaluationMode.SINGLE
        assert request.station_ids == ["KJFK", "KLAX"]
        assert request.hours == 1.5
        assert request.large_airports_only is True
        assert request.scheduled_service_only is True

    def test_evaluation_request_defaults(self):
        """Test EvaluationRequest default values."""
        request = EvaluationRequest(mode=EvaluationMode.RANDOM)

        assert request.mode == EvaluationMode.RANDOM
        assert request.sample_size == 100
        assert request.hours == 1.5
        assert request.large_airports_only is True
        assert request.scheduled_service_only is True
        assert request.station_ids is None

    def test_evaluation_job_response_creation(self):
        """Test creating EvaluationJobResponse."""
        now = datetime.utcnow()
        response = EvaluationJobResponse(
            job_id="test-job-123", status=JobStatus.PENDING, station_count=10, created_at=now
        )

        assert response.job_id == "test-job-123"
        assert response.status == JobStatus.PENDING
        assert response.station_count == 10
        assert response.created_at == now

    def test_comparison_detail_creation(self):
        """Test creating ComparisonDetail."""
        detail = ComparisonDetail(
            passed=True,
            our_elements=50,
            their_elements=50,
            missing_elements=[],
            extra_elements=[],
            value_mismatches=[],
            error_message=None,
        )

        assert detail.passed is True
        assert detail.our_elements == 50
        assert detail.their_elements == 50

    def test_evaluation_result_detail_creation(self):
        """Test creating EvaluationResultDetail."""
        now = datetime.utcnow()
        result = EvaluationResultDetail(
            station_id="KJFK",
            timestamp=now,
            tac_input="METAR KJFK ...",
            our_iwxxm="<xml>our</xml>",
            their_iwxxm="<xml>their</xml>",
            comparison_status=ComparisonStatus.PASS,
            errors=[],
        )

        assert result.station_id == "KJFK"
        assert result.comparison_status == ComparisonStatus.PASS
        assert len(result.errors) == 0

    def test_job_summary_stats_creation(self):
        """Test creating JobSummaryStats."""
        stats = JobSummaryStats(total=100, passed=80, failed=15, errors=5, pass_rate=0.8)

        assert stats.total == 100
        assert stats.passed == 80
        assert stats.failed == 15
        assert stats.errors == 5
        assert stats.pass_rate == 0.8

    def test_evaluation_job_status_creation(self):
        """Test creating EvaluationJobStatus."""
        now = datetime.utcnow()
        stats = JobSummaryStats(total=10, passed=10, failed=0, errors=0, pass_rate=1.0)

        status = EvaluationJobStatus(
            job_id="job-123",
            status=JobStatus.COMPLETED,
            progress=10,
            total=10,
            summary=stats,
            created_at=now,
            completed_at=now,
        )

        assert status.job_id == "job-123"
        assert status.status == JobStatus.COMPLETED
        assert status.progress == 10
        assert status.summary.pass_rate == 1.0

    def test_evaluation_results_response_creation(self):
        """Test creating EvaluationResultsResponse."""
        results = []
        response = EvaluationResultsResponse(
            job_id="job-123", results=results, page=1, per_page=50, total_results=0, total_pages=0
        )

        assert response.job_id == "job-123"
        assert response.page == 1
        assert response.per_page == 50
        assert response.total_results == 0

    def test_job_list_item_creation(self):
        """Test creating JobListItem."""
        now = datetime.utcnow()
        item = JobListItem(job_id="job-123", status=JobStatus.RUNNING, station_count=50, progress=25, created_at=now)

        assert item.job_id == "job-123"
        assert item.status == JobStatus.RUNNING
        assert item.station_count == 50
        assert item.progress == 25

    def test_job_list_response_creation(self):
        """Test creating JobListResponse."""
        response = JobListResponse(jobs=[], total=0, page=1, per_page=20)

        assert response.total == 0
        assert response.page == 1
        assert response.per_page == 20
        assert len(response.jobs) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
