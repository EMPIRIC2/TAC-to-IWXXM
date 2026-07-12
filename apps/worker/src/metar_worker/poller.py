"""HTTPS / object-prefix ingest poller (Q16=A / ADR-018)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True, slots=True)
class IngestJob:
    """
    One TAC report queued from a poller fetch.

    Parameters
    ----------
    job_id :
        Stable id from the feed (or derived).
    product :
        F6 product id (``METAR``, ``TAF``, …).
    tac :
        Single-report TAC text.
    source_url :
        Feed URL that produced this job.
    """

    job_id: str
    product: str
    tac: str
    source_url: str


def _normalize_items(payload: Any, *, source_url: str) -> list[IngestJob]:
    if isinstance(payload, dict) and "items" in payload:
        raw_items = payload["items"]
    elif isinstance(payload, list):
        raw_items = payload
    else:
        raise ValueError("poller feed must be a JSON list or {items: [...]}")

    if not isinstance(raw_items, list):
        raise ValueError("poller feed items must be a list")

    jobs: list[IngestJob] = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, dict):
            raise ValueError(f"feed item {index} must be an object")
        tac = str(item.get("tac") or "").strip()
        product = str(item.get("product") or "METAR").strip().upper()
        job_id = str(item.get("id") or f"job-{index + 1}")
        if not tac:
            raise ValueError(f"feed item {job_id!r} missing tac")
        jobs.append(
            IngestJob(
                job_id=job_id,
                product=product,
                tac=tac,
                source_url=source_url,
            )
        )
    return jobs


def fetch_jobs(
    url: str,
    *,
    client: httpx.Client | None = None,
    timeout: float = 30.0,
) -> list[IngestJob]:
    """
    Fetch an HTTPS JSON feed and return ingest jobs.

    Parameters
    ----------
    url :
        ``INGEST_POLLER_URL`` — HTTPS feed (fixture or object-prefix listing).
    client :
        Optional shared ``httpx.Client`` (tests inject mocked transport).
    timeout :
        Request timeout in seconds.

    Returns
    -------
    list[IngestJob]
        Zero or more jobs from the feed.
    """
    own_client = client is None
    http = client or httpx.Client(timeout=timeout)
    try:
        response = http.get(url)
        response.raise_for_status()
        payload = response.json()
        return _normalize_items(payload, source_url=url)
    finally:
        if own_client:
            http.close()


__all__ = ["IngestJob", "fetch_jobs"]
