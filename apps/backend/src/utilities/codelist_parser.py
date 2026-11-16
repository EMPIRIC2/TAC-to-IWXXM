"""Facade for ``codelist_parser.py`` (line-cap split)."""

from __future__ import annotations

import sys
import types
from typing import Any

from ..config.validation import get_validation_settings
from ..schemas.validation import (
    CodelistValidationResult,
    ValidationIssue,
    ValidationLayer,
    ValidationSeverity,
)

# Keep part_1 flag in sync for callers that import from there.
from . import codelist_parser_part_1 as _part1
from . import codelist_parser_part_3 as _part3
from .codelist_parser_part_1 import logger
from .codelist_parser_part_2 import CodeListParser
from .codelist_parser_part_3 import (
    CodeListRegistry,
    _registry,
    get_codelist_parser,
    validate_xml_codelists,
)
from .xml_types import lxml_etree as etree


def _load_requests() -> tuple[Any, bool]:
    """
    Internal helper ``_load_requests``.

    Returns
    -------
    object
        Return value.
    """
    # Use a statement import so builtins.__import__ monkeypatches (unit tests)
    # still observe ImportError; importlib.import_module bypasses that hook.
    try:
        import requests as requests_mod

        return requests_mod, True
    except ImportError:
        return None, False


requests, REQUESTS_AVAILABLE = _load_requests()

_part1.REQUESTS_AVAILABLE = REQUESTS_AVAILABLE


_ORIG: dict[str, object] = {}


class _CodelistParserModule(types.ModuleType):
    """Keep facade globals patched by tests in sync with split parts."""

    def __setattr__(self, name: str, value: object) -> None:
        """
        Internal helper ``__setattr__``.

        Parameters
        ----------
        name : object
            Argument ``name``.
        value : object
            Argument ``value``.
        """
        if name == "_registry":
            _part3._registry = value  # type: ignore[attr-defined]
        elif name == "REQUESTS_AVAILABLE":
            _part1.REQUESTS_AVAILABLE = value  # type: ignore[attr-defined]
        elif name == "CodeListParser":
            _part3.CodeListParser = value  # type: ignore[attr-defined]
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        """
        Internal helper ``__delattr__``.

        Parameters
        ----------
        name : object
            Argument ``name``.
        """
        if name in _ORIG and hasattr(_part1, name):
            setattr(_part1, name, _ORIG[name])
        if name in _ORIG and hasattr(_part3, name):
            setattr(_part3, name, _ORIG[name])
        super().__delattr__(name)


sys.modules[__name__].__class__ = _CodelistParserModule

__all__ = [
    "REQUESTS_AVAILABLE",
    "CodeListParser",
    "CodeListRegistry",
    "CodelistValidationResult",
    "ValidationIssue",
    "ValidationLayer",
    "ValidationSeverity",
    "_registry",
    "etree",
    "get_codelist_parser",
    "get_validation_settings",
    "logger",
    "requests",
    "validate_xml_codelists",
]
