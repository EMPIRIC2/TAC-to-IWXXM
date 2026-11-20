"""Package split of former ``exchange_output.py`` (stable import path)."""

from __future__ import annotations

from importlib import import_module as _import_module
from pathlib import Path as _Path

__all__ = [
    "CA_DISTRIBUTION_PATH_TEMPLATE",
    "CA_ECCC_IWXXM_VERSION",
    "CA_MSC_FILENAME_PATTERN",
    "ProfileOutputSpec",
    "build_ca_eccc_output_spec",
    "build_ca_eccc_output_spec_from_msc_filename",
    "ca_distribution_path",
    "ca_msc_filename",
    "ca_wmo_header_designator",
    "default_ca_translation_centre",
    "format_ca_wmo_ahl",
    "issued_at_from_yygggg",
    "msc_filename_matches_pattern",
    "parse_msc_exchange_filename",
    "profile_output_spec_to_dict",
]

_shared = _import_module("tac2iwxxm.exchange_output._shared")
globals().update({k: v for k, v in _shared.__dict__.items() if not k.startswith("__")})

_parts_dir = _Path(__file__).resolve().parent
for _part in sorted(_parts_dir.glob("_part*.py")):
    _src = _part.read_text(encoding="utf-8")
    exec(compile(_src, str(_part), "exec"), globals())

del _import_module, _Path, _shared, _parts_dir, _part, _src
