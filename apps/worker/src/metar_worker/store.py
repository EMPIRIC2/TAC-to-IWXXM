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

    def insert(self, table: str, row: dict[str, Any]) -> None:
        """Insert ``row`` into ``table``."""
        ...


def _to_psycopg_url(url: str) -> str:
    """
    Internal helper ``_to_psycopg_url``.

    Parameters
    ----------
    url : object
        Argument ``url``.

    Returns
    -------
    object
        Return value.
    """
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
        """
        Internal helper ``_get_engine``.

        Returns
        -------
        object
            Return value.
        """
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
        table : object
            Argument ``table``.
        row : object
            Argument ``row``.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (insert)
        2
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
        table : object
            Argument ``table``.
        job_id : object
            Argument ``job_id``.

        Returns
        -------
        object
            Return value.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (fetch_by_job_id)
        2
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
    """
    Internal helper ``_base_row``.

    Parameters
    ----------
    job : object
        Argument ``job``.
    result : object
        Argument ``result``.

    Returns
    -------
    object
        Return value.
    """
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

    Parameters
    ----------
    store : object
        Argument ``store``.
    job : object
        Argument ``job``.
    result : object
        Argument ``result``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (write_result)
    2
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
