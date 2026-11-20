"""lint_profile_catalog package split."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.lint_profile_catalog.load import (
    _delta,
    _mapping,
    _object_list,
    _required_str,
    _specs_from_document,
    _string_list,
    _validate_inherits,
    lint_profile_spec,
    load_lint_profiles,
    profile_inherit_chain,
)
from tac_validate.lint_profile_catalog.models import (
    LintDelta,
    LintProfileSpec,
    canonical_lint_profile_id,
)
from tac_validate.lint_profile_catalog.resolve import (
    MAX_INHERIT_DEPTH,
    _suppressed,
    apply_profile_deltas,
    resolved_lint_profile,
)

__all__ = [
    "MAX_INHERIT_DEPTH",
    "LintDelta",
    "LintProfileSpec",
    "_delta",
    "_mapping",
    "_object_list",
    "_required_str",
    "_specs_from_document",
    "_string_list",
    "_suppressed",
    "_validate_inherits",
    "apply_profile_deltas",
    "canonical_lint_profile_id",
    "lint_profile_spec",
    "load_lint_profiles",
    "profile_inherit_chain",
    "resolved_lint_profile",
]
