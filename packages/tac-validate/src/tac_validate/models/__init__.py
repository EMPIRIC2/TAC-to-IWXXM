"""msgspec models for TAC lint [Corpus: product §F12]."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.models.issue_spec import IssueSpec
from tac_validate.models.lint import Fix, Issue, LintReport

__all__ = ["Fix", "Issue", "IssueSpec", "LintReport"]
