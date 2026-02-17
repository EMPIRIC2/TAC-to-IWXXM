"""Schemas for evaluation endpoints."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class EvaluationMode(str, Enum):
    """Evaluation mode."""
    SINGLE = "single"
    RANDOM = "random"
    ALL = "all"


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ComparisonStatus(str, Enum):
    """Comparison result status."""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


class EvaluationRequest(BaseModel):
    """Request to create an evaluation job."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mode": "random",
                "sample_size": 50,
                "hours": 1.5,
                "large_airports_only": True,
                "scheduled_service_only": True,
            }
        }
    )

    mode: EvaluationMode = Field(
        ...,
        description="Evaluation mode: 'single' (specific stations), 'random' (random sample), or 'all' (all airports)"
    )
    station_ids: Optional[List[str]] = Field(
        default=None,
        description="Specific ICAO codes (required for 'single' mode)",
        examples=[["KJFK", "EGLL", "RJTT"]]
    )
    sample_size: Optional[int] = Field(
        default=100,
        description="Number of stations to sample (for 'random' mode)",
        ge=1,
        le=1000,
        examples=[50, 100, 200]
    )
    hours: float = Field(
        default=1.5,
        description="Hours back to search for METAR data",
        ge=0.5,
        le=24,
        examples=[1.5, 3.0, 6.0]
    )
    large_airports_only: bool = Field(
        default=True,
        description="Only evaluate large airports (IATA code available)"
    )
    scheduled_service_only: bool = Field(
        default=True,
        description="Only evaluate airports with scheduled service"
    )


class EvaluationJobResponse(BaseModel):
    """Response when creating an evaluation job."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job_550e8400e29b41d4a71662f7d6e6b1c0",
                "status": "pending",
                "station_count": 50,
                "created_at": "2026-02-10T14:30:45.123456+00:00",
            }
        }
    )

    job_id: str = Field(
        ...,
        description="Unique job identifier (UUID)",
        examples=["job_550e8400e29b41d4a71662f7d6e6b1c0"]
    )
    status: JobStatus = Field(
        ...,
        description="Current job status: pending, running, completed, failed"
    )
    station_count: int = Field(
        ...,
        description="Number of stations to evaluate",
        ge=0
    )
    created_at: datetime = Field(
        ...,
        description="Job creation timestamp"
    )


class ComparisonDetail(BaseModel):
    """Detailed comparison result between our and reference IWXXM."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "passed": True,
                "our_elements": 28,
                "their_elements": 28,
                "missing_elements": [],
                "extra_elements": [],
                "value_mismatches": [],
                "error_message": None,
            }
        }
    )

    passed: bool = Field(
        ...,
        description="Whether comparison passed"
    )
    our_elements: int = Field(
        ...,
        description="Number of elements in our converted IWXXM",
        ge=0
    )
    their_elements: int = Field(
        ...,
        description="Number of elements in reference IWXXM",
        ge=0
    )
    missing_elements: List[str] = Field(
        default_factory=list,
        description="Elements present in reference but missing from our output"
    )
    extra_elements: List[str] = Field(
        default_factory=list,
        description="Elements present in our output but not in reference"
    )
    value_mismatches: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Element values that differ between our and reference outputs"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if comparison failed"
    )


class EvaluationResultDetail(BaseModel):
    """Detailed result for a single station evaluation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "station_id": "KJFK",
                "timestamp": "2026-02-10T14:30:45.123456+00:00",
                "tac_input": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2",
                "our_iwxxm": "<?xml version='1.0'?>...",
                "their_iwxxm": "<?xml version='1.0'?>...",
                "comparison_status": "pass",
                "comparison": {
                    "passed": True,
                    "our_elements": 28,
                    "their_elements": 28,
                },
                "errors": [],
            }
        }
    )

    station_id: str = Field(
        ...,
        description="ICAO airport code",
        examples=["KJFK", "EGLL"]
    )
    timestamp: datetime = Field(
        ...,
        description="Evaluation timestamp"
    )
    tac_input: Optional[str] = Field(
        None,
        description="Original METAR TAC input"
    )
    our_iwxxm: Optional[str] = Field(
        None,
        description="Our converted IWXXM XML output"
    )
    their_iwxxm: Optional[str] = Field(
        None,
        description="Reference IWXXM XML for comparison"
    )
    comparison_status: ComparisonStatus = Field(
        ...,
        description="Comparison result: pass, fail, or error"
    )
    comparison: Optional[ComparisonDetail] = Field(
        None,
        description="Detailed comparison information"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Any errors during evaluation"
    )


class JobSummaryStats(BaseModel):
    """Summary statistics for a job."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 50,
                "passed": 45,
                "failed": 3,
                "errors": 2,
                "pass_rate": 0.9,
                "avg_elements_our": 28.5,
                "avg_elements_their": 26.8,
            }
        }
    )

    total: int = Field(
        ...,
        description="Total stations evaluated",
        ge=0
    )
    passed: int = Field(
        ...,
        description="Number of stations with passing comparison",
        ge=0
    )
    failed: int = Field(
        ...,
        description="Number of stations with failing comparison",
        ge=0
    )
    errors: int = Field(
        ...,
        description="Number of stations with evaluation errors",
        ge=0
    )
    pass_rate: float = Field(
        ...,
        description="Pass rate as decimal (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    avg_elements_our: Optional[float] = Field(
        None,
        description="Average number of elements in our converted IWXXM"
    )
    avg_elements_their: Optional[float] = Field(
        None,
        description="Average number of elements in reference IWXXM"
    )


