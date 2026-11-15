"""Maintainable TAC lint issue registry (package split)."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.issue_registry.api import ISSUES, by_code, catalog_entries, issue_from
from tac_validate.models import IssueSpec

__all__ = ["ISSUES", "IssueSpec", "by_code", "catalog_entries", "issue_from"]
