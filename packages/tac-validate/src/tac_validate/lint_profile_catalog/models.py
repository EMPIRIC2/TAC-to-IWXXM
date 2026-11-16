"""Load the shared lint-profile catalog.

One YAML row per semantic profile. Country differences are deltas in that
file, not a new Python module. [Corpus: domain-profiles] [Corpus: product §F36]
"""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from tac_validate.lint_profile_ids import canonical_lint_profile_id
from tac_validate.models import Issue, LintReport

_CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "lint_profiles.yaml"
_TOKEN_RE = re.compile(r"'([^']+)'")
MAX_INHERIT_DEPTH = 8


@dataclass(frozen=True, slots=True)
class LintDelta:
    """
    One recorded suppression against the engine rule pack.

    Parameters
    ----------
    rule_id : str
        Stable id for this country difference.
    products : frozenset[str]
        Products the suppression applies to.
    suppress_codes : frozenset[str]
        Engine issue codes to drop when the token matches.
    token_pattern : re.Pattern[str]
        Compiled match against the quoted token in the issue message.
    """

    rule_id: str
    products: frozenset[str]
    suppress_codes: frozenset[str]
    token_pattern: re.Pattern[str]


@dataclass(frozen=True, slots=True)
class LintProfileSpec:
    """
    Lint behavior for one semantic profile.

    Parameters
    ----------
    profile_id : str
        Profile id accepted by ``lint``.
    engine : str
        Existing rule pack that runs before deltas.
    products : frozenset[str]
        Products this profile may lint.
    differs : bool
        True when the profile is not identical to its engine.
    deltas : tuple[LintDelta, ...]
        Suppressions applied after the engine.
    recorded : tuple[str, ...]
        Difference ids that are noted and not yet suppressions.
    inherits : str or None
        Optional parent profile id (single-parent DAG).
    stations : frozenset[str]
        ICAO list for station-scoped resolve (not inherited).
    station_prefixes : frozenset[str]
        ICAO prefixes for station-scoped resolve (not inherited). Exact
        ``stations`` entries win over any prefix match.
    accept_end_tx_tn : bool
        When True, TX/TN after change groups is informational.
    """

    profile_id: str
    engine: str
    products: frozenset[str]
    differs: bool
    deltas: tuple[LintDelta, ...]
    recorded: tuple[str, ...]
    inherits: str | None = None
    stations: frozenset[str] = frozenset()
    station_prefixes: frozenset[str] = frozenset()
    accept_end_tx_tn: bool = False


__all__ = [
    "MAX_INHERIT_DEPTH",
    "_CATALOG_PATH",
    "_TOKEN_RE",
    "Issue",
    "LintDelta",
    "LintProfileSpec",
    "LintReport",
    "Path",
    "annotations",
    "cache",
    "canonical_lint_profile_id",
    "cast",
    "dataclass",
]
