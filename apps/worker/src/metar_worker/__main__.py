"""F8 worker entrypoint — poll loop → pipeline → store/quarantine."""

from __future__ import annotations

import logging
import signal
import time

from metar_worker.pipeline import process_job
from metar_worker.poller import fetch_jobs
from metar_worker.settings import WorkerSettings
from metar_worker.store import SupabaseRestStore, write_result

logger = logging.getLogger("metar_worker")

_shutdown = False


def _handle_sigterm(_signum: int, _frame: object) -> None:
    global _shutdown
    _shutdown = True
    logger.info("SIGTERM received — finishing current poll then exiting")


def run_once(settings: WorkerSettings, store: SupabaseRestStore | None = None) -> int:
    """
    Fetch feed once and process all jobs.

    Returns
    -------
    int
        Number of jobs processed.
    """
    if not settings.ingest_poller_url:
        raise RuntimeError("INGEST_POLLER_URL is required")

    writer = store
    if writer is None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required"
            )
        writer = SupabaseRestStore(
            base_url=settings.supabase_url,
            service_role_key=settings.supabase_service_role_key,
        )

    jobs = fetch_jobs(settings.ingest_poller_url)
    logger.info("fetched %s job(s) from %s", len(jobs), settings.ingest_poller_url)
    for job in jobs:
        result = process_job(
            job,
            profile=settings.ingest_profile,
            iwxxm_version=settings.iwxxm_version,
        )
        table = write_result(writer, job, result)
        logger.info(
            "job %s → %s ok=%s stage_failed=%s",
            job.job_id,
            table,
            result.ok,
            result.stage_failed,
        )
    return len(jobs)


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
