"""F8 worker entrypoint — poll loop → pipeline → store/quarantine."""

from __future__ import annotations

import logging
import signal
import time

from metar_worker.pipeline import process_job
from metar_worker.poller import fetch_jobs, safe_url_for_log
from metar_worker.settings import WorkerSettings
from metar_worker.store import PostgresStore, StoreClient, write_result

logger = logging.getLogger("metar_worker")

_shutdown = False
_seen_job_ids: set[str] = set()


def _handle_sigterm(_signum: int, _frame: object) -> None:
    global _shutdown
    _shutdown = True
    logger.info("SIGTERM received — finishing current poll then exiting")


def run_once(settings: WorkerSettings, store: StoreClient | None = None) -> int:
    """
    Fetch feed once and process all jobs.

    Returns
    -------
    int
        Number of jobs processed (skips already-seen ``job_id`` values in-process).
    """
    if not settings.ingest_poller_url:
        raise RuntimeError("INGEST_POLLER_URL is required")

    writer = store
    if writer is None:
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required")
        writer = PostgresStore(database_url=settings.database_url)

    jobs = fetch_jobs(settings.ingest_poller_url)
    logger.info(
        "fetched %s job(s) from %s",
        len(jobs),
        safe_url_for_log(settings.ingest_poller_url),
    )
    processed = 0
    for job in jobs:
        if job.job_id in _seen_job_ids:
            logger.debug("skip already-seen job_id=%s", job.job_id)
            continue
        result = process_job(
            job,
            profile=settings.ingest_profile,
            iwxxm_version=settings.iwxxm_version,
        )
        table = write_result(writer, job, result)
        _seen_job_ids.add(job.job_id)
        processed += 1
        logger.info(
            "job %s → %s ok=%s stage_failed=%s",
            job.job_id,
            table,
            result.ok,
            result.stage_failed,
        )
    return processed


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    signal.signal(signal.SIGTERM, _handle_sigterm)
    signal.signal(signal.SIGINT, _handle_sigterm)

    settings = WorkerSettings()
    if settings.once:
        run_once(settings)
        return

    while not _shutdown:
        try:
            run_once(settings)
        except Exception:
            logger.exception("poll cycle failed")
        for _ in range(int(max(settings.ingest_poll_interval_sec, 1))):
            if _shutdown:
                break
            time.sleep(1)


if __name__ == "__main__":
    main()
