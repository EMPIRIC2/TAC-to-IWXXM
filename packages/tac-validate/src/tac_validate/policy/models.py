"""TAC quality policy load + resolve.

Draft lifecycle warns on unknown registry codes; activate fails closed.
"""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Literal, cast

from tac_validate.issue_registry import ISSUES, by_code, catalog_entries
from tac_validate.models import Issue, LintReport

PolicyLifecycle = Literal["draft", "activated"]

MAX_EXTENDS_DEPTH = 5
ENV_POLICY_DIR = "TAC_VALIDATE_POLICY_DIR"

_SEVERITIES = frozenset({"error", "warning", "info"})


class PolicyError(ValueError):
    """
    Base error for TAC quality policy documents.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


class PolicyActivationError(PolicyError):
    """
    Activated policy references unknown codes or invalid severity remaps.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


class PolicyCycleError(PolicyError):
    """
    ``extends`` graph contains a cycle.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


class PolicyDepthError(PolicyError):
    """
    ``extends`` chain exceeds ``MAX_EXTENDS_DEPTH``.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


@dataclass(frozen=True, slots=True)
class PolicyDocument:
    """
    One TAC quality policy YAML document.

    Attributes
    ----------
    schema_version : int
        Positive integer document schema version.
    id : str
        Policy id.
    lifecycle : PolicyLifecycle
        ``draft`` or ``activated``.
    product : str or None
        Product id, when the policy names one.
    extends : tuple[str, ...]
        Parent policy ids.
    select : tuple[str, ...]
        Issue codes to keep. A non-empty child list replaces the parent list.
    ignore : tuple[str, ...]
        Issue codes to drop. Child lists are appended to the parent.
    profiles : tuple[str, ...]
        Profile ids this document applies to.
    severity : Mapping[str, str]
        Issue code to severity (``error``, ``warning``, or ``info``).
    preview : tuple[str, ...]
        Preview issue codes. Child lists are combined with the parent.
    detectors : tuple[str, ...]
        Detector pack ids. A non-empty child list replaces the parent list.
    source_path : str or None, optional
        Path the document was loaded from. By default ``None``.
    """

    schema_version: int
    id: str
    lifecycle: PolicyLifecycle
    product: str | None
    extends: tuple[str, ...]
    select: tuple[str, ...]
    ignore: tuple[str, ...]
    profiles: tuple[str, ...]
    severity: Mapping[str, str]
    preview: tuple[str, ...]
    detectors: tuple[str, ...]
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class ResolvedPolicy:
    """
    Merged policy ready for lint runtime consumption.

    Attributes
    ----------
    id : str
        Policy id.
    lifecycle : PolicyLifecycle
        ``draft`` or ``activated``.
    product : str or None
        Product id after walking the extend chain.
    enabled_codes : frozenset[str]
        Issue codes still enabled after select, preview, and ignore.
    severity_overrides : Mapping[str, str]
        Issue-code severity overrides from the chain.
    preview_codes : frozenset[str]
        Preview issue codes collected from the chain.
    detector_ids : tuple[str, ...]
        Detector pack ids from the nearest document that sets them.
    warnings : tuple[str, ...]
        Messages from code-reference checks.
    can_activate : bool
        True when ``warnings`` does not mention an unknown registry code.
    chain : tuple[str, ...]
        Policy ids from the root parent through this document.
    """

    id: str
    lifecycle: PolicyLifecycle
    product: str | None
    enabled_codes: frozenset[str]
    severity_overrides: Mapping[str, str]
    preview_codes: frozenset[str]
    detector_ids: tuple[str, ...]
    warnings: tuple[str, ...]
    can_activate: bool
    chain: tuple[str, ...]


__all__ = [
    "ENV_POLICY_DIR",
    "ISSUES",
    "MAX_EXTENDS_DEPTH",
    "_SEVERITIES",
    "Any",
    "Issue",
    "LintReport",
    "Literal",
    "Mapping",
    "Path",
    "PolicyActivationError",
    "PolicyCycleError",
    "PolicyDepthError",
    "PolicyDocument",
    "PolicyError",
    "PolicyLifecycle",
    "ResolvedPolicy",
    "annotations",
    "by_code",
    "cast",
    "catalog_entries",
    "dataclass",
    "resources",
]
