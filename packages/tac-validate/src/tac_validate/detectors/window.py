"""Detector window prep and issue emit."""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

import importlib
import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Literal, cast

from metar_shared import tac_patterns as _tac_patterns
from tac_validate.detectors.catalog_load import *
from tac_validate.detectors.models import *
from tac_validate.detectors.parse_rules import *
from tac_validate.issue_registry import issue_from
from tac_validate.match_port import match_port_spans
from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import _strip_research_refs
from tac_validate.theme_checks import lint_profile

_AHL_HEADING_LINE = _tac_patterns.AHL_HEADING_LINE_BBB3


def _prepare_window(body: str, prep: PreprocessSpec) -> tuple[str, int]:
    """
    Internal helper ``_prepare_window``.

    Parameters
    ----------
    body : object
        Argument ``body``.
    prep : object
        Argument ``prep``.

    Returns
    -------
    object
        Return value.
    """
    text = body
    offset = 0
    if prep.strip_terminator and text.endswith("="):
        text = text[:-1]
    if prep.after:
        at = text.find(prep.after)
        if at >= 0:
            cut = at + len(prep.after)
            text = text[cut:]
            offset = cut
    if prep.before:
        at = text.find(prep.before)
        if at >= 0:
            text = text[:at]
    if prep.exclude_ahl_lines:
        kept = [
            line
            for line in text.splitlines(keepends=True)
            if not _AHL_HEADING_LINE.match(line.strip("\n").strip("\r").strip())
        ]
        text = "".join(kept)
        # Keep offset 0 so spans match legacy metar_speci visibility (stripped window
        # treated as starting at body start) — only when after was not applied.
        if not prep.after:
            offset = 0
    return text, offset


def _resolve_python(ref: str) -> PythonDetector:
    """
    Internal helper ``_resolve_python``.

    Parameters
    ----------
    ref : object
        Argument ``ref``.

    Returns
    -------
    object
        Return value.
    """
    if not ref.startswith("python:"):
        msg = f"python ref must start with python:: {ref!r}"
        raise DetectorError(msg)
    rest = ref[len("python:") :]
    if ":" not in rest:
        msg = f"python ref must be python:module:attr: {ref!r}"
        raise DetectorError(msg)
    module_name, _, attr = rest.rpartition(":")
    if not module_name or not attr:
        msg = f"python ref must be python:module:attr: {ref!r}"
        raise DetectorError(msg)
    module = importlib.import_module(module_name)
    fn = getattr(module, attr, None)
    if not callable(fn):
        msg = f"python detector not callable: {ref!r}"
        raise DetectorError(msg)
    return cast(PythonDetector, fn)


def _emit_issue(
    emit: EmitSpec,
    *,
    product: str,
    body_start: int,
    body_end: int,
    window_offset: int,
    match: re.Match[str] | None,
) -> Issue:
    """
    Internal helper ``_emit_issue``.

    Parameters
    ----------
    emit : object
        Argument ``emit``.
    product : object
        Argument ``product``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    window_offset : object
        Argument ``window_offset``.
    match : object
        Argument ``match``.

    Returns
    -------
    object
        Return value.
    """
    capture = ""
    start = body_start
    end = body_end
    if emit.span == "match" and match is not None:
        group = emit.capture_group
        try:
            capture = match.group(group)
            start = body_start + window_offset + match.start(group)
            end = body_start + window_offset + match.end(group)
        except IndexError:
            capture = match.group(0)
            start = body_start + window_offset + match.start(0)
            end = body_start + window_offset + match.end(0)
    message = _strip_research_refs(emit.message_template.format(product=product, capture=capture))
    return issue_from(
        emit.code,
        message=message,
        start=start,
        end=end,
        location=emit.location,
    )


__all__ = [
    "_AHL_HEADING_LINE",
    "Any",
    "Callable",
    "Issue",
    "Literal",
    "Mapping",
    "Sequence",
    "_emit_issue",
    "_prepare_window",
    "_resolve_python",
    "_strip_research_refs",
    "issue_from",
    "lint_profile",
    "match_port_spans",
]
