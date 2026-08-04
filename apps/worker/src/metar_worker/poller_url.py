"""INGEST_POLLER_URL validation (no network deps — safe for ops CLI)."""

from __future__ import annotations

# Non-prod fixture used after DOKS cutover when no operational feed is configured.
# Keep in sync with docs/deploy.md / docs/env-contract.md / .env.example.
DEFAULT_FIXTURE_INGEST_POLLER_URL = (
    "https://raw.githubusercontent.com/EMPIRIC2/TAC-to-IWXXM/main/"
    "apps/worker/tests/fixtures/ingest_feed.json"
)

_PLACEHOLDER_MARKERS = (
    "REPLACE_ME",
    "CHANGEME",
    "TODO_SET",
    "YOUR_POLLER",
)


def validate_ingest_poller_url(url: str) -> str:
    """
    Return a stripped HTTPS poller URL, or raise ``ValueError``.

    Rejects empty values, non-HTTPS schemes, and cutover placeholders such as
    ``REPLACE_ME_INGEST_POLLER_URL`` so the worker fails closed with a clear
    message instead of looping on a bogus feed (EV-033 / F8 harden).

    Parameters
    ----------
    url :
        Raw ``INGEST_POLLER_URL`` value.

    Returns
    -------
    str
        Stripped URL suitable for ``fetch_jobs``.

    Raises
    ------
    ValueError
        If the URL is missing, a placeholder, or not ``https://``.
    """
    cleaned = (url or "").strip()
    if not cleaned:
        raise ValueError(
            "INGEST_POLLER_URL is required (HTTPS JSON feed). "
            f"Non-prod fixture: {DEFAULT_FIXTURE_INGEST_POLLER_URL}"
        )
    upper = cleaned.upper()
    for marker in _PLACEHOLDER_MARKERS:
        if marker.upper() in upper:
            raise ValueError(
                "INGEST_POLLER_URL looks like a cutover placeholder "
                f"({marker!r} in {cleaned!r}). Set a real https:// feed or the "
                f"fixture URL: {DEFAULT_FIXTURE_INGEST_POLLER_URL}. "
                "Scale metar-worker to 0 until the secret is fixed "
                "(scripts/deploy/doks_worker_poller_preflight.sh)."
            )
    if not cleaned.lower().startswith("https://"):
        raise ValueError(
            "INGEST_POLLER_URL must be an https:// URL (ADR-018 Q16=A); "
            f"got {cleaned!r}. Non-prod fixture: {DEFAULT_FIXTURE_INGEST_POLLER_URL}"
        )
    return cleaned


__all__ = [
    "DEFAULT_FIXTURE_INGEST_POLLER_URL",
    "validate_ingest_poller_url",
]
