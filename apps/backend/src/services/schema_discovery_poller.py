"""Facade for ``schema_discovery_poller.py`` (line-cap split)."""

from src.services.schema_discovery_poller_part_1 import (
    RC_PATTERN,
    VERSION_PATTERN,
    WMO_SCHEMA_DIRECTORIES,
    VersionCallback,
    extract_version_from_url,
    logger,
)
from src.services.schema_discovery_poller_part_2 import (
    SchemaDiscoveryPoller,
)
from src.services.schema_discovery_poller_part_3 import (
    discover_schemas,
    discover_schemas_with_retry,
)

__all__ = [
    "RC_PATTERN",
    "VERSION_PATTERN",
    "WMO_SCHEMA_DIRECTORIES",
    "SchemaDiscoveryPoller",
    "VersionCallback",
    "discover_schemas",
    "discover_schemas_with_retry",
    "extract_version_from_url",
    "logger",
]
