"""Generated IWXXM pydantic models (xsdata / ADR-027).

Regenerate with ``make codegen-iwxxm-xsd``. Prefer leaf imports via
``metar_shared.iwxxm_xsd.adapt.import_version_leaf`` — version package
``__init__`` modules may hit GML circular imports.
"""

from metar_shared.iwxxm_xsd.adapt import (
    available_versions,
    import_version_leaf,
    package_name,
    pydantic_to_msgspec,
    pydantic_to_rust_hint,
    version_package,
)

__all__ = [
    "available_versions",
    "import_version_leaf",
    "package_name",
    "pydantic_to_msgspec",
    "pydantic_to_rust_hint",
    "version_package",
]
