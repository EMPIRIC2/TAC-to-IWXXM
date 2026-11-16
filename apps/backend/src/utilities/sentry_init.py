"""Optional Sentry init for API / worker (EV-052 / AC6).

When ``SENTRY_DSN`` is unset, init is a no-op. Sample rates stay low for the
Sentry Developer free tier (errors-first; traces/profiles off or ≤0.05).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import sentry_sdk

logger = logging.getLogger(__name__)

DEFAULT_TRACES_SAMPLE_RATE = 0.0
DEFAULT_PROFILES_SAMPLE_RATE = 0.0


def init_sentry(
    *,
    service_name: str,
    dsn: str | None = None,
    traces_sample_rate: float | None = None,
    profiles_sample_rate: float | None = None,
) -> bool:
    """
    Initialize Sentry when a DSN is available.

    Parameters
    ----------
    service_name : str
        Logical service tag (e.g. ``backend``, ``worker``).
    dsn : str | None
        Explicit DSN; otherwise ``SENTRY_DSN`` env.
    traces_sample_rate : float | None
        Override traces sample rate (default 0.0).
    profiles_sample_rate : float | None
        Override profiles sample rate (default 0.0).

    Returns
    -------
    bool
        ``True`` if ``sentry_sdk.init`` ran; ``False`` when DSN unset.
    """
    resolved = (dsn if dsn is not None else os.environ.get("SENTRY_DSN", "")).strip()
    if not resolved:
        logger.debug("Sentry disabled (SENTRY_DSN unset) for %s", service_name)
        return False

    traces = DEFAULT_TRACES_SAMPLE_RATE if traces_sample_rate is None else traces_sample_rate
    profiles = DEFAULT_PROFILES_SAMPLE_RATE if profiles_sample_rate is None else profiles_sample_rate
    # Clamp to free-tier-friendly ceiling (D-S061-sentry-sample).
    traces = min(max(traces, 0.0), 0.05)
    profiles = min(max(profiles, 0.0), 0.05)

    init_kwargs: dict[str, Any] = {
        "dsn": resolved,
        "traces_sample_rate": traces,
        "profiles_sample_rate": profiles,
        "send_default_pii": False,
    }
    if service_name == "backend":
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        init_kwargs["integrations"] = [
            StarletteIntegration(),
            FastApiIntegration(),
        ]

    sentry_sdk.init(**init_kwargs)
    sentry_sdk.set_tag("service", service_name)
    logger.info("Sentry initialized for %s", service_name)
    return True


__all__ = ["init_sentry"]
