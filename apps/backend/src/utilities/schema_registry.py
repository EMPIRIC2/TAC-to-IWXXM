"""Facade for ``schema_registry.py`` (line-cap split)."""

from src.utilities.schema_registry_part_1 import (
    logger,
)
from src.utilities.schema_registry_part_2 import (
    SchemaRegistry,
)
from src.utilities.schema_registry_part_3 import (
    _registry_instance,
    clear_registry_cache,
    get_schema_registry,
)

__all__ = [
    "SchemaRegistry",
    "_registry_instance",
    "clear_registry_cache",
    "get_schema_registry",
    "logger",
]
