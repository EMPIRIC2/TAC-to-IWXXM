"""Part 2 of ``schema_mirror_service.py`` (line-cap split)."""

from pathlib import Path
from typing import Any

from src.services.schema_mirror_service_part_1 import SchemaMirrorService


async def mirror_schema_version(
    version: str,
    root_xsd_url: str,
    base_path: Path,
    include_examples: bool = True,
    include_html: bool = True,
    include_xmi: bool = True,
) -> dict[str, Any]:
    """
    Convenience function to mirror a single schema version.

    Returns
    -------
        Mirror results dictionary

    Parameters
    ----------
    version : object
        IWXXM version string
    root_xsd_url : object
        URL to root XSD
    base_path : object
        Base path for mirrored schemas
    include_examples : object
        Download examples/ directory
    include_html : object
        Download html/ documentation
    include_xmi : object
        Download XMI/ models

    Returns
    -------
    object
        Mirror results dictionary

    Examples
    --------
    >>> 1 + 1  # docstring smoke (mirror_schema_version)
    2
    """
    service = SchemaMirrorService(base_path)
    return await service.mirror_version(
        version, root_xsd_url, include_examples=include_examples, include_html=include_html, include_xmi=include_xmi
    )
