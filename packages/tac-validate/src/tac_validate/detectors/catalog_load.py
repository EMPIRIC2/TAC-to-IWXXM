"""Detector catalog loading and mode helpers."""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence
from importlib import resources
from pathlib import Path
from typing import Any, Literal

import yaml

from metar_shared import tac_patterns as _tac_patterns
from tac_validate.detectors.models import *
from tac_validate.detectors.parse_rules import *
from tac_validate.issue_registry import issue_from
from tac_validate.match_port import match_port_spans
from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import _strip_research_refs
from tac_validate.theme_checks import lint_profile

_AHL_HEADING_LINE = _tac_patterns.AHL_HEADING_LINE_BBB3


def load_detector_catalog(profile: str | None = None) -> dict[str, DetectorPack]:
    """
    Load builtin detector packs plus optional ``TAC_VALIDATE_DETECTOR_DIR``.

    An overlay with ``extends`` layers rules onto that builtin for the profile
    ids in its header. Omitting ``profile`` leaves those layers off. A new pack
    id with no ``extends`` is added for every profile.


    Parameters
    ----------
    profile : str or None, optional
        Profile id. By default ``None``.

    Returns
    -------
    dict[str, DetectorPack]
        Load builtin detector packs plus optional ``TAC_VALIDATE_DETECTOR_DIR``.
    """
    catalog: dict[str, DetectorPack] = {}
    root = resources.files("tac_validate").joinpath("data", "detectors")
    for entry in root.iterdir():
        name = entry.name
        if name.endswith((".yaml", ".yml")):
            text = entry.read_text(encoding="utf-8")
            pack = _parse_pack(yaml.safe_load(text), source_path=f"builtin:{name}")
            catalog[pack.id] = pack
    overlay = os.environ.get(ENV_DETECTOR_DIR, "").strip()
    if overlay:
        overlay_path = Path(overlay)
        if overlay_path.is_dir():
            for path in sorted(overlay_path.glob("*.yaml")) + sorted(overlay_path.glob("*.yml")):
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                pack = _parse_pack(raw, source_path=str(path))
                layered = _take_detector_overlay(raw, pack, catalog, profile=profile)
                if layered is None:
                    continue
                catalog[layered.id] = layered
    return catalog


def detector_mode() -> Literal["legacy", "shadow", "detector"]:
    """
    Return effective detector mode (default ``detector`` after R2 flip).


    Returns
    -------
    Literal['legacy', 'shadow', 'detector']
        Effective detector mode (default ``detector`` after R2 flip).
    """
    raw = os.environ.get(ENV_DETECTOR_MODE, "detector").strip().lower()
    if raw == "legacy":
        return "legacy"
    if raw == "shadow":
        return "shadow"
    return "detector"


def _body_span(tac: str) -> tuple[int, int, str]:
    """
    Internal helper ``_body_span``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.

    Returns
    -------
    object
        Return value.
    """
    stripped = tac.strip()
    if not stripped:
        return 0, len(tac), ""
    leading = len(tac) - len(tac.lstrip())
    return leading, leading + len(stripped), stripped


__all__ = [
    "_AHL_HEADING_LINE",
    "Any",
    "Callable",
    "Issue",
    "Literal",
    "Mapping",
    "Sequence",
    "_body_span",
    "_strip_research_refs",
    "detector_mode",
    "issue_from",
    "lint_profile",
    "load_detector_catalog",
    "match_port_spans",
]
