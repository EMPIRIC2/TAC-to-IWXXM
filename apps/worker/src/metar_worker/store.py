"""Supabase store / quarantine writers (service-role JWT — Q20=C)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from metar_worker.pipeline import PipelineResult
from metar_worker.poller import IngestJob

RESULTS_TABLE = "iwxxm_ingest_results"
QUARANTINE_TABLE = "iwxxm_ingest_quarantine"


class StoreClient(Protocol):
    """Minimal PostgREST insert protocol for tests."""

    def insert(self, table: str, row: dict[str, Any]) -> None: ...


@dataclass(slots=True)
class SupabaseRestStore:
    """
    PostgREST writer using the service-role key.

    Parameters
    ----------
    base_url :
        Supabase project URL (``SUPABASE_URL``).
    service_role_key :
        Service-role JWT (``SUPABASE_SERVICE_ROLE_KEY``).
    client :
        Optional shared httpx client.
    """

    base_url: str
    service_role_key: str
    client: httpx.Client | None = None

    def insert(self, table: str, row: dict[str, Any]) -> None:
        own = self.client is None
        http = self.client or httpx.Client(timeout=30.0)
        try:
            url = f"{self.base_url.rstrip('/')}/rest/v1/{table}"
            response = http.post(
                url,
                headers={
                    "apikey": self.service_role_key,
                    "Authorization": f"Bearer {self.service_role_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                json=row,
            )
            response.raise_for_status()
        finally:
            if own:
                http.close()


def _base_row(job: IngestJob, result: PipelineResult) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "product": result.product,
        "profile": result.profile,
        "source_url": job.source_url,
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
    "StoreClient",
    "SupabaseRestStore",
    "write_result",
]
