"""Detector DSL models."""

# pyright: reportPrivateUsage=false
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from tac_validate.models import Issue

DetectorStage = Literal["parse_gate", "token", "cross_field"]
DetectorKind = Literal["finditer", "require_search", "python", "token_scan"]

ENV_DETECTOR_DIR = "TAC_VALIDATE_DETECTOR_DIR"
ENV_DETECTOR_MODE = "TAC_VALIDATE_DETECTOR_MODE"  # legacy | shadow | detector
DEFAULT_LINT_BUDGET = 10_000

PythonDetector = Callable[[str, str], list[Issue]]

_TOKEN_RE = re.compile(r"\S+")


class DetectorError(ValueError):
    """
    Invalid detector pack or rule.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


@dataclass(frozen=True, slots=True)
class PreprocessSpec:
    """
    Text windowing before a rule runs.

    Attributes
    ----------
    before : str or None, optional
        When this marker is found, keep only the text before it. By default ``None``.
    after : str or None, optional
        When this marker is found, keep only the text after it. By default ``None``.
    exclude_ahl_lines : bool, optional
        Drop lines that match an AHL heading. By default ``False``.
    strip_terminator : bool, optional
        Drop a trailing ``=``. By default ``True``.
    """

    before: str | None = None
    after: str | None = None
    exclude_ahl_lines: bool = False
    strip_terminator: bool = True


@dataclass(frozen=True, slots=True)
class EmitSpec:
    """
    Issue emission on match or fail.

    Attributes
    ----------
    code : str
        Code.
    location : str or None
        Location.
    message_template : str
        Message template.
    capture_group : int, optional
        Capture group. By default ``0``.
    span : Literal['match', 'body'], optional
        Span. By default ``'match'``.
    """

    code: str
    location: str | None
    message_template: str
    capture_group: int = 0
    span: Literal["match", "body"] = "match"


@dataclass(frozen=True, slots=True)
class DetectorRule:
    """
    One detector rule inside a pack.

    Attributes
    ----------
    id : str
        ID.
    kind : DetectorKind
        ``finditer``, ``require_search``, ``python``, or ``token_scan``.
    preprocess : PreprocessSpec
        Preprocess.
    pattern : str or None
        Pattern.
    flags : int
        Flags.
    skip_if_codes : tuple[str, ...]
        Skip if codes.
    on_match : EmitSpec or None
        On match.
    on_fail : EmitSpec or None
        On fail.
    python_ref : str or None
        Python ref.
    skip_if_match : str or None, optional
        Skip if match. By default ``None``.
    select_pattern : str or None, optional
        Select pattern. By default ``None``.
    ok_pattern : str or None, optional
        OK pattern. By default ``None``.
    on_ok : EmitSpec or None, optional
        On OK. By default ``None``.
    max_emits : int or None, optional
        Max emits. By default ``None``.
    """

    id: str
    kind: DetectorKind
    preprocess: PreprocessSpec
    pattern: str | None
    flags: int
    skip_if_codes: tuple[str, ...]
    on_match: EmitSpec | None
    on_fail: EmitSpec | None
    python_ref: str | None
    skip_if_match: str | None = None
    select_pattern: str | None = None
    ok_pattern: str | None = None
    on_ok: EmitSpec | None = None
    max_emits: int | None = None


@dataclass(frozen=True, slots=True)
class DetectorPack:
    """
    Loaded detector pack document.

    Attributes
    ----------
    id : str
        ID.
    stage : DetectorStage
        Stage.
    products : frozenset[str]
        Products.
    rules : tuple[DetectorRule, ...]
        Rules.
    source_path : str or None, optional
        Source path. By default ``None``.
    """

    id: str
    stage: DetectorStage
    products: frozenset[str]
    rules: tuple[DetectorRule, ...]
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class ShadowCompareResult:
    """
    Legacy vs detector issue sets for one code family.

    Attributes
    ----------
    matched : bool
        Matched.
    legacy_keys : frozenset[tuple[str, int or None, int or None]]
        Legacy keys.
    detector_keys : frozenset[tuple[str, int or None, int or None]]
        Detector keys.
    """

    matched: bool
    legacy_keys: frozenset[tuple[str, int | None, int | None]]
    detector_keys: frozenset[tuple[str, int | None, int | None]]


__all__ = [
    "DEFAULT_LINT_BUDGET",
    "ENV_DETECTOR_DIR",
    "ENV_DETECTOR_MODE",
    "_TOKEN_RE",
    "DetectorError",
    "DetectorKind",
    "DetectorPack",
    "DetectorRule",
    "DetectorStage",
    "EmitSpec",
    "PreprocessSpec",
    "PythonDetector",
    "ShadowCompareResult",
]
