"""Evaluation endpoints for METAR conversion validation."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

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
from ..services.evaluation_store import (
    create_job_in_db,
    get_job_for_user,
    list_jobs_for_user,
    list_results_for_job,
    save_result_to_db,
    update_job_status,
)
from ..utilities.conversion import ConversionError, convert_metar_tac
from ..utilities.station_sampler import StationSampler

router = APIRouter()


async def run_evaluation_job(job_id: str, request: EvaluationRequest) -> None:
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

        async with AviationWeatherClient() as client:
            metar_data = await client.fetch_metar_batch(stations, request.hours)

        evaluation_service = EvaluationService()
        results: list[Any] = []
        passed_count = 0
        failed_count = 0
        error_count = 0

        for station_id, (raw_tac, their_iwxxm) in metar_data.items():
            errors: list[str] = []
            our_iwxxm = None
            comparison = None
            comparison_status = ComparisonStatus.ERROR

            if raw_tac:
                try:
                    our_iwxxm = convert_metar_tac(raw_tac)
                except ConversionError as e:
                    errors.append(f"Conversion error: {e!s}")
                except Exception as e:
                    errors.append(f"Unexpected error: {e!s}")
            else:
                errors.append("No raw TAC data from API")

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
                    errors.append(f"Comparison error: {e!s}")
                    error_count += 1
            elif errors:
                error_count += 1

            result = EvaluationResultDetail(
                station_id=station_id,
                timestamp=datetime.now(UTC).replace(tzinfo=None),
                tac_input=raw_tac,
                our_iwxxm=our_iwxxm,
                their_iwxxm=their_iwxxm,
                comparison_status=comparison_status,
                comparison=comparison,
                errors=errors,
            )

            await save_result_to_db(job_id, result)
            results.append(result)
            await update_job_status(job_id, "running", progress=len(results))

        total = len(results)
        summary = JobSummaryStats(
            total=total,
            passed=passed_count,
            failed=failed_count,
            errors=error_count,
            pass_rate=passed_count / total if total > 0 else 0.0,
        )

        await update_job_status(job_id, "completed", progress=total, summary_stats=summary)

    except Exception as e:
        await update_job_status(job_id, "failed", error_message=str(e))


@router.post(
    "/jobs",
    response_model=EvaluationJobResponse,
    tags=["Evaluation"],
    responses={},
)
async def create_evaluation_job(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
) -> object:
    """Create a new evaluation job."""
    if request.mode == EvaluationMode.SINGLE and not request.station_ids:
        raise HTTPException(status_code=400, detail="station_ids required for single mode")

    if request.mode == EvaluationMode.SINGLE:
        station_count = len(request.station_ids or [])
    elif request.mode == EvaluationMode.RANDOM:
        station_count = request.sample_size or 100
    else:
        sampler = StationSampler()
        all_stations = sampler.get_all_major_airports(
            large_only=request.large_airports_only, scheduled_service_only=request.scheduled_service_only
        )
        station_count = len(all_stations)

    job_id = await create_job_in_db(
        user_id="anonymous",
        mode=request.mode.value,
        total_stations=station_count,
    )

    background_tasks.add_task(run_evaluation_job, job_id, request)

    return EvaluationJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        station_count=station_count,
        created_at=datetime.now(UTC).replace(tzinfo=None),
    )


@router.get(
    "/jobs/{job_id}",
    response_model=EvaluationJobStatus,
    tags=["Evaluation"],
    responses={},
)
async def get_job_status(
    job_id: str,
) -> object:
    """Get the status of an evaluation job."""
    job = await get_job_for_user(job_id, "anonymous")
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    summary = job.get("summary_stats")
    return EvaluationJobStatus(
        job_id=job["id"],
        status=JobStatus(job["status"]),
        progress=job["progress"],
        total=job["total_stations"],
        summary=JobSummaryStats(**summary) if summary else None,
        created_at=job["created_at"]
        if isinstance(job["created_at"], datetime)
        else datetime.fromisoformat(str(job["created_at"])),
        completed_at=(
            job["completed_at"]
            if isinstance(job.get("completed_at"), datetime)
            else datetime.fromisoformat(str(job["completed_at"]))
            if job.get("completed_at")
            else None
        ),
        error_message=job.get("error_message"),
    )


@router.get(
    "/jobs/{job_id}/results",
    response_model=EvaluationResultsResponse,
    tags=["Evaluation"],
    responses={},
)
async def get_job_results(
    job_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status_filter: ComparisonStatus | None = None,
) -> object:
    """Get evaluation results for a job (paginated)."""
    job = await get_job_for_user(job_id, "anonymous")
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    offset = (page - 1) * per_page
    results_data, total_count = await list_results_for_job(
        job_id,
        limit=per_page,
        offset=offset,
        status_filter=status_filter.value if status_filter else None,
    )

    results: list[Any] = []
    for row in results_data:
        created = row["created_at"]
        results.append(
            EvaluationResultDetail(
                station_id=row["station_id"],
                timestamp=created if isinstance(created, datetime) else datetime.fromisoformat(str(created)),
                tac_input=row.get("tac_input"),
                our_iwxxm=row.get("our_iwxxm"),
                their_iwxxm=row.get("their_iwxxm"),
                comparison_status=ComparisonStatus(row["comparison_status"]),
                comparison=ComparisonDetail(**row["comparison_detail"]) if row.get("comparison_detail") else None,
                errors=row.get("errors", []),
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
    responses={},
)
async def list_user_jobs(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100)) -> object:
    """List all evaluation jobs for the current user."""
    offset = (page - 1) * per_page
    jobs_data, total_count = await list_jobs_for_user("anonymous", per_page, offset)

    jobs: list[Any] = []
    for job in jobs_data:
        summary = job.get("summary_stats")
        created = job["created_at"]
        completed = job.get("completed_at")
        jobs.append(
            JobListItem(
                job_id=job["id"],
                status=JobStatus(job["status"]),
                station_count=job["station_count"],
                progress=job["progress"],
                summary=JobSummaryStats(**summary) if summary else None,
                created_at=created if isinstance(created, datetime) else datetime.fromisoformat(str(created)),
                completed_at=(
                    completed
                    if isinstance(completed, datetime)
                    else datetime.fromisoformat(str(completed))
                    if completed
                    else None
                ),
            )
        )

    return JobListResponse(jobs=jobs, total=total_count, page=page, per_page=per_page)
