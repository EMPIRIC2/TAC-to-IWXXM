"""Part 1 of ``codelist_parser.py`` (line-cap split)."""

import logging

try:
    import requests
except ImportError:  # pragma: no cover - requests is a workspace dependency
    requests = None  # type: ignore[assignment,misc]

REQUESTS_AVAILABLE = requests is not None

logger = logging.getLogger(__name__)

if not REQUESTS_AVAILABLE:  # pragma: no cover - flag flipped via facade in tests
    logger.warning("requests library not available, online validation disabled")
