"""Part 1 of ``codelist_parser.py`` (line-cap split)."""

import logging

try:
    import requests
except ImportError:
    requests = None  # type: ignore[assignment,misc]

REQUESTS_AVAILABLE = requests is not None

logger = logging.getLogger(__name__)

if not REQUESTS_AVAILABLE:
    logger.warning("requests library not available, online validation disabled")
