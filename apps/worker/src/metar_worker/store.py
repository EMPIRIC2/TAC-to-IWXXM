"""Postgres store / quarantine writers via DATABASE_URL (F30 / ADR-033)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from metar_worker.pipeline import PipelineResult
from metar_worker.poller import IngestJob, safe_url_for_log

RESULTS_TABLE = "iwxxm_ingest_results"
QUARANTINE_TABLE = "iwxxm_ingest_quarantine"
_ALLOWED_TABLES = frozenset({RESULTS_TABLE, QUARANTINE_TABLE})


class StoreClient(Protocol):
    """Minimal insert protocol for tests and Postgres writers."""

    def insert(self, table: str, row: dict[str, Any]) -> None: ...


def _to_psycopg_url(url: str) -> str:
    """Normalize DATABASE_URL to SQLAlchemy psycopg v3 dialect."""
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql+asyncpg://")
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql+psycopg2://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


@dataclass(slots=True)
class PostgresStore:
    """
    SQLAlchemy writer targeting DigitalOcean Postgres (``DATABASE_URL``).

    Parameters
    ----------
    database_url :
        Postgres URL (``DATABASE_URL``). Asyncpg / psycopg2 schemes are rewritten.
    """

    database_url: str
    _engine: Engine | None = field(default=None, init=False, repr=False)

    def _get_engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                _to_psycopg_url(self.database_url),
                pool_pre_ping=True,
            )
        return self._engine

    def insert(self, table: str, row: dict[str, Any]) -> None:
        """
        Insert one ingest row into ``iwxxm_ingest_results`` or quarantine.

        Parameters
        ----------
        table :
            Target table name (must be an F8 ingest table).
        row :
            Column map produced by :func:`write_result`.

        Raises
        ------
        ValueError
            If ``table`` is not an allowed F8 ingest table.
        """
        if table not in _ALLOWED_TABLES:
            msg = f"refusing insert into unexpected table: {table}"
            raise ValueError(msg)

        payload = {
            "job_id": row["job_id"],
            "product": row["product"],
            "profile": row.get("profile", "annex3"),
            "source_url": row.get("source_url", ""),
            "tac_input": row.get("tac_input", ""),
            "iwxxm_xml": row.get("iwxxm_xml"),
            "issues": json.dumps(row.get("issues") or []),
            "stage_failed": row.get("stage_failed"),
        }
        stmt = text(
            f"""
            INSERT INTO {table} (
                job_id, product, profile, source_url, tac_input,
                iwxxm_xml, issues, stage_failed
            ) VALUES (
                :job_id, :product, :profile, :source_url, :tac_input,
                :iwxxm_xml, CAST(:issues AS jsonb), :stage_failed
            )
            """
        )
        with self._get_engine().begin() as conn:
            conn.execute(stmt, payload)

    def fetch_by_job_id(self, table: str, job_id: str) -> list[dict[str, Any]]:
        """
        Read rows for a job id (tests / smoke).

        Parameters
        ----------
        table :
            Target table name.
        job_id :
            Ingest job identifier.

        Returns
        -------
        list[dict[str, Any]]
            Matching rows as plain dicts.
        """
        if table not in _ALLOWED_TABLES:
            msg = f"refusing select from unexpected table: {table}"
            raise ValueError(msg)
        stmt = text(
            f"""
            SELECT job_id, product, profile, source_url, tac_input,
                   iwxxm_xml, issues, stage_failed
            FROM {table}
            WHERE job_id = :job_id
            ORDER BY created_at DESC
            """
        )
        with self._get_engine().connect() as conn:
            result = conn.execute(stmt, {"job_id": job_id})
            return [dict(row._mapping) for row in result]


def _base_row(job: IngestJob, result: PipelineResult) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "product": result.product,
        "profile": result.profile,
        "source_url": safe_url_for_log(job.source_url),
        "tac_input": job.tac,
        "issues": result.issues,
        "stage_failed": result.stage_failed,
    }


def write_result(store: StoreClient, job: IngestJob, result: PipelineResult) -> str:
    """
    Persist a pipeline outcome to store or quarantine.

    Returns
    -------
    str
        Target table name written.
    """
    row = _base_row(job, result)
    if result.ok and result.xml:
        row["iwxxm_xml"] = result.xml
        store.insert(RESULTS_TABLE, row)
        return RESULTS_TABLE

    row["iwxxm_xml"] = result.xml
    store.insert(QUARANTINE_TABLE, row)
    return QUARANTINE_TABLE


__all__ = [
    "QUARANTINE_TABLE",
    "RESULTS_TABLE",
    "PostgresStore",
    "StoreClient",
    "write_result",
]
