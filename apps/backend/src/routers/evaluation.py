"""Evaluation endpoints for METAR conversion validation."""

import os
from datetime import datetime
from typing import Any, Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from ..clients.aviation_weather_client import AviationWeatherClient
from ..schemas.evaluation import (
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
from ..services.evaluation_service import EvaluationService
from ..utilities.conversion import ConversionError, convert_metar_tac
from ..utilities.security import verify_supabase_token
from ..utilities.station_sampler import StationSampler

router = APIRouter()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


async def get_supabase_client():
    """Get httpx client with Supabase auth."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    return httpx.AsyncClient(base_url=SUPABASE_URL, headers=headers, timeout=30.0)


async def create_job_in_db(user_id: str, mode: str, total_stations: int) -> str:
    """Create evaluation job in database."""
    async with await get_supabase_client() as client:
        job_data = {
            "user_id": user_id,
            "status": "pending",
            "mode": mode,
            "station_count": 0,
            "progress": 0,
            "total_stations": total_stations,
        }

        response = await client.post("/rest/v1/evaluation_jobs", json=job_data)
        response.raise_for_status()

        result = response.json()
        return result[0]["id"] if isinstance(result, list) else result["id"]


async def update_job_status(
    job_id: str,
    status: str,
    progress: Optional[int] = None,
    summary_stats: Optional[dict] = None,
    error_message: Optional[str] = None,
):
    """Update job status in database."""
    async with await get_supabase_client() as client:
        update_data: dict[str, Any] = {"status": status}

        if progress is not None:
            update_data["progress"] = progress
        if summary_stats is not None:
            update_data["summary_stats"] = summary_stats
        if error_message is not None:
            update_data["error_message"] = error_message
        if status == "completed":
            update_data["completed_at"] = datetime.utcnow().isoformat()

        response = await client.patch(f"/rest/v1/evaluation_jobs?id=eq.{job_id}", json=update_data)
        response.raise_for_status()


async def save_result_to_db(job_id: str, result: EvaluationResultDetail):
    """Save evaluation result to database."""
    async with await get_supabase_client() as client:
        result_data = {
            "job_id": job_id,
            "station_id": result.station_id,
            "tac_input": result.tac_input,
            "our_iwxxm": result.our_iwxxm,
            "their_iwxxm": result.their_iwxxm,
            "comparison_status": result.comparison_status.value,
            "comparison_detail": result.comparison.dict() if result.comparison else None,
            "errors": result.errors,
        }

        response = await client.post("/rest/v1/evaluation_results", json=result_data)
        response.raise_for_status()


async def run_evaluation_job(job_id: str, request: EvaluationRequest):
    """Background task to run evaluation job."""
    try:
        await update_job_status(job_id, "running")

        if request.mode == EvaluationMode.SINGLE:
            if not request.station_ids:
                raise ValueError("station_ids required for single mode")
            stations = request.station_ids
        elif request.mode == EvaluationMode.RANDOM:
            sampler = StationSampler()
            stations = sampler.sample_random_stations(
                count=request.sample_size or 100,
                large_airports_only=request.large_airports_only,
                scheduled_service_only=request.scheduled_service_only,
            )
        else:  # ALL
            sampler = StationSampler()
            stations = sampler.get_all_major_airports(
                large_only=request.large_airports_only, scheduled_service_only=request.scheduled_service_only
            )

        # Fetch data from aviationweather.gov
        async with AviationWeatherClient() as client:
            metar_data = await client.fetch_metar_batch(stations, request.hours)

        # Process each station
        evaluation_service = EvaluationService()
        results = []
        passed_count = 0
        failed_count = 0
        error_count = 0

        for station_id, (raw_tac, their_iwxxm) in metar_data.items():
            errors = []
            our_iwxxm = None
            comparison = None
            comparison_status = ComparisonStatus.ERROR

            # Convert with our service
            if raw_tac:
                try:
                    our_iwxxm = convert_metar_tac(raw_tac)
                except ConversionError as e:
                    errors.append(f"Conversion error: {str(e)}")
                except Exception as e:
                    errors.append(f"Unexpected error: {str(e)}")
            else:
                errors.append("No raw TAC data from API")

            # Compare if we have both
            if our_iwxxm and their_iwxxm:
                try:
                    comp_result = evaluation_service.compare_iwxxm(our_iwxxm, their_iwxxm)
                    comparison = ComparisonDetail(
                        passed=comp_result.passed,
                        our_elements=comp_result.our_elements,
                        their_elements=comp_result.their_elements,
                        missing_elements=comp_result.missing_elements,
                        extra_elements=comp_result.extra_elements,
                        value_mismatches=comp_result.value_mismatches,
                        error_message=comp_result.error_message,
                    )
                    comparison_status = ComparisonStatus.PASS if comp_result.passed else ComparisonStatus.FAIL

                    if comp_result.passed:
                        passed_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    errors.append(f"Comparison error: {str(e)}")
                    error_count += 1
            elif errors:
                error_count += 1

            result = EvaluationResultDetail(
                station_id=station_id,
                timestamp=datetime.utcnow(),
                tac_input=raw_tac,
                our_iwxxm=our_iwxxm,
                their_iwxxm=their_iwxxm,
                comparison_status=comparison_status,
                comparison=comparison,
                errors=errors,
            )

            # Save incrementally
            await save_result_to_db(job_id, result)
            results.append(result)

            # Update progress
            await update_job_status(job_id, "running", progress=len(results))

        # Calculate summary stats
        total = len(results)
        summary = JobSummaryStats(
            total=total,
            passed=passed_count,
            failed=failed_count,
            errors=error_count,
            pass_rate=passed_count / total if total > 0 else 0.0,
        )

        await update_job_status(job_id, "completed", progress=total, summary_stats=summary.dict())

    except Exception as e:
        await update_job_status(job_id, "failed", error_message=str(e))


@router.post(
    "/jobs",
    response_model=EvaluationJobResponse,
    tags=["Evaluation"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
    },
)
async def create_evaluation_job(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(verify_supabase_token),
):
    """Create a new evaluation job.

    Modes:
    - single: Evaluate specific station_ids
    - random: Evaluate random sample of airports
    - all: Evaluate all major airports (500+)

    The job runs in the background. Poll the status endpoint to check progress.
    """
    # Validate request
    if request.mode == EvaluationMode.SINGLE and not request.station_ids:
        raise HTTPException(status_code=400, detail="station_ids required for single mode")

    if request.mode == EvaluationMode.SINGLE:
        station_count = len(request.station_ids or [])
    elif request.mode == EvaluationMode.RANDOM:
        station_count = request.sample_size or 100
    else:  # ALL
        sampler = StationSampler()
        all_stations = sampler.get_all_major_airports(
            large_only=request.large_airports_only, scheduled_service_only=request.scheduled_service_only
        )
        station_count = len(all_stations)

    # Create job in database
    job_id = await create_job_in_db(user_id=user["sub"], mode=request.mode.value, total_stations=station_count)

    # Start background task
    background_tasks.add_task(run_evaluation_job, job_id, request)

    return EvaluationJobResponse(
        job_id=job_id, status=JobStatus.PENDING, station_count=station_count, created_at=datetime.utcnow()
    )


@router.get(
    "/jobs/{job_id}",
    response_model=EvaluationJobStatus,
    tags=["Evaluation"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
    },
)
async def get_job_status(
    job_id: str,
    user: dict = Depends(verify_supabase_token),
):
    """Get the status of an evaluation job."""
    async with await get_supabase_client() as client:
        response = await client.get(f"/rest/v1/evaluation_jobs?id=eq.{job_id}&user_id=eq.{user['sub']}")
        response.raise_for_status()

        jobs = response.json()
        if not jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        job = jobs[0]

        return EvaluationJobStatus(
            job_id=job["id"],
            status=JobStatus(job["status"]),
            progress=job["progress"],
            total=job["total_stations"],
            summary=JobSummaryStats(**job["summary_stats"]) if job.get("summary_stats") else None,
            created_at=datetime.fromisoformat(job["created_at"]),
            completed_at=datetime.fromisoformat(job["completed_at"]) if job.get("completed_at") else None,
            error_message=job.get("error_message"),
        )


@router.get(
    "/jobs/{job_id}/results",
    response_model=EvaluationResultsResponse,
    tags=["Evaluation"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
    },
)
async def get_job_results(
    job_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status_filter: Optional[ComparisonStatus] = None,
    user: dict = Depends(verify_supabase_token),
):
    """Get evaluation results for a job (paginated)."""
    # Verify job ownership
    async with await get_supabase_client() as client:
        job_response = await client.get(f"/rest/v1/evaluation_jobs?id=eq.{job_id}&user_id=eq.{user['sub']}")
        job_response.raise_for_status()

        if not job_response.json():
            raise HTTPException(status_code=404, detail="Job not found")

        # Get results with pagination
        offset = (page - 1) * per_page
        query = f"/rest/v1/evaluation_results?job_id=eq.{job_id}&limit={per_page}&offset={offset}&order=created_at.asc"

        if status_filter:
            query += f"&comparison_status=eq.{status_filter.value}"

        results_response = await client.get(query)
        results_response.raise_for_status()

        results_data = results_response.json()

        # Get total count
        count_query = f"/rest/v1/evaluation_results?job_id=eq.{job_id}&select=count"
        if status_filter:
            count_query += f"&comparison_status=eq.{status_filter.value}"

        count_response = await client.get(count_query, headers={"Prefer": "count=exact"})
        total_count = int(count_response.headers.get("Content-Range", "0").split("/")[-1])

        # Parse results
        results = []
        for r in results_data:
            results.append(
                EvaluationResultDetail(
                    station_id=r["station_id"],
                    timestamp=datetime.fromisoformat(r["created_at"]),
                    tac_input=r.get("tac_input"),
                    our_iwxxm=r.get("our_iwxxm"),
                    their_iwxxm=r.get("their_iwxxm"),
                    comparison_status=ComparisonStatus(r["comparison_status"]),
                    comparison=ComparisonDetail(**r["comparison_detail"]) if r.get("comparison_detail") else None,
                    errors=r.get("errors", []),
                )
            )

        return EvaluationResultsResponse(
            job_id=job_id,
            results=results,
            page=page,
            per_page=per_page,
            total_results=total_count,
            total_pages=(total_count + per_page - 1) // per_page,
        )


@router.get(
    "/jobs",
    response_model=JobListResponse,
    tags=["Evaluation"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
    },
)
async def list_user_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: dict = Depends(verify_supabase_token),
):
    """List all evaluation jobs for the current user."""
    async with await get_supabase_client() as client:
        offset = (page - 1) * per_page
        response = await client.get(
            f"/rest/v1/evaluation_jobs?user_id=eq.{user['sub']}&limit={per_page}&offset={offset}&order=created_at.desc"
        )
        response.raise_for_status()

        jobs_data = response.json()

        # Get total count
        count_response = await client.get(
            f"/rest/v1/evaluation_jobs?user_id=eq.{user['sub']}&select=count", headers={"Prefer": "count=exact"}
        )
        total_count = int(count_response.headers.get("Content-Range", "0").split("/")[-1])

        jobs = []
        for job in jobs_data:
            jobs.append(
                JobListItem(
                    job_id=job["id"],
                    status=JobStatus(job["status"]),
                    station_count=job["station_count"],
                    progress=job["progress"],
                    summary=JobSummaryStats(**job["summary_stats"]) if job.get("summary_stats") else None,
                    created_at=datetime.fromisoformat(job["created_at"]),
                    completed_at=datetime.fromisoformat(job["completed_at"]) if job.get("completed_at") else None,
                )
            )

        return JobListResponse(jobs=jobs, total=total_count, page=page, per_page=per_page)
