"""Facade for ``conversion.py`` (line-cap split)."""

import sys
import types

from tac2iwxxm.profile_registry import supported_report_variants_for_profile

from src.schemas.conversion import FailedSpan

from . import conversion_part_1 as _part1
from . import conversion_part_2 as _part2
from . import conversion_part_6 as _part6
from . import conversion_routes_io as _routes_io
from .conversion_api_surface import api_surface
from .conversion_part_1 import (
    _convert_output_policy_id,
    _ConvertRuntime,
    _form_text,
    _infer_report_variant_from_sample,
    _initial_layers_passed,
    _output_validation_orch_layers,
    _pre_convert_tac_layers,
    _resolve_effective_iwxxm_version,
    _resolve_report_variant,
    _run_pre_convert_validation,
    _wire_payload_dict,
    logger,
    router,
    tac_lint_fn,
)
from .conversion_part_2 import (
    _append_pre_convert_lint_issues,
    _ConvertAccumulator,
    _record_convert_station_health,
)
from .conversion_part_3 import _process_json_metars
from .conversion_part_4 import _process_manual_entries
from .conversion_part_5 import _process_uploaded_files
from .conversion_part_6 import ConversionProfilesService, convert_bulletin
from .conversion_routes_io import convert
from .conversion_routes_zip import convert_zip

_SYNC = {
    "ConversionProfilesService",
    "FailedSpan",
    "api_surface",
    "supported_report_variants_for_profile",
    "tac_lint_fn",
}


_ORIG: dict[str, object] = {}
for _n in _SYNC:
    for _mod in (
        _part1,
        _part2,
        _part6,
        _routes_io,
    ):
        if hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


class _ConversionRouterModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name in _SYNC:
            for mod in (_part1, _part2, _part6, _routes_io):
                if hasattr(mod, name):
                    setattr(mod, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if name in _ORIG and hasattr(_part1, name):
            setattr(_part1, name, _ORIG[name])
        if name in _ORIG and hasattr(_part2, name):
            setattr(_part2, name, _ORIG[name])
        if name in _ORIG and hasattr(_part6, name):
            setattr(_part6, name, _ORIG[name])
        if name in _ORIG and hasattr(_routes_io, name):
            setattr(_routes_io, name, _ORIG[name])
        super().__delattr__(name)


sys.modules[__name__].__class__ = _ConversionRouterModule

__all__ = [
    "ConversionProfilesService",
    "FailedSpan",
    "_ConvertAccumulator",
    "_ConvertRuntime",
    "_append_pre_convert_lint_issues",
    "_convert_output_policy_id",
    "_form_text",
    "_infer_report_variant_from_sample",
    "_initial_layers_passed",
    "_output_validation_orch_layers",
    "_pre_convert_tac_layers",
    "_process_json_metars",
    "_process_manual_entries",
    "_process_uploaded_files",
    "_record_convert_station_health",
    "_resolve_effective_iwxxm_version",
    "_resolve_report_variant",
    "_run_pre_convert_validation",
    "_wire_payload_dict",
    "api_surface",
    "convert",
    "convert_bulletin",
    "convert_zip",
    "logger",
    "router",
    "supported_report_variants_for_profile",
    "tac_lint_fn",
]
