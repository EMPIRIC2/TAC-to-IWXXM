"""Maintainable TAC lint issue registry (package split)."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.issue_registry.api import (
    ISSUES,
    _strip_unresolved_braces,
    by_code,
    catalog_entries,
    format_operator_message,
    issue_from,
)
from tac_validate.issue_registry.spec import IssueSpec

__all__ = [
    "ISSUES",
    "IssueSpec",
    "_strip_unresolved_braces",
    "by_code",
    "catalog_entries",
    "format_operator_message",
    "issue_from",
]