class EvaluationJobStatus(BaseModel):
    """Current status of an evaluation job."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job_550e8400e29b41d4a71662f7d6e6b1c0",
                "status": "running",
                "progress": 25,
                "total": 50,
                "summary": None,
                "created_at": "2026-02-10T14:30:45.123456+00:00",
                "completed_at": None,
                "error_message": None,
            }
        }
    )

    job_id: str = Field(
        ...,
        description="Unique job identifier"
    )
    status: JobStatus = Field(
        ...,
        description="Current status: pending, running, completed, failed"
    )
    progress: int = Field(
        ...,
        description="Number of stations processed",
        ge=0
    )
    total: int = Field(
        ...,
        description="Total stations to process",
        ge=0
    )
    summary: Optional[JobSummaryStats] = Field(
        None,
        description="Summary statistics (populated when job completes)"
    )
    created_at: datetime = Field(
        ...,
        description="Job creation timestamp"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Job completion timestamp (if completed)"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if job failed"
    )


class EvaluationResultsResponse(BaseModel):
    """Response with paginated evaluation results."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job_550e8400e29b41d4a71662f7d6e6b1c0",
                "results": [
                    {
                        "station_id": "KJFK",
                        "timestamp": "2026-02-10T14:30:45.123456+00:00",
                        "comparison_status": "pass",
                    }
                ],
                "page": 1,
                "per_page": 20,
                "total_results": 50,
                "total_pages": 3,
            }
        }
    )

    job_id: str = Field(
        ...,
        description="Job identifier"
    )
    results: List[EvaluationResultDetail] = Field(
        ...,
        description="Results for this page"
    )
    page: int = Field(
        ...,
        description="Current page number (1-indexed)",
        ge=1
    )
    per_page: int = Field(
        ...,
        description="Results per page",
        ge=1
    )
    total_results: int = Field(
        ...,
        description="Total number of results",
        ge=0
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages",
        ge=0
    )


class JobListItem(BaseModel):
    """Summary item for job list."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job_550e8400e29b41d4a71662f7d6e6b1c0",
                "status": "completed",
                "station_count": 50,
                "progress": 50,
                "summary": {
                    "total": 50,
                    "passed": 45,
                    "failed": 3,
                    "errors": 2,
                    "pass_rate": 0.9,
                },
                "created_at": "2026-02-10T14:30:45.123456+00:00",
                "completed_at": "2026-02-10T15:45:30.123456+00:00",
            }
        }
    )

    job_id: str = Field(
        ...,
        description="Job identifier"
    )
    status: JobStatus = Field(
        ...,
        description="Job status"
    )
    station_count: int = Field(
        ...,
        description="Total stations in job",
        ge=0
    )
    progress: int = Field(
        ...,
        description="Stations processed so far",
        ge=0
    )
    summary: Optional[JobSummaryStats] = Field(
        None,
        description="Summary statistics (if completed)"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Completion timestamp (if completed)"
    )


class JobListResponse(BaseModel):
    """Response with list of jobs."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "jobs": [
                    {
                        "job_id": "job_550e8400e29b41d4a71662f7d6e6b1c0",
                        "status": "completed",
                        "station_count": 50,
                        "progress": 50,
                        "created_at": "2026-02-10T14:30:45.123456+00:00",
                    }
                ],
                "total": 15,
                "page": 1,
                "per_page": 20,
            }
        }
    )

    jobs: List[JobListItem] = Field(
        ...,
        description="Jobs on this page"
    )
    total: int = Field(
        ...,
        description="Total number of jobs",
        ge=0
    )
    page: int = Field(
        ...,
        description="Current page number (1-indexed)",
        ge=1
    )
    per_page: int = Field(
        ...,
        description="Jobs per page",
        ge=1
    )
