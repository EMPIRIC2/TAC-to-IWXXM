"""Optional Sentry init for the F8 worker (EV-052 / AC6)."""

from __future__ import annotations

import logging
import os

import sentry_sdk

logger = logging.getLogger(__name__)


def init_sentry(*, dsn: str | None = None) -> bool:
    """
    Initialize Sentry when ``SENTRY_DSN`` (or ``dsn``) is set.

    Returns
    -------
    bool
        ``True`` if initialized; ``False`` when DSN unset.
    """
    resolved = (dsn if dsn is not None else os.environ.get("SENTRY_DSN", "")).strip()
    if not resolved:
        logger.debug("Sentry disabled (SENTRY_DSN unset) for worker")
        return False
    sentry_sdk.init(
        dsn=resolved,
        traces_sample_rate=0.0,
        profiles_sample_rate=0.0,
        send_default_pii=False,
    )
    sentry_sdk.set_tag("service", "worker")
    logger.info("Sentry initialized for worker")
    return True
