"""Direct Postgres persistence for evaluation jobs (server-side, no service role key)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from ..schemas.evaluation import EvaluationResultDetail, JobSummaryStats
from .database import get_db_session


async def create_job_in_db(user_id: str, mode: str, total_stations: int) -> str:
    """Insert a pending evaluation job and return its id."""
    async with get_db_session() as session:
        result = await session.execute(
            text(
                """
                INSERT INTO evaluation_jobs (
                    user_id, status, mode, station_count, progress, total_stations
                )
                VALUES (:user_id, 'pending', :mode, 0, 0, :total_stations)
                RETURNING id::text
                """
            ),
            {"user_id": user_id, "mode": mode, "total_stations": total_stations},
        )
        row = result.fetchone()
        await session.commit()
        if row is None:
            raise RuntimeError("Failed to create evaluation job")
        return str(row[0])


async def update_job_status(
    job_id: str,
    status: str,
    progress: int | None = None,
    summary_stats: JobSummaryStats | dict[str, Any] | None = None,
    error_message: str | None = None,
) -> None:
    """Update evaluation job status and optional fields."""
    update_data: dict[str, Any] = {"job_id": job_id, "status": status}
    set_clauses = ["status = :status", "updated_at = NOW()"]

    if progress is not None:
        set_clauses.append("progress = :progress")
        update_data["progress"] = progress
    if summary_stats is not None:
        payload = summary_stats.model_dump() if isinstance(summary_stats, JobSummaryStats) else summary_stats
        set_clauses.append("summary_stats = CAST(:summary_stats AS jsonb)")
        update_data["summary_stats"] = json.dumps(payload)
    if error_message is not None:
        set_clauses.append("error_message = :error_message")
        update_data["error_message"] = error_message
    if status == "completed":
        set_clauses.append("completed_at = NOW()")

    sql = f"UPDATE evaluation_jobs SET {', '.join(set_clauses)} WHERE id = CAST(:job_id AS uuid)"
    async with get_db_session() as session:
        await session.execute(text(sql), update_data)
        await session.commit()


async def save_result_to_db(job_id: str, result: EvaluationResultDetail) -> None:
    """Persist one evaluation result row."""
    comparison_detail = result.comparison.dict() if result.comparison else None
    async with get_db_session() as session:
        await session.execute(
            text(
                """
                INSERT INTO evaluation_results (
                    job_id, station_id, tac_input, our_iwxxm, their_iwxxm,
                    comparison_status, comparison_detail, errors
                )
                VALUES (
                    CAST(:job_id AS uuid), :station_id, :tac_input, :our_iwxxm, :their_iwxxm,
                    :comparison_status, CAST(:comparison_detail AS jsonb), CAST(:errors AS jsonb)
                )
                """
            ),
            {
                "job_id": job_id,
                "station_id": result.station_id,
                "tac_input": result.tac_input,
                "our_iwxxm": result.our_iwxxm,
                "their_iwxxm": result.their_iwxxm,
                "comparison_status": result.comparison_status.value,
                "comparison_detail": json.dumps(comparison_detail) if comparison_detail else None,
                "errors": json.dumps(result.errors),
            },
        )
        await session.commit()


async def get_job_for_user(job_id: str, user_id: str) -> dict[str, Any] | None:
    """Fetch a job row when owned by ``user_id``."""
    async with get_db_session() as session:
        result = await session.execute(
            text(
                """
                SELECT id::text, status, progress, total_stations, summary_stats,
                       created_at, completed_at, error_message
                FROM evaluation_jobs
                WHERE id = CAST(:job_id AS uuid) AND user_id = CAST(:user_id AS uuid)
                """
            ),
            {"job_id": job_id, "user_id": user_id},
        )
        row = result.mappings().first()
        return dict(row) if row else None


async def list_jobs_for_user(user_id: str, limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
    """Return paginated jobs and total count for a user."""
    async with get_db_session() as session:
        rows = await session.execute(
            text(
                """
                SELECT id::text, status, station_count, progress, summary_stats,
                       created_at, completed_at
                FROM evaluation_jobs
                WHERE user_id = CAST(:user_id AS uuid)
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            {"user_id": user_id, "limit": limit, "offset": offset},
        )
        count_result = await session.execute(
            text("SELECT COUNT(*) FROM evaluation_jobs WHERE user_id = CAST(:user_id AS uuid)"),
            {"user_id": user_id},
        )
        total = int(count_result.scalar_one())
        return [dict(row) for row in rows.mappings()], total


async def list_results_for_job(
    job_id: str,
    *,
    limit: int,
    offset: int,
    status_filter: str | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Return paginated evaluation results for a job."""
    filters = "job_id = CAST(:job_id AS uuid)"
    params: dict[str, Any] = {"job_id": job_id, "limit": limit, "offset": offset}
    if status_filter:
        filters += " AND comparison_status = :status_filter"
        params["status_filter"] = status_filter

    async with get_db_session() as session:
        rows = await session.execute(
            text(
                f"""
                SELECT station_id, tac_input, our_iwxxm, their_iwxxm, comparison_status,
                       comparison_detail, errors, created_at
                FROM evaluation_results
                WHERE {filters}
                ORDER BY created_at ASC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        )
        count_result = await session.execute(
            text(f"SELECT COUNT(*) FROM evaluation_results WHERE {filters}"),
            {k: v for k, v in params.items() if k not in ("limit", "offset")},
        )
        total = int(count_result.scalar_one())
        return [dict(row) for row in rows.mappings()], total
