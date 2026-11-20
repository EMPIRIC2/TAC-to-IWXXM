"""Part 3 of ``schema_registry.py`` (line-cap split)."""

from .schema_registry_part_2 import SchemaRegistry

_registry_instance: SchemaRegistry | None = None


def get_schema_registry() -> SchemaRegistry:
    """
    Get singleton instance of SchemaRegistry.

    Returns
    -------
    object
        Global SchemaRegistry instance
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SchemaRegistry()
    return _registry_instance


def clear_registry_cache() -> None:
    """
    Clear all cached schema paths (useful for testing).
    """
    global _registry_instance
    if _registry_instance:
        _registry_instance._file_cache.clear()
        _registry_instance._version_cache.clear()
