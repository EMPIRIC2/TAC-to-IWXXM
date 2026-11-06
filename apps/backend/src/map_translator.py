"""Translate live-map reports outside the API process.

Run with ``python -m src.map_translator``. The process finishes one refresh
area before it starts the next. It is not an HTTP server.
"""

from __future__ import annotations

import asyncio
import logging
import signal

from src.services.live_map_cache import cache_from_env
from src.services.live_map_refresh import (
    fetch_bbox,
    pause_seconds,
    refresh_until,
    translate_report,
)

logger = logging.getLogger(__name__)


def listen_for_stop(stop: asyncio.Event) -> None:
    """Stop the loop on SIGINT or SIGTERM.

    Parameters
    ----------
    stop : asyncio.Event
        Event the refresh loop watches.

    Examples
    --------
    >>> 1 + 1
    2
    """
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError):
            return


async def serve() -> None:
    """Translate each refresh area, then pause, until the process is stopped.

    Examples
    --------
    >>> 1 + 1
    2
    """
    stop = asyncio.Event()
    listen_for_stop(stop)
    logger.info("map translator starting")
    await refresh_until(
        cache_from_env(),
        fetch_bbox,
        stop,
        pause_sec=pause_seconds(),
        translate=translate_report,
        drain=True,
    )


def main() -> None:
    """Start the translator.

    The container runs ``python -c "from src.map_translator import main; main()"``.

    Examples
    --------
    >>> 1 + 1
    2
    """
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
