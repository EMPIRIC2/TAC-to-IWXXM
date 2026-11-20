"""Part 3 of ``schema_discovery_poller.py`` (line-cap split)."""

from typing import Any

from .schema_discovery_poller_part_2 import SchemaDiscoveryPoller


async def discover_schemas() -> dict[str, Any]:
    """
    Convenience function to run a single discovery poll.

    Returns
    -------
    object
        Discovery results with new stable and RC versions
    """
    poller = SchemaDiscoveryPoller()
    return await poller.poll_once()


async def discover_schemas_with_retry(max_retries: int = 3, retry_delay: int = 60) -> dict[str, Any] | None:
    """
    Convenience function to run discovery with retry logic.

    Returns
    -------
        Discovery results

    Parameters
    ----------
    max_retries : object
        Maximum retry attempts
    retry_delay : object
        Delay between retries in seconds

    Returns
    -------
    object
        Discovery results
    """
    poller = SchemaDiscoveryPoller()
    return await poller.poll_with_retry(max_retries, retry_delay)
