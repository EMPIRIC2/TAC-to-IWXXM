"""Facade for ``codelist_parser.py`` (line-cap split)."""

from src.utilities.codelist_parser_part_1 import (
    REQUESTS_AVAILABLE,
    logger,
)
from src.utilities.codelist_parser_part_2 import (
    CodeListParser,
)
from src.utilities.codelist_parser_part_3 import (
    CodeListRegistry,
    _registry,
    get_codelist_parser,
    validate_xml_codelists,
)

__all__ = [
    "REQUESTS_AVAILABLE",
    "CodeListParser",
    "CodeListRegistry",
    "_registry",
    "get_codelist_parser",
    "logger",
    "validate_xml_codelists",
]
