"""detectors package split."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.detectors.catalog_load import (
    _body_span,
    detector_mode,
    load_detector_catalog,
)
from tac_validate.detectors.models import (
    DEFAULT_LINT_BUDGET,
    ENV_DETECTOR_DIR,
    ENV_DETECTOR_MODE,
    DetectorError,
    DetectorKind,
    DetectorPack,
    DetectorRule,
    DetectorStage,
    EmitSpec,
    PreprocessSpec,
    PythonDetector,
    ShadowCompareResult,
)
from tac_validate.detectors.parse_rules import (
    _AHL_HEADING_LINE,
    _header_extends,
    _header_profiles,
    _merge_detector_rules,
    _parse_emit,
    _parse_pack,
    _parse_preprocess,
    _parse_rule,
    _re_flags,
    _take_detector_overlay,
    load_detector_pack,
)
from tac_validate.detectors.run import (
    _ANNEX3_METAR_THEME_PACKS,
    compare_shadow,
    example_python_hatch,
    example_python_hatch_emit,
    issue_keys,
    run_detector_pack,
    run_r2_visibility_detectors,
    run_theme_pack,
)
from tac_validate.detectors.window import (
    _emit_issue,
    _prepare_window,
    _resolve_python,
)
from tac_validate.issue_registry import issue_from
from tac_validate.match_port import match_port_spans
from tac_validate.product_rules_pkg._common import _strip_research_refs
from tac_validate.theme_checks import lint_profile

__all__ = [
    "DEFAULT_LINT_BUDGET",
    "ENV_DETECTOR_DIR",
    "ENV_DETECTOR_MODE",
    "_AHL_HEADING_LINE",
    "_ANNEX3_METAR_THEME_PACKS",
    "DetectorError",
    "DetectorKind",
    "DetectorPack",
    "DetectorRule",
    "DetectorStage",
    "EmitSpec",
    "PreprocessSpec",
    "PythonDetector",
    "ShadowCompareResult",
    "_body_span",
    "_emit_issue",
    "_header_extends",
    "_header_profiles",
    "_merge_detector_rules",
    "_parse_emit",
    "_parse_pack",
    "_parse_preprocess",
    "_parse_rule",
    "_prepare_window",
    "_re_flags",
    "_resolve_python",
    "_strip_research_refs",
    "_take_detector_overlay",
    "compare_shadow",
    "detector_mode",
    "example_python_hatch",
    "example_python_hatch_emit",
    "issue_from",
    "issue_keys",
    "lint_profile",
    "load_detector_catalog",
    "load_detector_pack",
    "match_port_spans",
    "run_detector_pack",
    "run_r2_visibility_detectors",
    "run_theme_pack",
]
